from datetime import datetime
from decimal import *
from enum import Enum
from typing import Optional
from Core.Client.Client import OrderType
from Utils.Utils import generateId

class PositionStatus(Enum):
    ACTIVE = 1
    CLOSED = 2


class Position:
    
    def __init__(self, price:float, type:OrderType, sl: Optional[float] = None, tp: Optional[float] = None, filledDate:datetime = None, volume: Optional[float] = None):
        
        self.id = generateId()
        self.price = price
        self.closedPrice:float = None
        self.type = type
        self.sl = sl
        self.tp = tp
        self.volume= volume
        self.filledDate:datetime = filledDate
        self.closedDate:datetime = None
        self.isWin:bool = False
        self.isLoss:bool = False
        self.pnl:Decimal = 0.0
        self.profit:float= 0.0
        self.price_current: float=0.0
        self.status: PositionStatus = PositionStatus.ACTIVE
        self.isBuy = True if type == OrderType.BUY_LIMIT or type == OrderType.BUY_STOP else False
        self.isSell = True if type == OrderType.SELL_LIMIT or type == OrderType.SELL_STOP else False
        self.isStop = True if type == OrderType.BUY_STOP or type == OrderType.SELL_STOP else False
        self.isLimit = True if type == OrderType.BUY_LIMIT or type == OrderType.SELL_LIMIT else False
            