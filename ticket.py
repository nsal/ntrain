"""
Module contains:
    dataclass Ticket
    dataclass Two_for_one
    function define_holidays
"""
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Ticket:
    """ Class to store ticket data """
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


@dataclass
class Two_for_one:
    """ Class to store 2 for 1 offers details """
    link: str
    updated: str
    name: str
    station: str = None
    postcode: str = None
    price: str = None
    expiration: str = None


def define_holidays(travel_days, search_limit_days):
    """ Function to find travel days """

    search_days = int(search_limit_days)
    today = datetime.today()

    bank_holidays = ['2020-04-13', '2020-05-08', '2020-05-25',
                     '2020-08-31', '2020-12-25', '2020-12-28',
                     '2021-01-01']

    list_of_dates = [(today + timedelta(days=x)).date()
                     for x in range(1, search_days)]

    travel_days_numbers = [int(day) for day in travel_days.split(',')]

    # 7 is an alias for all days
    if 7 not in travel_days_numbers:
        weekends = [datetime.strftime(day, '%d%m%y')
                    for day in list_of_dates
                    if day.weekday() in travel_days_numbers
                    or str(day) in bank_holidays]
        return weekends

    return [datetime.strftime(day, '%d%m%y') for day in list_of_dates]
