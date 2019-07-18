import requests
import re
import sys
import datetime
import csv
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool
import itertools
from ticket import Ticket
from ticket import define_holidays

origin = 'BFD'
destinations = ['SAL', 'CBG', 'BTH', 'CBW', 'RYE', 'DVP',
                'NRW', 'BRI', 'BMH']
list_of_tickets = []
price_index = {}


def call_for_fares(l_date, origin, destination, r_date=None):
    """ Call national rails for prices """
    origin = origin
    destination = destination
    leaving_date = l_date
    return_date = r_date or l_date
    leaving_time = '0700'
    return_time = '1830'
    # Passenger = 2
    # rail_card_discount = 0.34

    link = ('http://ojp.nationalrail.co.uk/service/timesandfares/' +
            origin + '/' + destination + '/' + leaving_date + '/' +
            leaving_time + '/dep/' + return_date + '/' + return_time + '/dep')

    r = requests.get(link, headers={'User-Agent': UserAgent().random})
    if r.status_code != 200:
        print('Website is down')
        sys.exit(0)
    soup = BeautifulSoup(r.content, 'html.parser')

    try:
        cheapest_tickets = soup.find(lambda tag: tag.name == 'th' and
                                     tag.get('class') == ['fare']).findAll('a')

        cheapest_tickets = re.findall(r'£\d{1,3}.\d\d', str(cheapest_tickets))
        cheapest_return = float(cheapest_tickets[0].replace('£', ''))
        cheapest_2singles = float(cheapest_tickets[1].replace('£', ''))
        min_price = float(min(cheapest_return, cheapest_2singles))
        list_of_tickets.append(
            Ticket(
                   origin=origin,
                   destination=destination,
                   date=datetime.datetime.strptime(leaving_date, '%d%m%y'),
                   price=min_price))
        price_list.append(min_price)

    except AttributeError as e:
        print(e, link)

    return list_of_tickets


if __name__ == "__main__":

    calendar_holidays = define_holidays()

    pool = ThreadPool(16)

    for destination in destinations:
        price_list = []
        pool.starmap(call_for_fares,
                     zip(calendar_holidays,
                         itertools.repeat(origin),
                         itertools.repeat(destination)))
        price_index[destination] = min(price_list)
    pool.close()
    pool.join()

    with open('output2.csv', 'w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=",")
        csv_writer.writerow(['Origin', 'Destination', 'Date', 'Price'])
        for item in list_of_tickets:
            #print(item.origin, item.destination, item.date, item.price)

            csv_writer.writerow([
                                item.origin,
                                item.destination,
                                item.date.strftime('%d-%m-%Y'),
                                item.price])
    # for key in price_index:
    #     print(key, price_index[key])

    # for key in price_index:
    #     temp_array = [ticket for ticket in list_of_tickets
    #                   if ticket.destination == key
    #                   and ticket.price == price_index[key]]
    #     for item in temp_array:
    #         print(item)
