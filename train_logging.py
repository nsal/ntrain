import csv
from datetime import datetime


def train_logging(ip, origin_station_code, origin_departure_time,
                  destination_station_code, destination_departure_time,
                  return_option, travel_days, search_limit_days):

    with open('logs/flask_access.log', 'a') as logfile:
        csv_writer = csv.writer(logfile, delimiter=',')
        timestamp = datetime.strftime(datetime.now(),
                                      '%Y-%m-%d %H:%M:%S')
        csv_writer.writerow([timestamp,
                             ip,
                             origin_station_code,
                             origin_departure_time,
                             destination_station_code,
                             destination_departure_time,
                             return_option,
                             travel_days,
                             search_limit_days])
