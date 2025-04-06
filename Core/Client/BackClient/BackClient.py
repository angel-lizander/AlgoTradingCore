
from ast import List
import datetime
from decimal import *
from typing import Optional
from Core.Client.BackClient.Order import Order, OrderStatus
from Core.Client.BackClient.Position import Position, PositionStatus
from Core.Client.Client import Client, OrderType, TimeFrame
import MetaTrader5 as mt5
import pandas as pd
import numpy as np

from Utils.Utils import mt5ParseData, pip_calc
class BackClient(Client):
    
    """
    BackTrader Client
    """    
     
    def __init__(self, name: str =None, strategyName:str = None, params = None, date:datetime = None, balance:float = None, volume:float = None):
        super().__init__(name, strategyName, params)
        self.orders: List[Order] = []
        self.positions: List[Position] = []
        self.date = date
        self.volume: float = volume
        self.balance:Decimal= Decimal(self._params.startBalance)



    def init(self):
        self._name = "BackTrader Client"
        print('init ', self._name)
        login = self._login()

    
    def _login(self):
        account = self._params
        if not mt5.initialize(login=int(account.user),password=account.password, server=account.server):
            print("initialize() failed, error code =",mt5.last_error())
            return False   
        else:
            mt5.login(login=int(account.user),
                    password=account.password, server=account.server)
            return True

    def getOrders(self):
        return list(filter(lambda x: x.status == OrderStatus.ACTIVE, self.orders))

    def getTotalOrders(self):
        return len(self.getOrders())
    
    
    def cancelOrder(self, order):
        list(filter(lambda x: x.id == order.id, self.orders))[0].status = OrderStatus.CANCELLED
   
    
    def cancelAllOrders(self):
        orders = self.getOrders()
        for order in orders:
            order.status = OrderStatus.CANCELLED
    
    def getPositions(self):
        activePositions= list(filter(lambda x: x.status == PositionStatus.ACTIVE, self.positions))
        self.getPositionProfits(activePositions)
        return activePositions
    
    def getPositionProfits(self, positions):
        bar= self.data.iloc[-1]
        for position in positions:
            if position.type == OrderType.BUY_STOP or position.type == OrderType.BUY_LIMIT:
                position.price_current=bar['High']
            elif position.type == OrderType.SELL_STOP or  position.type == OrderType.SELL_LIMIT:
                position.price_current=bar['Low']
            position.profit= float(pip_calc(open=position.price , close=position.price_current)* float(self._params.symbol.contractSize)* position.volume)

    def getTotalPositions(self):
        return len(self.getPositions())
        
    
    def closePosition(self, position):
        bar = self.getBar()

        if position.type == OrderType.BUY_STOP or position.type == OrderType.BUY_LIMIT:
            position.closedDate = bar['Date']
            if position.price < bar['High']:
                position.isWin = True
                position.closedPrice = self.getClosedPrice(position=position,bar=bar)
            
            elif position.price > bar['Low']:
                position.isLoss = True
                position.closedPrice = self.getClosedPrice(position=position,bar=bar)

                    
        elif position.type == OrderType.SELL_STOP or  position.type == OrderType.SELL_LIMIT:
            position.closedDate = bar['Date']
            if position.price > bar['Low']:
                position.isWin = True
                position.closedPrice = self.getClosedPrice(position=position,bar=bar)

                
            elif position.price < bar['High']:
                position.isLoss = True
                position.closedPrice = self.getClosedPrice(position=position,bar=bar)

        position.pnl= self.checkBalance()
        position.status = PositionStatus.CLOSED
        
    def closeAllPositions(self):
        positions = self.getPositions()
        for position in positions:
            self.closePosition(position)
    
    def newOrder(self, price:float, type:OrderType, sl: Optional[float] = None, tp: Optional[float] = None, volume: Optional[float]= None):

        is_long = True if type == OrderType.BUY_LIMIT or type == OrderType.BUY_STOP else False
        
        bar = self.getBar()
        
        if type == OrderType.BUY_STOP and (bar['Close'] >= price):
            raise ValueError("BUY_STOP: the entry price cannot be less than the current price.")
        
        
        if type == OrderType.SELL_STOP and (bar['Close'] <= price):
            raise ValueError("SELL_STOP: the entry price cannot be higher than the current price.")
        
        
        if type == OrderType.BUY_LIMIT and not (bar['Close'] >= price):
            raise ValueError("BUY_LIMIT: the entry price cannot be higher than the current price.")
        
        
        if type == OrderType.SELL_LIMIT and not (bar['Close'] <= price):
            raise ValueError("SELL_LIMIT: the entry price cannot be less than the current price.")
            
        if is_long:
            if not (sl or -np.inf) < price < (tp or np.inf):
                raise ValueError(
                    "Long orders require: "
                    f"SL ({sl}) < LIMIT ({price}) < TP ({tp})")
        else:
            if not (tp or -np.inf) < price < (sl or np.inf):
                raise ValueError(
                    "Short orders require: "
                    f"TP ({tp}) < LIMIT ({price}) < SL ({sl})")

        order = Order(price=price, type= type, sl= sl, tp=tp, date=self.date, volume=volume)
       
        self.orders.append(order)
    

    def getData(self, fromDate:datetime =None, toDate:datetime = None, timeframe: TimeFrame = TimeFrame.M1):
        
        data = pd.DataFrame(mt5.copy_rates_range(self._params.symbol.name, timeframe, fromDate, toDate))
        data = mt5ParseData(data)
        self._data = data
        return data
    
    def getBar(self):
        return self.data.iloc[-1]
    
    def next(self):
        bar = self.getBar()
        if self.getTotalPositions() > 0:
            self.checkPositions(bar)
        if self.getTotalOrders() > 0:
            self.checkOrders(bar)
     
    
    def checkOrders(self, bar):
        fills = []
        for order in self.getOrders():
            if order.type == OrderType.BUY_STOP and (bar['High'] >= order.price):
                fills.append(order)
            
            elif order.type == OrderType.SELL_STOP and (bar['Low'] <= order.price):
                fills.append(order)
            
            elif order.type == OrderType.BUY_LIMIT and (bar['Low'] >= order.price):
                fills.append(order)
            
            elif order.type == OrderType.SELL_LIMIT and (bar['High'] >= order.price):
                fills.append(order)
       
        if len(fills) > 0:
            for order in fills:
                list(filter(lambda x: x.id == order.id, self.orders))[0].status = OrderStatus.FILLED
                self.positions.append(Position(price=order.price, type=order.type, sl=order.sl, tp=order.tp, filledDate=order.date, volume=order.volume))
    
    def getClosedPrice(self,position:Position, bar):
        
        if position.isBuy:
            if position.isWin:
                return position.tp if bar['High'] >= position.tp else bar['High']
            if position.isLoss:
                return position.sl if bar['Low'] <= position.sl else bar['Low']
        
        if position.isSell:
            if position.isWin:
                return position.tp if bar['Low'] <= position.tp else bar['Low']
            if position.isLoss:
                return position.sl if bar['High'] >= position.sl else bar['High']
          

    def checkPositions(self, bar):
        
        a = self.data.dtypes
        for position in self.getPositions():
            if position.type == OrderType.BUY_STOP or position.type == OrderType.BUY_LIMIT:
                if position.tp <= bar['High']:
                    position.isWin = True
                    position.closedDate = bar['Date']
                    position.closedPrice = self.getClosedPrice(position=position,bar=bar)
                    position.status = PositionStatus.CLOSED
                    position.pnl= self.checkBalance()

                
                elif position.sl >= bar['Low']:
                    position.isLoss = True
                    position.closedDate = bar['Date']
                    position.closedPrice = self.getClosedPrice(position=position,bar=bar)
                    position.status = PositionStatus.CLOSED
                    position.pnl= self.checkBalance()
      
            elif position.type == OrderType.SELL_STOP or  position.type == OrderType.SELL_LIMIT:
                if position.tp >= bar['Low']:
                    position.isWin = True
                    position.closedDate = bar['Date']
                    position.closedPrice = self.getClosedPrice(position=position,bar=bar)
                    position.status = PositionStatus.CLOSED
                    position.pnl= self.checkBalance()

                    
                elif position.sl <= bar['High']:
                    position.isLoss = True
                    position.closedDate = bar['Date']
                    position.closedPrice = self.getClosedPrice(position=position,bar=bar)
                    position.status = PositionStatus.CLOSED
                    position.pnl= self.checkBalance()
                    
    def getAccountInfo(self):
        return self._params
    
    def getBalance(self):
        return self.balance
    
    def getSymbolInfo(self):
        return self._params.symbol.contractSize

    def checkBalance(self):

        position= self.positions[-1]

        if position.type == OrderType.SELL_STOP or  position.type == OrderType.SELL_LIMIT:
            balance= Decimal(pip_calc(open=position.closedPrice , close=position.price)* float(self._params.symbol.contractSize)* position.volume)

        elif position.type == OrderType.BUY_STOP or position.type == OrderType.BUY_LIMIT:
            balance= Decimal(pip_calc(open=position.price , close=position.closedPrice)* float(self._params.symbol.contractSize)* position.volume)

        
        if (position.isLoss and balance>0) or position.isWin and balance< 0:
            balance=balance*-1
        
        balance= round(balance,2)

        self.balance+=balance


        if self.balance >= Decimal(self._params.startBalance) * Decimal(self._params.resetAccountPercent):
            self.balance= Decimal(self._params.startBalance)
        

        return balance 

    def modifyPosition(self, sl: Optional[float] = None, tp: Optional[float] = None):
        position= self.positions[-1]
        type= position.type        
        price_current= position.price_current

        if sl <= price_current:
             position.sl= sl
        
        if tp != tp:
             
             if type == OrderType.BUY_STOP and (price_current >= tp):
              raise ValueError("BUY_STOP: the tp price cannot be less than the current price.")
        
        
             if type == OrderType.SELL_STOP and (price_current <= tp):
              raise ValueError("SELL_STOP: the tp price cannot be higher than the current price.")
        
        
             if type == OrderType.BUY_LIMIT and not (price_current >= tp):
               raise ValueError("BUY_LIMIT: the tp price cannot be higher than the current price.")
        
        
             if type == OrderType.SELL_LIMIT and not (price_current <= tp):
               raise ValueError("SELL_LIMIT: the tp price cannot be less than the current price.")
             

             position.tp=tp
    