"""
Module contains:
    dataclass Ticket
    function define_holidays
"""
from dataclasses import dataclass
import datetime
import pandas as pd


@dataclass
class Ticket:
    """
    Class to store ticket data:
        - origin
        - destination
        - date
        - price
    """
    origin_station_code: str
    destination_station_code: str
    date: int
    price: float
    link: str
    destination: str = None
    origin: str = None

    def __str__(self):
        return f"From: {self.origin} to {self.destination} \
               on {self.date} £{self.price}"


def define_holidays(weekends_only):
    """ Function to find holiadys """
    calendar_holidays = []
    uk_holidays = ['060519', '270519', '260819', '251219', '261219']
    calendar = pd.date_range(
                             start=datetime.date.today(),
                             periods=60)

    calendar_business_days = pd.date_range(
                                            start=datetime.date.today(),
                                            periods=60,
                                            freq='B')

    for day in calendar:
        if weekends_only:
            if day not in calendar_business_days or \
            day.strftime('%d%m%y') in uk_holidays:
                calendar_holidays.append(day.strftime('%d%m%y'))
        else:
            calendar_holidays.append(day.strftime('%d%m%y'))

    return calendar_holidays
