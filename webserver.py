import json
import csv
from flask import Flask, Response, render_template, request, url_for, flash, redirect # noqa
from config import Config
from parse import launcher
from train_logging import train_logging
from ticket import Two_for_one


application = Flask(__name__)
application.config.from_object(Config)

station_codes = {}
station_postcodes = {}
two_for_one_offers = []

with open('station_codes.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        station_codes[row[1]] = row[0]
        station_postcodes[row[1]] = row[2]

with open('2for1.csv', 'r') as offers_file:
    csv_reader = csv.reader(offers_file)
    for row in csv_reader:
        two_for_one_offers.append(Two_for_one(
                                  name=row[0],
                                  station=row[1],
                                  postcode=row[2],
                                  price=row[3],
                                  expiration=row[4],
                                  link=row[5],
                                  updated=row[6]))


@application.route('/_autocomplete', methods=['GET'])
def autocomplete():
    return Response(json.dumps(list(station_codes.values())),
                    mimetype='application/json')


@application.route('/', methods=['GET', 'POST'])
def home():
    return render_template("index.html",
                           stations=list(station_codes.values()))


@application.route("/result", methods=['GET', 'POST'])
def result():
    # block to grab user's input
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    origin = request.form.get('origin')
    origin_departure_time = request.form.get('origin_departure_time')
    destination = request.form.get('destination')
    destination_departure_time = request.form.get('destination_departure_time')
    search_limit_days = request.form.get('search_limit_days')
    return_option = request.form.get('return_option')
    travel_days = request.form.get('travel_days')
    # end block

    # block to validate input data \ prevent users from typos
    if origin not in station_codes.values() \
       or destination not in station_codes.values():
        flash('Check your input')
        return redirect(url_for('home'))
    # end block

    origin_station_code = [key for key, value in station_codes.items()
                           if value == origin][0]
    destination_station_code = [key for key, value in station_codes.items()
                                if value == destination][0]

    destination_postcode = station_postcodes[destination_station_code]
    destination_postcode = destination_postcode.split(' ')[0]

    destination_offers = [offer for offer in two_for_one_offers if
                          destination_postcode == offer.postcode.split(' ')[0]]

    list_of_tickets = launcher(
        origin=origin,
        origin_station_code=origin_station_code,
        origin_departure_time=origin_departure_time,
        destination=destination,
        destination_departure_time=destination_departure_time,
        destination_station_code=destination_station_code,
        return_option=return_option,
        travel_days=travel_days,
        search_limit_days=search_limit_days)

    train_logging(ip=ip,
                  origin_station_code=origin_station_code,
                  origin_departure_time=origin_departure_time,
                  destination_station_code=destination_station_code,
                  destination_departure_time=destination_departure_time,
                  return_option=return_option,
                  travel_days=travel_days,
                  search_limit_days=search_limit_days)

    return render_template('result.html',
                           origin=origin,
                           destination=destination,
                           list_of_tickets=list_of_tickets,
                           destination_offers=destination_offers)


if __name__ == '__main__':
    application.run()
