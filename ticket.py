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
    origin: str
    destination: str
    date: datetime
    departure_time: datetime
    arrival_time: datetime
    duration: str
    changes: int
    single_price: float
    return_price: float
    status: str
    link: str
    direction: str

    # def __str__(self):
    #     return f"From: {self.origin} to {self.destination} \
    #            on {self.date} £{self.price}"


def define_holidays():
    """ Function to find holiadys """
    calendar_holidays = []
    uk_holidays = ['060519', '270519', '260819', '251219', '261219']

    calendar = pd.date_range(
                             start=datetime.date.today(),
                             periods=70)

    calendar_business_days = pd.date_range(
                                            start=datetime.date.today(),
                                            periods=70,
                                            freq='B')

    for day in calendar:
        if day not in calendar_business_days or \
           day.strftime('%d%m%y') in uk_holidays:
            calendar_holidays.append(day.strftime('%d%m%y'))
    return calendar_holidays
