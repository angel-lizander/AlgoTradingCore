from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Optional


class OrderType(Enum):
    BUY_STOP    = 1
    BUY_LIMIT   = 2

    SELL_STOP   = 3
    SELL_LIMIT  = 4


class TimeFrame(Enum):
    M1   = 1
    M2   = 2
    M3   = 3
    M4   = 4
    M5   = 5
    M6   = 6
    M10  = 10
    M12  = 12
    M15  = 15
    M20  = 20
    M30  = 30
    H1   = 1  | 0x4000
    H2   = 2  | 0x4000
    H4   = 4  | 0x4000
    H3   = 3  | 0x4000
    H6   = 6  | 0x4000
    H8   = 8  | 0x4000
    H12  = 12 | 0x4000
    D1   = 24 | 0x4000
    W1   = 1  | 0x8000
    MN1  = 1  | 0xC000

class Client(ABC):
    """
    Trading client base class. Extend this class and
    override methods to define your own client.
    """

    def __init__(self, name: str =None, strategyName:str = None, params = None, **kwargs):
        self._name = name
        self._strategyName=strategyName
        self._params = params
        self.data = None
   
    @abstractmethod
    def init(self):
        """
        Initialize the client
        """

    @abstractmethod
    def newOrder(self, price:float, type:OrderType, sl: Optional[float] = None, tp: Optional[float] = None, **kwargs):
        """
        New order method
        """
    
    @abstractmethod
    def getOrders(self, **kwargs):
        """Returns all pending orders (have not been filled) in the account."""

    @abstractmethod
    def getTotalOrders(self, **kwargs):
        """Get the number of active orders."""
    
    @abstractmethod
    def cancelOrder(self, order, **kwargs):
        """Cancels order by order."""

    @abstractmethod
    def cancelAllOrders(self, **kwargs):
        """Cancels all order"""
    
    @abstractmethod
    def getPositions(self, **kwargs):
        """Returns all positions in the account."""
    
    @abstractmethod
    def getTotalPositions(self, **kwargs):
        """Get the number of active positions."""

    @abstractmethod
    def closePosition(self, position, **kwargs):
        """Close position by position."""

    @abstractmethod
    def closeAllPositions(self, **kwargs):
        """Close all positions"""
    
    @abstractmethod
    def getBalance(self, **kwargs):
        """Get the actual balance of the account"""

    @abstractmethod
    def getAccountInfo(self, **kwargs):
        """Get the account information"""
    
    @abstractmethod 
    def getData(self, fromDate:datetime =None, toDate:datetime = None, timeframe: TimeFrame = TimeFrame.M1, **kwargs):
        """ Function to import the data"""

    @abstractmethod 
    def getSymbolInfo(self):
        """ Get all the symbol information"""

    @abstractmethod 
    def modifyPosition(self, sl: Optional[float] = None, tp: Optional[float] = None, **kwargs):
        """ Modify the position take-profit or stop loss"""
    


    
    