from datetime import datetime, timedelta, timezone
import time
from Configurations import getMarketConfigurations
from Core.Client.Client import Client, TimeFrame
from Core.Client.MT5Client import MT5Client
from Core.Strategy import Strategy
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Type, Union
import pandas as pd
from Utils.StrategyUtils import StrategyUtils
from Utils.Utils import convertDateTimeZone, currentDate

DEBUG = True
class LiveTrader:

    def __init__(self, client: Type[Client], strategy: Type[Strategy], accountParams = None, strategyParams = None, mt5 = None):

        if not (isinstance(client, type) and issubclass(client, Client)):
            raise TypeError('`client` must be a Client sub-type')
        
        if not (isinstance(strategy, type) and issubclass(strategy, Strategy)):
            raise TypeError('`strategy` must be a Strategy sub-type')

        self._client = client
        self._strategy = strategy
        self._accountParams = accountParams
        self._strategyParams = strategyParams
        self._markerParams = getMarketConfigurations()
        self.mt5 = mt5
    
    # def getNewData(self, client:Client):
    #     fromdate = client.data['Date'][-1]
    #     date = currentDate()
    #     newdata = client.getData(fromDate= fromdate, toDate=date)
    #     result = pd.concat([client.data,newdata])
    #     result = result[~result.index.duplicated(keep='first')]
    #     print(result['Date'][-1])

    #     client.data = result
        
    def run(self):
        print('====> LiveTrader Running <====')

        client: Client = self._client(strategyName=self._strategy.__name__, params=self._accountParams)
        strategy : Strategy = self._strategy(client=client, params=self._strategyParams)
        
        client.init(mt5=self.mt5)
        strategy.init()
        
        marketClosed= False
        
        while True:                        
            date = currentDate()
            utils = StrategyUtils(config=self._markerParams,marketDatetime=date)
            strategy.utils = utils
            strategy.date = date

            if DEBUG:
                print('current date =>', date.strftime("%Y-%m-%d %H:%M:%S %Z %z") + "\n" + "account => " + self._accountParams.description + "\n")
            if utils.isBusinessDay():
                if marketClosed:
                    strategy.init()
                    marketClosed = False
                client.getData(fromDate= date - timedelta(days=5), toDate=date)
                strategy.data = client.data
                strategy.run()
            
            else:
                marketClosed = True
                if DEBUG:
                    print("-------------------------\n The market is closed \n-------------------------")
        
            sleeptime = 60 - (date.second + date.microsecond/1000000.0)
            time.sleep(sleeptime)