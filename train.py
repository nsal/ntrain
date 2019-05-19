import requests, re, sys, json
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import datetime
import pandas as pd
price_index = {}



def define_holidays():
    """ Function to find holiadys """
    calendar_holidays = []
    uk_holidays = ['060519', '270519', '260819', '251219', '261219']
    calendar = pd.date_range(start=datetime.date.today(), periods=30)
    calendar_business_days = pd.date_range(start=datetime.date.today(), periods=30, freq='B')

    for day in calendar:
        if day not in calendar_business_days or day.strftime('%d%m%y') in uk_holidays :
            calendar_holidays.append(day.strftime('%d%m%y'))

    return calendar_holidays

define_holidays()

def call_for_fares(date):
    """ Call national rails for prices """
    origin = 'BFD'
    destination = 'BTH'
    leaving_date = date
    return_date = date
    leaving_time = '0700'
    return_time = '1830'
    Passenger = 2
    rail_card_discount = 0.34
    prices = []
 

    link = 'http://ojp.nationalrail.co.uk/service/timesandfares/' + origin + '/' + destination + '/' + leaving_date + '/' + leaving_time + '/dep/' + \
    return_date + '/' + return_time + '/dep'

    r = requests.get(link, headers={'User-Agent': UserAgent().random})
    soup = BeautifulSoup(r.content, 'html.parser')


    if soup.title.text == 'National Rail Enquiries - Oh no! There\'s been a problem!' or  soup.title.text == '504 - Gateway Timeout':
        print('Website is down')
        sys.exit(0)
 
    try:
        cheapest_tickets = soup.find(lambda tag: tag.name == 'th' and tag.get('class') == ['fare']).findAll('a')

        #print(date)
        print(link)
        cheapest_tickets = re.findall(r'£\d{1,3}.\d\d', str(cheapest_tickets))
        cheapest_return = float(cheapest_tickets[0].replace('£', ''))
        cheapest_2singles = float(cheapest_tickets[1].replace('£', ''))
        if cheapest_return < cheapest_2singles:
            print(f'Cheapest option is Return £{cheapest_return}')
            price_index[date] = cheapest_return
        else:
            print(f'It is better to buy 2 tickets for £{cheapest_2singles}')
            price_index[date] = cheapest_2singles


        # for item in cheapest_tickets:
        #     item_price = re.search(r'£\d{1,3}.\d\d', item.text.replace('\n', ''))
        #     item_price = float(item_price[0].replace('£','')) #* Passenger
        #     prices.append(item_price)
        #     prices.append(item_price - (item_price * rail_card_discount))

        # print(min(prices))
        # print('=== \n')

        script_blocks = soup.findAll('script')
        travel_details_raw = re.findall(r'{"jsonJourneyBreakdown":(.+?)}]}', str(script_blocks))

        for travel in travel_details_raw:
            try:
                departure_time = re.search(r'"departureTime":"\d\d:\d\d', travel)
                arrival_time = re.search(r'"arrivalTime":"\d\d:\d\d', travel)
                #departure_time = int(travel[161:166].replace(':',''))
                #arrival_time = int(travel[183:188].replace(":",''))
                single_fare_raw = re.search(r'"singleJsonFareBreakdowns":(.+?)}],', travel)
                single_fare = re.search(r'"ticketPrice":\d{1,3}.\d{1,2}', single_fare_raw[0])
                return_fare_raw = re.search(r'"returnJsonFareBreakdowns":(.+?)$', travel)
                return_fare = re.search(r'"ticketPrice":\d{1,3}.\d{1,2}', return_fare_raw[0])

                #print(date, departure_time[0], arrival_time[0], single_fare[0], return_fare[0])
            except Exception:
                continue


        # with open ('2test.html', 'w') as ofile:
        #     ofile.write(soup.prettify()) 
    except Exception as e:
        print(e)
    
    return price_index
    
    

calendar_holidays = define_holidays()
for day in calendar_holidays:
    call_for_fares(day)

values = []
for item in price_index:
    values.append(price_index[item])

print(f'Max price: £{max(values)} \nAverage price: £{sum(values) / len(values)} \nMin price: £{min(values)}')

for item in price_index:
    if price_index[item] <= min(values) * 1.20:
        print(item, price_index[item])




# cut = soup.findAll(lambda tag: tag.name == 'td' and tag.get('class') == ['fare'])


# for c in cut:
#     arr = re.findall(r'{"jsonJourneyBreakdown":(.+?)}]}', str(c))
#     if arr: 
#         departure_time = re.search(r'"departureTime":"\d\d:\d\d', arr[0])
#         arrival_time = re.search(r'"arrivalTime":"\d\d:\d\d', arr[0])
#         ticket_price = re.search(r'"ticketPrice":\d{1,3}.\d{1,2}', arr[0])
#         ticket_price = float(ticket_price[0].split(':')[1]) * 2
#         ticket_price = round((ticket_price - (ticket_price * 0.34)), 2)
#         print('Departure time:', departure_time[0].split('"')[3], '\t', 'Arrival time:', arrival_time[0].split('"')[3], '\t', 'Price', ticket_price )



