from datetime import datetime
from enum import Enum
from typing import Optional
from Core.Client.Client import OrderType
from Utils.Utils import generateId

class OrderStatus(Enum):
    ACTIVE = 1
    FILLED = 2
    CANCELLED = 3


class Order:
    
    def __init__(self, price:float, type:OrderType, sl: Optional[float] = None, tp: Optional[float] = None, date:datetime = None, volume: Optional[float]= None):
        
        self.id = generateId()
        self.price = price
        self.type = type
        self.sl = sl
        self.tp = tp
        self.date = date
        self.status: OrderStatus = OrderStatus.ACTIVE
        self.is_buy = True if type == OrderType.BUY_LIMIT or type == OrderType.BUY_STOP else False
        self.is_sell = True if type == OrderType.SELL_LIMIT or type == OrderType.SELL_STOP else False
        self.is_stop = True if type == OrderType.BUY_STOP or type == OrderType.SELL_STOP else False
        self.is_limit = True if type == OrderType.BUY_LIMIT or type == OrderType.SELL_LIMIT else False
        self.volume= volume
