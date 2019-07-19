import requests
import sys
import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def call_for_fares(origin, destination, date, l_time, r_time):
    """ Call national rails for prices """

    link = ('http://ojp.nationalrail.co.uk/service/timesandfares/' +
            origin + '/' + destination + '/' + date + '/' +
            l_time + '/dep/' + date + '/' + r_time + '/dep')

    r = requests.get(link, headers={'User-Agent': UserAgent().random})

    if r.status_code != 200:
        print('Website is down')
        sys.exit(0)

    soup = BeautifulSoup(r.content, 'html.parser')
    print(link)
    return soup


def cook_soup(soup):
    """ """
    
    tr_pattern = r'{"jsonJourneyBreakdown":(.+?)}]}'
    try:
        min_price_list = []
        cheapest_tickets = soup.find('th',
                                     attrs={'class': 'fare'}).findAll('a')
        for ticket in cheapest_tickets:
            ticket_price = ticket.find('strong', attrs={'class':'ctf-pr'}).text
            ticket_price = float(ticket_price.replace('£', ''))
            min_price_list.append(ticket_price)

        cheapest_ticket = min(min_price_list)
        print(cheapest_ticket)

        script_blocks = soup.findAll('script')
        travel_details_raw = re.findall(tr_pattern, str(script_blocks))
        for travel in travel_details_raw:
            journeys = {}
            travel = re.sub('{|"|"', '', travel)
            travel = travel.replace('fullFarePrice', 'SfullFarePrice', 1)
            travel = travel.split(',')
            for item in travel:
                if ':' in item:
                    dict_items = item.split(':', 1)
                    journeys[dict_items[0]] = dict_items[1]
            if float(journeys['ticketPrice']) <= cheapest_ticket or \
               float(journeys['SfullFarePrice']) <= cheapest_ticket:
                print(f"{journeys['departureStationName']} " \
                    f"{journeys['departureTime']} -> "
                    f"{journeys['arrivalStationName']} " \
                    f"{journeys['arrivalTime']} " \
                    f"{journeys['statusMessage']} " \
                    f"{journeys['statusIcon']} " \
                    f"£{journeys['SfullFarePrice']} " \
                    f"£{journeys['ticketPrice']} "  
                    )

         
    except AttributeError:
        print('No data for ticket')
    return None #journeys


soup = call_for_fares(origin='BFD',
                      destination='SAL',
                      date='010819',
                      l_time='0730',
                      r_time='1830')

journeys = cook_soup(soup)


