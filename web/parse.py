import requests
import re
import datetime
from multiprocessing.dummy import Pool as ThreadPool
import itertools
from ticket import Ticket
from ticket import define_holidays


list_of_tickets = []
price_index = {}


def call_for_fares(l_date, origin, destination, 
                   same_day_return, r_date=None):
    """ Call national rails for prices """
    origin = origin
    destination = destination
    leaving_date = l_date
    return_date = r_date or l_date
    leaving_time = '0700'
    return_time = '1830'
    price_array = []

    if same_day_return:
        link = ('http://ojp.nationalrail.co.uk/service/timesandfares/' +
                origin + '/' + destination + '/' + leaving_date + '/' +
                leaving_time + '/dep/' + return_date + '/' + return_time +
                '/dep')
    else:
        link = ('http://ojp.nationalrail.co.uk/service/timesandfares/' +
                origin + '/' + destination + '/' + leaving_date + '/' +
                leaving_time + '/dep/')

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
            price_array.append(float(cheapest_ticket))
            list_of_tickets.append(
                Ticket(
                    origin=origin,
                    destination=destination,
                    date=datetime.datetime.strptime(leaving_date,
                                                    '%d%m%y').date(),
                    price=cheapest_ticket,
                    link=link))
    except Exception as e:
        print(e, link)
    return list_of_tickets


def launcher(origin, destination, same_day_return):
    list_of_tickets.clear()
    calendar_holidays = define_holidays()
    pool = ThreadPool(12)

    pool.starmap(call_for_fares,
                    zip(calendar_holidays,
                        itertools.repeat(origin),
                        itertools.repeat(destination),
                        itertools.repeat(same_day_return)))

    pool.close()
    pool.join()
    list_of_tickets.sort(key=lambda x: x.date)
    return list_of_tickets
