import requests
import re
from datetime import datetime, timedelta
from multiprocessing.dummy import Pool as ThreadPool
import itertools
from ticket import Ticket
from ticket import define_holidays


list_of_tickets = []
price_index = {}


def call_for_fares(l_date, origin, origin_departure_time,
                   destination, destination_departure_time,
                   return_option):
    """ Call national rails for prices """

    leaving_time = origin_departure_time
    return_time = destination_departure_time
    leaving_date = l_date

    if return_option == '999':
        link = ('http://ojp.nationalrail.co.uk/service/timesandfares/' +
                origin + '/' + destination + '/' + leaving_date + '/' +
                leaving_time + '/dep/')

    else:
        return_option = int(return_option) - 1
        return_date = datetime.strptime(l_date, '%d%m%y') + \
            timedelta(days=return_option)
        return_date = datetime.strftime(return_date, '%d%m%y')

        link = ('http://ojp.nationalrail.co.uk/service/timesandfares/' +
                origin + '/' + destination + '/' + leaving_date + '/' +
                leaving_time + '/dep/' + return_date + '/' + return_time +
                '/dep')

    user_agent = 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 \
                 (KHTML, like Gecko) Chrome/35.0.2117.157 Safari/537.36'

    r = requests.get(link, headers={'User-Agent': user_agent})

    if r.status_code != 200:
        # don't know yet how to exit from multithreading
        pass

    try:
        cheapest_ticket = re.search(r'Buy cheapest for &#163; \d{1,3}.\d\d',
                                    r.text)
        if cheapest_ticket:
            cheapest_ticket = cheapest_ticket[0].split('; ')[1]
            list_of_tickets.append(
                Ticket(
                    origin_station_code=origin,
                    destination_station_code=destination,
                    date=datetime.strptime(leaving_date, '%d%m%y').date(),
                    price=float(cheapest_ticket),
                    link=link))
    except Exception as e:
        print(e, link)
    return list_of_tickets


def make_chart_bar(min_price, current_price):
    """ """
    counter = int((((current_price * 100) / min_price) - 100) / 5) + 1
    if counter > 5:
        counter = 5
    chart = '£' * counter
    return chart


def launcher(origin, origin_station_code, origin_departure_time,
             destination, destination_station_code, destination_departure_time,
             return_option, travel_days, search_limit_days):
    list_of_tickets.clear()

    calendar_holidays = define_holidays(travel_days, search_limit_days)
    pool = ThreadPool(12)
    pool.starmap(call_for_fares,
                 zip(calendar_holidays,
                     itertools.repeat(origin_station_code),
                     itertools.repeat(origin_departure_time),
                     itertools.repeat(destination_station_code),
                     itertools.repeat(destination_departure_time),
                     itertools.repeat(return_option)))
    pool.close()
    pool.join()

    list_of_tickets.sort(key=lambda x: x.date)

    min_price_in_period = (min(list_of_tickets, key=lambda x: x.price))
    min_price_in_period = int(min_price_in_period.price)
    for ticket in list_of_tickets:
        ticket.origin = origin
        ticket.destination = destination
        ticket.chart = make_chart_bar(min_price_in_period, int(ticket.price))
        ticket.date = datetime.strftime(ticket.date, '%B %d, %A')

    return list_of_tickets
