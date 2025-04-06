from dataclasses import dataclass
import datetime
from CalendarNew.impact import Impact

@dataclass
class New:

    time: datetime.datetime
    currency: str
    impact: Impact
    event: str
    actual: str
    forecast: str
    previous: str
    allday: bool

    def __init__(self,  time: datetime.datetime, currency: str, impact: Impact, event: str, actual: float, forecast: float, previous: float, allday:bool):
        self.time = time
        self.currency = currency
        self.impact = impact
        self.event = event
        self.actual = actual
        self.forecast = forecast
        self.previous = previous
        self.allday = allday
