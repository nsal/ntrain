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
list_of_tickets = []  # list to store elements of Ticket class
price_index = {}  # dict to store min price per destination. e.g. SAL:20
price_list = []  # list to store min price per date for certain destination


def find_min_price(soup, link):
    """ """
    try:
        cheapest_tickets = soup.find(lambda tag: tag.name == 'th' and
                                     tag.get('class') == ['fare']).findAll('a')

        cheapest_tickets = re.findall(r'£\d{1,3}.\d\d', str(cheapest_tickets))
        cheapest_return = float(cheapest_tickets[0].replace('£', ''))
        cheapest_2singles = float(cheapest_tickets[1].replace('£', ''))
        min_price = float(min(cheapest_return, cheapest_2singles))
    except AttributeError as e:
        print(e, link)
    return min_price


def update_price_list(price, price_list=price_list):
    """ """
    price_list.append(price)
    return price_list

def get_ride_details(soup, leaving_date, return_date, list_of_tickets=list_of_tickets):
    """ """
    tr_pattern = r'{"jsonJourneyBreakdown":(.+?)}]}'

    script_blocks = soup.findAll('script')
    ride_details = re.findall(tr_pattern, str(script_blocks))
    for rides in ride_details:
        daily_rides = {}
        rides = re.sub('{|"|"', '', rides)
        rides = rides.replace('fullFarePrice', 'SfullFarePrice', 1)
        rides = rides.split(',')
        for ride in rides:
            if ':' in ride:
                temp_dict = ride.split(':', 1)
                daily_rides[temp_dict[0]] = temp_dict[1]

        # print(f"{daily_rides['departureStationName']} " \
        #             f"{daily_rides['departureTime']} -> "
        #             f"{daily_rides['arrivalStationName']} " \
        #             f"{daily_rides['arrivalTime']} " \
        #             f"{daily_rides['statusMessage']} " \
        #             f"{daily_rides['statusIcon']} " \
        #             f"£{daily_rides['SfullFarePrice']} " \
        #             f"£{daily_rides['ticketPrice']} "  
        #             )
        duration = daily_rides['durationHours'] + ":" + \
                   daily_rides['durationMinutes']

        ticket = Ticket(origin=daily_rides['departureStationCRS'],
                departure_time=daily_rides['departureTime'],
                destination=daily_rides['arrivalStationCRS'],
                arrival_time=daily_rides['arrivalTime'],
                date=leaving_date,
                single_price=daily_rides['SfullFarePrice'],
                return_price=daily_rides['ticketPrice'],
                status=daily_rides['statusIcon'],
                duration=duration,
                changes=daily_rides['changes'])
        list_of_tickets.append(ticket)
    return list_of_tickets  

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
        sys.exit(0)  # doesn't work in multithreading

    soup = BeautifulSoup(r.content, 'html.parser')
    min_price = find_min_price(soup, link)
    update_price_list(price=min_price)
    #get_ride_details(soup)
    # ticket = Ticket(
    #             origin=origin,
    #             destination=destination,
    #             date=datetime.datetime.strptime(leaving_date, '%d%m%y'),
    #             price=min_price)

    get_ride_details(soup,leaving_date, return_date)
    

    return None


if __name__ == "__main__":

    calendar_holidays = define_holidays()

    pool = ThreadPool(16)

    for destination in destinations:
        price_list.clear()  # clear list of prices for each destination
        pool.starmap(call_for_fares,
                     zip(calendar_holidays,
                         itertools.repeat(origin),
                         itertools.repeat(destination),
                         ))
        price_index[destination] = min(price_list)
    pool.close()
    pool.join()

    with open('output2.csv', 'w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=",")
        csv_writer.writerow(['Origin', 'Destination', 'Date', 'Departure',\
                             'Arrival', 'Duration', 'Changes', \
                             'Single Price', 'Return Price', 'Status'])
        for ticket in list_of_tickets:
            # print(item.origin, item.destination, item.date, item.price)

            csv_writer.writerow([
                                ticket.origin,
                                ticket.destination,
                                ticket.date, #.strftime('%d-%m-%Y'),
                                ticket.departure_time,
                                ticket.arrival_time,
                                ticket.duration,
                                ticket.changes,
                                ticket.single_price,
                                ticket.return_price,
                                ticket.status])
    for key in price_index:
        print(key, price_index[key])

    # for key in price_index:
    #     temp_array = [ticket for ticket in list_of_tickets
    #                   if ticket.destination == key
    #                   and ticket.price == price_index[key]]
    #     for item in temp_array:
    #         print(item)
