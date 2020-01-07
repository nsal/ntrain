import requests
import re
import sys
import csv
from ticket import Two_for_one
from bs4 import BeautifulSoup, SoupStrainer

offers_link = 'https://www.daysoutguide.co.uk/sitemapxml'


def fill_missing_postcode(station_name: str) -> str:
    """ Fill missing postcodes """
    return station_postcodes[station_name.lower()] or 'None'


def add_nearest_postcodes(postcode: str) -> list:
    """ Add nearest postcodes """
    pass

def call_website(link: str) -> str:
    """ Get data from the website for parsing """
    r = requests.get(link)

    if r.status_code != 200:
        sys.exit(1)

    return r.text


def get_links(html: str, offers_db=[]) -> list:
    """Parse offers data for:
        1. offer's name
        2. offer's url
        3. offer's update time """

    soup = BeautifulSoup(html, 'xml')
    urls = soup.find_all('url')

    # URL for actual offer doesn't have trailing \
    offers_pattern = r'.*[a-z]$'

    for url in urls:
        link = url.find('loc').text
        updated = url.find('lastmod').text
        name = link.split('/')[-1].replace('-', ' ').title()

        if re.match(offers_pattern, link) and updated and name:
            offers_db.append(Two_for_one(link=link,
                                         updated=updated,
                                         name=name))

    return offers_db


def parse_details(pattern: str, data: BeautifulSoup) -> dict:
    """ Parse data using the pattern. Return 'None' if failed """
    answer = re.search(pattern, data)
    return answer.group(1) if answer else 'None'


def get_offer_details(link: str) -> dict:
    """ Create a dict with parsed data:
        1. Attraction's closest railway station
        2. Attraction's postcode
        3. Price for the attraction
        4. Attraction's expiration date """

    station_pattern = r'Nearest station:\n(.+?)\n'
    location_pattern = r'Location:\n(.+?)\n'
    price_pattern = r'Adult: £(\d{1,3}.\d{2})'
    expiration_pattern = r'Offer expires:\n(.+?)\n'
    postcode_pattern = r'[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$'

    html = call_website(link)
    strainer = SoupStrainer('div',
                            attrs={'class': 'attraction-description__table'})
    soup = BeautifulSoup(html, 'lxml', parse_only=strainer).text

    station = parse_details(station_pattern, soup)
    location = parse_details(location_pattern, soup)

    postcode = re.findall(postcode_pattern, location)

    try:
        postcode = postcode[0] if postcode else fill_missing_postcode(station)
    except KeyError:
        postcode = 'None'

    price = parse_details(price_pattern, soup)
    expiration = parse_details(expiration_pattern, soup)

    return {'station': station,
            'postcode': postcode,
            'price': price,
            'expiration': expiration}


if __name__ == '__main__':

    # the block to create a dict {station_name: postcode}
    # to fill missing data

    station_postcodes = {}

    with open('station_codes.csv', 'r') as input_file:
        csv_reader = csv.reader(input_file)
        for row in csv_reader:
            station_postcodes[row[0].lower()] = row[2]

    # end block

    # block to create a dict {postcode: list_of_nearest_postcodes}

    nearest_postcodes = {}

    with open('postcode_districts.csv', 'r') as nearest_pcode_file:
        csv_reader = csv.reader(nearest_pcode_file)
        for row in csv_reader:
            nearest_postcodes[row[0]] = row[12]

    # end block

    raw_offers_data = call_website(offers_link)
    offers_db = get_links(raw_offers_data)

    for offer in offers_db:
        offer_details = get_offer_details(offer.link)
        offer.station = offer_details['station']
        offer.postcode = offer_details['postcode']
        offer.price = offer_details['price']
        offer.expiration = offer_details['expiration']

    with open('2for1.csv', 'w', encoding='utf_8_sig') as offers_file:
        csv_writer = csv.writer(offers_file)
        csv_writer.writerow(['Name',
                             'Station',
                             'Postcode',
                             'Price',
                             'Expiration',
                             'Link',
                             'Updated'])

        for offer in offers_db:
            if offer.price == 'None':
                offer.price = 'Free'
            else:
                offer.price = '£' + offer.price

            csv_writer.writerow([offer.name,
                                offer.station,
                                offer.postcode,
                                offer.price,
                                offer.expiration,
                                offer.link,
                                offer.updated])
