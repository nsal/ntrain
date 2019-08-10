import requests
import re
import datetime
from bs4 import BeautifulSoup, SoupStrainer 
from multiprocessing.dummy import Pool as ThreadPool
import itertools
import lxml
from ticket import Ticket
from ticket import define_holidays


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
    price_array = []
    
    link = ('http://ojp.nationalrail.co.uk/service/timesandfares/' +
            origin + '/' + destination + '/' + leaving_date + '/' +
            leaving_time + '/dep/' + return_date + '/' + return_time + '/dep')

    user_agent = 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2117.157 Safari/537.36'
    r = requests.get(link, headers={'User-Agent': user_agent})

    pre_soup = SoupStrainer('th')
    soup = BeautifulSoup(r.content, 'lxml', parse_only=pre_soup)

    try:
        cheapest_tickets = soup.find(lambda tag: tag.name == 'th' and
                                     tag.get('class') == ['fare']).findAll('a')

        cheapest_tickets = re.findall(r'£\d{1,3}.\d\d', str(cheapest_tickets))
        for ticket in cheapest_tickets:
            price_array.append(float(ticket.replace('£', '')))
        min_price = min(price_array)
        list_of_tickets.append(
            Ticket(
                   origin=origin,
                   destination=destination,
                   date=datetime.datetime.strptime(leaving_date, '%d%m%y').date(),
                   price=min_price,
		   link=link))
        # price_list.append(min_price)

    except AttributeError as e:
        print(e, link)
    return list_of_tickets
    

def launcher(origin, destination):
    list_of_tickets.clear()
    calendar_holidays = define_holidays()
    pool = ThreadPool(12)

    # price_list = []
    pool.starmap(call_for_fares,
                    zip(calendar_holidays,
                        itertools.repeat(origin),
                        itertools.repeat(destination)))
    # price_index[destination] = min(price_list)
    pool.close()
    pool.join()
    list_of_tickets.sort(key=lambda x: x.date)
    return list_of_tickets
