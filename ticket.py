"""
Module contains:
    dataclass Ticket
    function define_holidays
    function flask_logging
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
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


def define_holidays(weekends_only, search_limit_days):
    """ Function to find holiadys """

    search_days = int(search_limit_days)
    bank_holidays = ['060519', '270519', '260919', '251219', '261219']
    today = datetime.today()

    list_of_dates = [(today + timedelta(days=x)).date()
                      for x in range(1, search_days)]

    if weekends_only:
        weekends = [datetime.strftime(day, '%d%m%y') 
                    for day in list_of_dates if day.weekday() in (5, 6) or day in bank_holidays ]
        return weekends
    
    return [datetime.strftime(day, '%d%m%y') for day in list_of_dates]


def flask_logging(ip, origin_station_code, destination_station_code,
                  return_option, weekends_only, search_limit_days):

    with open('logs/flask_access.log', 'a') as logfile:
        csv_writer = csv.writer(logfile, delimiter=',')
        timestamp = datetime.strftime(datetime.now(),
                                               '%Y-%m-%d %H:%M:%S')
        csv_writer.writerow([timestamp,
                             ip,
                             origin_station_code,
                             destination_station_code,
                             return_option,
                             weekends_only,
                             search_limit_days])
