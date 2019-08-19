"""
Module contains:
    dataclass Ticket
    function define_holidays
    function flask_logging
"""
from dataclasses import dataclass
import datetime
import pandas as pd
import csv


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
    chart: str = None

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


def flask_logging(ip, origin_station_code, destination_station_code,
                  same_day_return, weekends_only):

    with open('flask_access.log', 'a') as logfile:
        csv_writer = csv.writer(logfile, delimiter=',')
        timestamp = datetime.datetime.strftime(datetime.datetime.now(),
                                               '%Y-%m-%d %H:%M:%S')
        csv_writer.writerow([timestamp,
                             ip,
                             origin_station_code,
                             destination_station_code,
                             same_day_return,
                             weekends_only])
