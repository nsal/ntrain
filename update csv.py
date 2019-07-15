import csv
from datetime import datetime
new_data = []
old_data = []
temp_data = []

with open('output.csv', 'r') as old_file:
    csv_reader_old = csv.reader(old_file, delimiter=',')
    next(csv_reader_old, None)
    for old_row in csv_reader_old:
        old_data.append([str(old_row[0]),
                         str(old_row[1]),
                         str(old_row[2]),
                         float(old_row[3])])

with open('output2.csv', 'r') as new_file:
    csv_reader = csv.reader(new_file, delimiter=',')
    next(csv_reader, None)
    for new_row in csv_reader:

        new_data.append([str(new_row[0]),
                         str(new_row[1]),
                         str(new_row[2]),
                         float(new_row[3])])
        for old_row in old_data:
            if old_row[:3] == new_row[:3] and old_row[3] != float(new_row[3]):
                if old_row[3] < float(new_row[3]):
                    print(f"Price has increased for {old_row[0]} -> \
                          {old_row[1]} on {old_row[2]} from £{old_row[3]}\
                          to £{float(new_row[3])}")
                else:
                    print(f"Price has DECREASED for {old_row[0]} -> \
                          {old_row[1]} on {old_row[2]} from £{old_row[3]}\
                          to £{float(new_row[3])}")
                old_row[3] = float(new_row[3])
                break

for n in new_data:
    if n not in old_data:
        old_data.append(n)
        print(f"New Ticket: {n[0]} -> {n[1]} on {n[2]} for £{float(n[3])} ")

old_data.sort(key=lambda x: datetime.strptime(x[2], '%d-%m-%Y'))
old_data.sort(key=lambda x: x[1])


with open('output.csv', 'w') as updated_file:
    csv_writer = csv.writer(updated_file, delimiter=',')
    csv_writer.writerow(['Origin', 'Destination', 'Date', 'Price'])
    for row in old_data:
        csv_writer.writerow(row)
