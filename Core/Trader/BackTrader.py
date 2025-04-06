from datetime import datetime, timedelta, timezone
from decimal import Decimal
import itertools
from Configurations import getMarketConfigurations
from Core.Client.BackClient.BackClient import BackClient
from Core.Client.Client import Client, TimeFrame
from Core.Client.MT5Client import MT5Client
from Core.Strategy import Strategy
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Type, Union

from Utils.StrategyUtils import StrategyUtils
from Utils.Utils import convertDateTimeZone, getNDXData, percentBar

import pandas as pd

DEBUG = False
class BackTrader:

    def __init__(self, strategy: Type[Strategy], accountParams = None, strategyParams = None, fromDate:str =None, toDate:str =None, LocalData:bool= None, PathData:str= None):


        if not (isinstance(strategy, type) and issubclass(strategy, Strategy)):
            raise TypeError('`strategy` must be a Strategy sub-type')

        self._strategy = strategy
        self._accountParams = accountParams
        self._strategyParams = strategyParams
        self._markerParams = getMarketConfigurations()
        self.Data = None
        self.fromDate = fromDate
        self.toDate = toDate
        self.LocalData= LocalData
        self.PathData= PathData
        
    def get_data_itt(self, index):
        return (self.data.iloc[:index]
            if index < len(self.data)
            else self.data)
        
    def run(self):
        print('====> BackTrader Running <====')
      
        client: BackClient = BackClient(strategyName=self._strategy.__name__, params=self._accountParams)
        strategy : Strategy = self._strategy(client=client, params=self._strategyParams)
        
        client.init()
        strategy.init()
        
        date_format = "%Y-%m-%d"

    
        fromdt = datetime.strptime(self.fromDate, date_format)
        todt = datetime.strptime(self.toDate, date_format)
        delta = todt - fromdt

          #mt5
        
        if self.LocalData:
              #file
            self.data = getNDXData(self.PathData)
            self.data.sort_index()
            self.data = self.data.loc[fromdt:todt]

        else:
            self.data = client.getData(fromDate=fromdt,toDate=todt, timeframe=TimeFrame[self._strategyParams.timeFrame].value)


      

      

        marketClosed = False
        
        for i in range(1, len(self.data)):
            data_itt = self.get_data_itt(i)
            bar = data_itt.iloc[-1]
            bdate = bar['Date']

            client.date = bdate
            client.data = data_itt
            client.next()
            
            utils = StrategyUtils(config=self._markerParams,marketDatetime=bdate)
        
            if utils.isBusinessDay():
                if marketClosed:
                    strategy.init()
                    marketClosed = False
                
                strategy.utils = utils
                strategy.date = bdate
                strategy.data = data_itt
                strategy.run()
                barstep = todt - bdate
                barstep = delta.days - barstep.days
                percentBar(step=barstep, total_steps=delta.days)
            
            else:
                marketClosed = True
                if DEBUG:
                    print("-------------------------\n The market is closed \n-------------------------")
        
        self.result(client=client)  
            
    def result(self, client:BackClient):
        print("====> BackTrader Result <====")
        win = list(filter(lambda x: x.isWin, client.positions))
        loss = list(filter(lambda x: x.isLoss, client.positions))
        all = list(filter(lambda x: x.isLoss or x.isWin, client.positions))
        currentBalance: Decimal= Decimal(client._params.startBalance)
        profit: Decimal= 0

        print("====Month Result====")

        for x in range(12):
            m = x +1
            pos = list(filter(lambda x: x.filledDate.month == m, client.positions))
            win = list(filter(lambda x: x.isWin, pos))
            loss = list(filter(lambda x: x.isLoss, pos))

            print(f"------ Month - {m} ------")

            for position in pos:
                if currentBalance + position.pnl >= (Decimal(client._params.startBalance) * Decimal(client._params.resetAccountPercent)):
                        currentBalance+=position.pnl
                        profit+=(currentBalance-Decimal(client._params.startBalance))
                        print(f'Posicion open at {position.filledDate}, closed at {position.closedDate} price {position.price}, TP: {position.tp}, SL: {position.sl} P/L: {"${:,.2f}".format(currentBalance)}, Ganancia={"${:,.2f}".format(Decimal(position.pnl))}')
                        print(f"-----------------Balance reset by profit: *** {'${:,.2f}'.format(profit)}***-----------------")
                        currentBalance= Decimal(client._params.startBalance)
                else:
                    currentBalance+=position.pnl
                    print(f'Posicion open at {position.filledDate}, closed at {position.closedDate} price {position.price}, TP: {position.tp}, SL: {position.sl} P/L: {"${:,.2f}".format(currentBalance)}, Ganancia={"${:,.2f}".format(Decimal(position.pnl))}')