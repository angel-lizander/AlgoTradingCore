from datetime import datetime, timezone
from Configurations import getAccountsConfigurations, getStrategyConfigurations
import pandas as pd
from dateutil import tz
import string
import random
from decimal import *

def mt5ParseData(data):
    data.rename(columns = {'open':'Open', 'high':'High', 'low': 'Low', 'close': 'Close', 'time': 'Date', 'tick_volume':'TickVolume', 'spread':'Spread'}, inplace = True)
    data['Date'] = pd.to_datetime(data['Date'], unit='s').dt.tz_localize(None)
    data = data.set_index('Date', drop=False)
    return data

def getParams(accountName, strategyName):

    accounts = getAccountsConfigurations()
    account = next(filter(lambda x: x.keyName == accountName, accounts), None)

    strategy = getStrategyConfigurations()
    strategy = getattr(strategy, strategyName)
    stgAccountConfig = next(filter(lambda x: x.keyName == accountName, strategy.accounts),None)

    setattr(account,"volume", stgAccountConfig.volume)
    setattr(account,"deviation", stgAccountConfig.deviation)
    setattr(account,"symbol", stgAccountConfig.symbol)
    delattr(strategy, "accounts")

    return account, strategy

def getAccountsByStrategy(strategyName):
    strategyConfig = getStrategyConfigurations()
    strategy = getattr(strategyConfig, strategyName)
    return list(map(lambda x :  x.keyName, strategy.accounts))


def convertDateTimeZone(date, toZone):
    toTz = tz.gettz(toZone)
    localTz = datetime.now(timezone.utc).astimezone().tzname()
    localTz = tz.gettz(localTz)
    d = date.replace(tzinfo=localTz)
    d = d.astimezone(toTz)
    return d.replace(tzinfo=None)

def generateId():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))

def getNDXData(file):
    data=pd.read_csv(file, sep=';', header=None, names=["Date","Open", "High", "Low", "Close", "Volume"])
    data['Date'] = pd.to_datetime(data['Date'],  format='%Y%m%d %H%M%S').dt.tz_localize('US/Eastern')
    data['Date'] =  data['Date'].dt.tz_convert('Europe/London')
    data['Date'] =  data['Date'].dt.tz_localize(None)

    data = data.set_index('Date', drop=False)
    

    return data

def currentDate():
    return convertDateTimeZone(date=datetime.today(), toZone='GMT+2')

def orderVolume(balance, risk, slPrice, slPorcent, leverage, riskEmergency, riskEmergencyPercent):
    volume= (float(balance) * float(risk)) / (slPorcent * slPrice )

    if riskEmergency:
        volume= volume/riskEmergencyPercent
    return round(volume/(float(leverage)),2)

def pip_calc(open, close):

    pips = abs(close - open)
    return pips

def first_n_digits(num, n):
    num = abs(num)
    num_str = str(num)

    if n >= len(num_str):
        return num

    return int(num_str[:n])

def percentBar(step, total_steps, bar_width=60, title="", print_perc=True):
    import sys

    # UTF-8 left blocks: 1, 1/8, 1/4, 3/8, 1/2, 5/8, 3/4, 7/8
    utf_8s = ["█", "▏", "▎", "▍", "▌", "▋", "▊", "█"]
    perc = 100 * float(step) / float(total_steps)
    max_ticks = bar_width * 8
    num_ticks = int(round(perc / 100 * max_ticks))
    full_ticks = num_ticks / 8      # Number of full blocks
    part_ticks = num_ticks % 8      # Size of partial block (array index)
    
    disp = bar = ""                 # Blank out variables
    bar += utf_8s[0] * int(full_ticks)  # Add full blocks into Progress Bar
    
    # If part_ticks is zero, then no partial block, else append part char
    if part_ticks > 0:
        bar += utf_8s[part_ticks]
    
    # Pad Progress Bar with fill character
    bar += "▒" * int((max_ticks/8 - float(num_ticks)/8.0))
    
    if len(title) > 0:
        disp = title + ": "         # Optional title to progress display
    
    # Print progress bar in green: https://stackoverflow.com/a/21786287/6929343
    disp += "\x1b[0;32m"            # Color Green
    disp += bar                     # Progress bar to progress display
    disp += "\x1b[0m"               # Color Reset
    if print_perc:
        # If requested, append percentage complete to progress display
        if perc > 100.0:
            perc = 100.0            # Fix "100.04 %" rounding error
        disp += " {:6.2f}".format(perc) + " %"
    
    # Output to terminal repetitively over the same line using '\r'.
    sys.stdout.write("\r" + disp)
    sys.stdout.flush()