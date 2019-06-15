import requests
import re
import sys
import datetime
import csv
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import pandas as pd
from dataclasses import dataclass
import time
from multiprocessing.dummy import Pool as ThreadPool
import itertools


@dataclass
class Ticket:
    origin: str
    destination: str
    date: int
    price: float


origin = 'BFD'
destinations = ['SAL', 'CBG', 'BTH', 'CBW', 'WIN', 'BTN', 'RYE', 'DVP',
                'NRW', 'BRI']
list_of_tickets = []
website_errors = ['National Rail Enquiries - Oh no! There\'s been a problem!',
                  '504 - Gateway Timeout']


def define_holidays():
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
        if day not in calendar_business_days or \
           day.strftime('%d%m%y') in uk_holidays:
            calendar_holidays.append(day.strftime('%d%m%y'))

    return calendar_holidays


def call_for_fares(l_date, origin, destination):
    """ Call national rails for prices """
    origin = origin
    destination = destination
    leaving_date = l_date
    return_date = l_date
    leaving_time = '0700'
    return_time = '1830'
    # Passenger = 2
    # rail_card_discount = 0.34

    link = ('http://ojp.nationalrail.co.uk/service/timesandfares/' +
            origin + '/' + destination + '/' + leaving_date + '/' +
            leaving_time + '/dep/' + return_date + '/' + return_time + '/dep')

    r = requests.get(link, headers={'User-Agent': UserAgent().random})
    soup = BeautifulSoup(r.content, 'html.parser')

    if soup.title.text in website_errors:
        print('Website is down')
        sys.exit(0)

    try:
        cheapest_tickets = soup.find(lambda tag: tag.name == 'th' and
                                     tag.get('class') == ['fare']).findAll('a')

        cheapest_tickets = re.findall(r'£\d{1,3}.\d\d', str(cheapest_tickets))
        cheapest_return = float(cheapest_tickets[0].replace('£', ''))
        cheapest_2singles = float(cheapest_tickets[1].replace('£', ''))
        list_of_tickets.append(
            Ticket(
                   origin=origin,
                   destination=destination,
                   date=datetime.datetime.strptime(leaving_date, '%d%m%y'),
                   price=float(min(cheapest_return, cheapest_2singles))))

        # script_blocks = soup.findAll('script')
        # travel_details_raw = re.findall(r'{"jsonJourneyBreakdown":(.+?)}]}',
        #                                 str(script_blocks))

        # for travel in travel_details_raw:
        #     try:
        #         departure_time = re.search(r'"departureTime":"\d\d:\d\d',
        #                                    travel)
        #         arrival_time = re.search(r'"arrivalTime":"\d\d:\d\d',
        #                                  travel)
        #         #departure_time = int(travel[161:166].replace(':',''))
        #         #arrival_time = int(travel[183:188].replace(":",''))
        #         single_fare_raw = re.search(
        #                           r'"singleJsonFareBreakdowns":(.+?)}],',
        #                           travel)
        #         single_fare = re.search(r'"ticketPrice":\d{1,3}.\d{1,2}',
        #                                 single_fare_raw[0])
        #         return_fare_raw = re.search(
        #                           r'"returnJsonFareBreakdowns":(.+?)$',
        #                           travel)
        #         return_fare = re.search(r'"ticketPrice":\d{1,3}.\d{1,2}',
        #                                 return_fare_raw[0])

        #         print(date, departure_time[0], arrival_time[0],
        #               single_fare[0], return_fare[0])
        #     except Exception:
        #         continue

        # with open ('2test.html', 'w') as ofile:
        #     ofile.write(soup.prettify())
    except Exception as e:
        print(e)

    return list_of_tickets

start = time.time()
calendar_holidays = define_holidays()

pool = ThreadPool(16)

for destination in destinations:
    results = pool.starmap(call_for_fares, zip(calendar_holidays, itertools.repeat(origin), itertools.repeat(destination)))
pool.close()
pool.join()


#for destination in destinations:
    
#     for day in calendar_holidays:
#         call_for_fares(
#                         l_date=day,
#                         r_date=day,
#                         origin=origin,
#                         destination=destination)

with open('output.csv', 'w') as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=",")
    csv_writer.writerow(['Origin', 'Destination', 'Date', 'Price'])
    for item in list_of_tickets:
        print(item.origin, item.destination, item.date, item.price)

        csv_writer.writerow([
                            item.origin,
                            item.destination,
                            item.date.strftime('%d-%b-%Y'),
                            item.price])
end = time.time()
print(end - start)

# cut = soup.findAll(lambda tag: tag.name == 'td' and
#                    tag.get('class') == ['fare'])


# for c in cut:
#     arr = re.findall(r'{"jsonJourneyBreakdown":(.+?)}]}', str(c))
#     if arr:
#         departure_time = re.search(r'"departureTime":"\d\d:\d\d', arr[0])
#         arrival_time = re.search(r'"arrivalTime":"\d\d:\d\d', arr[0])
#         ticket_price = re.search(r'"ticketPrice":\d{1,3}.\d{1,2}', arr[0])
#         ticket_price = float(ticket_price[0].split(':')[1]) * 2
#         ticket_price = round((ticket_price - (ticket_price * 0.34)), 2)
#         print('Departure time:', departure_time[0].split('"')[3], '\t',
#               'Arrival time:', arrival_time[0].split('"')[3], '\t', 'Price',
#                ticket_price )
