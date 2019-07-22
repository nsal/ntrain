import csv
from datetime import datetime
from ticket import Ticket
from ticket import define_holidays

destinations = ['SAL', 'CBG', 'BTH', 'CBW', 'RYE', 'DVP',
                'NRW', 'BRI', 'BMH']
list_of_tickets = []


with open('output2.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    next(csv_reader, None)
    for row in csv_reader:
        list_of_tickets.append(Ticket(
                origin=row[0],
                destination=row[1],
                date=datetime.strptime(row[2], '%d%m%Y'),
                departure_time=row[3],
                arrival_time=row[4],
                duration=row[5],
                changes=row[6],
                single_price=float(row[7]),
                return_price=float(row[8]),
                status=row[9],
                direction=row[10],
                link=row[11]))

dates = define_holidays()

destinations = ['SAL']
min_price = 20
counter = 0

def find_tickets(date): 
    for ticket in list_of_tickets:
        if ticket.date == datetime.strptime(date, '%d%m%y') and (ticket.origin == destination or ticket.destination == destination):
            if ticket.return_price <= min_price or ticket.single_price <= min_price / 2 and ticket.status == 'OK':
                print(ticket.origin, ticket.date, ticket.departure_time)
                global counter
                counter +=1 
    return counter

# for destination in destinations:
#     for date in dates:
#         find_tickets(date)

# print(counter)


a = [x for x in list_of_tickets if x.destination == 'SAL']


