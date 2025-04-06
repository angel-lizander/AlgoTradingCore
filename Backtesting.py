from datetime import datetime
import importlib
import sys
import threading
from Core.Client.MT5Client import MT5Client
from Core.Trader.BackTrader import BackTrader 
from Core.Trader.LiveTrader import LiveTrader
from Utils.Utils import convertDateTimeZone, currentDate, getParams, getAccountsByStrategy
import logging


#logging Config
logging.basicConfig(filename="log.txt", level=logging.DEBUG)

account, strategy = getParams(accountName="",strategyName="")


#Init BackTrader with Test
localData: bool=True
pathData= r"Data\DAT_ASCII_NSXUSD_M1_2020.csv";
trader = BackTrader(strategy=Test, accountParams=account, strategyParams=strategy, fromDate='2020-01-02', toDate='2020-12-30', LocalData=localData, PathData=pathData)
trader.run()

