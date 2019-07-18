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
        cheapest_tickets = soup.find('th',
                                     attrs={'class': 'fare'}).findAll('a')
        cheapest_tickets = (re.findall(r'£\d{1,3}.\d\d', str(cheapest_tickets)))
        
        cheapest_ticket = min(cheapest_tickets)
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
    return journeys


soup = call_for_fares(origin='BFD',
                      destination='SAL',
                      date='010819',
                      l_time='0730',
                      r_time='1830')

journeys = cook_soup(soup)


