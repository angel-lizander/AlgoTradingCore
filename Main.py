from datetime import datetime
import importlib
import sys
import threading
from Core.Client.MT5Client import MT5Client
from Core.Trader.BackTrader import BackTrader 
from Core.Trader.LiveTrader import LiveTrader
from Utils.Utils import convertDateTimeZone, currentDate, getParams, getAccountsByStrategy
import logging

import Libs.meta1 as mt1
import Libs.meta2 as mt2
import Libs.meta3 as mt3
import Libs.meta4 as mt4
import Libs.meta5 as mt5
import Libs.meta6 as mt6

#logging Config
logging.basicConfig(filename="log.txt", level=logging.DEBUG)

def lazy_import(name, id):
    
    SPEC = importlib.util.find_spec(name)
    md = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(md)
    sys.modules[name+str(id)] = md
    del SPEC
    return md

def getMt5Pk(id):
    if id ==1:
        return mt1
    if id ==2:
        return mt2
    if id ==3:
        return mt3
    if id ==4:
        return mt4
    if id ==5:
        return mt5
    if id ==6:
        return mt6

def strategyCaller(client, strategy, accountParams, strategyParams, id):
    #Init LiveTrader with LondonOnePercentStrategy
    #mt5 = lazy_import("MetaTrader5", id)
    mt5 = getMt5Pk(id)

    trader = LiveTrader(client=client, strategy=strategy, accountParams=accountParams, strategyParams=strategyParams, mt5 = mt5)
    trader.run()
    

def run():
    accountsByStrategy= getAccountsByStrategy(strategyName="TestStrategy")
    idx = 1
    for account in accountsByStrategy:
        #Get config Params
        account, strategy = getParams(accountName=account,strategyName="TestStrategy")

        thread = threading.Thread(target=strategyCaller, args=(MT5Client, TestStrategy, account, strategy, idx))  
        thread.start()
        idx = idx +1

run()