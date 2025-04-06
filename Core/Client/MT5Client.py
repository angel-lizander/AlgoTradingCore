
import datetime
from typing import Optional
from Core.Client.Client import Client, OrderType, TimeFrame
import pandas as pd
from Utils.Utils import currentDate, mt5ParseData

class MT5Client(Client):
    """
    MetaTrader 5 Client
    """
    
    def init(self, mt5):
        self._name = "MetaTrader 5"
        self.mt5 = mt5
        print('init ', self._name)
        login = self._login()
        date = currentDate()
        fromdate = date - datetime.timedelta(days=5)
        if login:
           self.data = self.getData(fromDate= fromdate, toDate=date)
    
    def _login(self):
        account = self._params
        if not self.mt5.initialize(account.rootTerminal, login=int(account.user),password=account.password, server=account.server):
            print("initialize() failed, error code =",self.mt5.last_error())
            return False   
        else:
            self.mt5.login(login=int(account.user),
                    password=account.password, server=account.server)
            return True

    def _getMt5OrderType(self, type:OrderType):
        if type == OrderType.BUY_STOP:
            return self.mt5.ORDER_TYPE_BUY_STOP
        elif type == OrderType.BUY_LIMIT:
            return self.mt5.ORDER_TYPE_BUY_LIMIT
        elif type == OrderType.SELL_STOP:
            return self.mt5.ORDER_TYPE_SELL_STOP
        elif type == OrderType.SELL_LIMIT:
            return self.mt5.ORDER_TYPE_SELL_LIMIT    

    def newOrder(self, price:float, type:OrderType, sl: Optional[float] = None, tp: Optional[float] = None, volume: Optional[float]= None):

        orderType = self._getMt5OrderType(type=type)

        request = {
            "action": self.mt5.TRADE_ACTION_PENDING,
            "symbol": self._params.symbol.name,
            "volume": volume,  
            "type": orderType,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": self._params.deviation,
            "comment": self._strategyName,
            "type_time": self.mt5.ORDER_TIME_GTC,
            "type_filling": self.mt5.ORDER_FILLING_RETURN,
            "magic": 2,
        }

        order_result = self.mt5.order_send(request)
        print(self.mt5.last_error())
        return (order_result)
    
    def getOrders(self):
        return self.mt5.orders_get()

    def getTotalOrders(self):
        return self.mt5.orders_total()
    
    def cancelOrder(self, order):
        close_request = {
            "action": self.mt5.TRADE_ACTION_REMOVE,
            "order": order[0],
            "type_time": self.mt5.ORDER_TIME_GTC,
            "type_filling": self.mt5.ORDER_FILLING_IOC,
        }
        result = self.mt5.order_send(close_request)

        if result.retcode != self.mt5.TRADE_RETCODE_DONE:
            result_dict = result._asdict()
            return result_dict
        else:
            return True
    
    def cancelAllOrders(self):
        pendingOrders = self.getOrders()
        for order in pendingOrders:
            self.cancelOrder(order)
        return True
    
    def getPositions(self):
        return self.mt5.positions_get()
    
    
    def getTotalPositions(self):
        return self.mt5.positions_total()
        
    
    def closePosition(self, position):
        order_type_dict = {
            0: self.mt5.ORDER_TYPE_SELL,
            1: self.mt5.ORDER_TYPE_BUY
        }

        price_dict = {
            0: self.mt5.symbol_info_tick(self._params.symbol.name).bid,
            1: self.mt5.symbol_info_tick(self._params.symbol.name).ask
        }

        request = {
            "action": self.mt5.TRADE_ACTION_DEAL,
            # select the position you want to close
            "position": position['ticket'],
            "symbol": self._params.symbol.name,
            "volume": self._params.volume,  # FLOAT
            "type": order_type_dict[position['type']],
            "price": price_dict[position['type']],
            "deviation": self._params.deviation,  # INTERGER
            "comment": self._strategyName,
            "type_time": self.mt5.ORDER_TIME_GTC,
            "type_filling": self.mt5.ORDER_FILLING_IOC,
        }

        return self.mt5.order_send(request)
    
    def closeAllPositions(self):
        positions = self.getPositions()
        for position in positions:
            self.closePosition(position)
        return True
    
    def getData(self, fromDate:datetime = None, toDate:datetime = None, timeframe: TimeFrame = TimeFrame.M1):
        date = currentDate()
        toDate = date if toDate == None else toDate
        fromDate = date - datetime.timedelta(days=1) if fromDate == None else fromDate

        data = pd.DataFrame(self.mt5.copy_rates_range(self._params.symbol.name, timeframe.value, fromDate, toDate))      
        data = mt5ParseData(data)
        self.data = data

        return data
    
    def getAccountInfo(self):
        return self.mt5.account_info()
    
    def getBalance(self):
        return self.getAccountInfo().balance
    
    def getSymbolInfo(self):
        return self.mt5.symbol_info(self._params.symbol.name)
    
    def modifyPosition(self, sl: Optional[float] = None, tp: Optional[float] = None):
        
        position= self.mt5.positions_get()[0]
        request = {
            'action': self.mt5.TRADE_ACTION_SLTP,
            'position': position['ticket'],
            'sl': sl,
        }

        if tp != None:
            request.tp= tp
        

        order_result = self.mt5.order_send(request)
        print(self.mt5.last_error())
        return (order_result)