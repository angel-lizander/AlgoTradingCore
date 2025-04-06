from abc import ABC, abstractmethod
from datetime import datetime

from Core.Client.Client import Client
from Utils.StrategyUtils import StrategyUtils

class Strategy(ABC):
    """
    A trading strategy base class. Extend this class and
    override methods to define your own strategy.
    """

    def __init__(self, client: Client = None, params = None, date: datetime = None, data = None, utils: StrategyUtils = None):
        self.client: Client = client
        self._params = params
        self.date = date
        self.data = data
        self.utils =utils

    @abstractmethod
    def init(self):
        """
        Initialize the strategy.
        """

    @abstractmethod
    def run(self):
        """
        Main strategy runtime method
        """

    