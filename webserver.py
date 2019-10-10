from flask import Flask, Response, render_template, request, url_for, flash, redirect # noqa
from config import Config
from parse import launcher
from train_logging import train_logging
import json
import csv

application = Flask(__name__)
application.config.from_object(Config)

station_codes = {}

with open('station_codes.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        station_codes[row[1]] = row[0]


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
    weekends_only = request.form.get('weekends_only')
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

    list_of_tickets = launcher(
        origin=origin,
        origin_station_code=origin_station_code,
        origin_departure_time=origin_departure_time,
        destination=destination,
        destination_departure_time=destination_departure_time,
        destination_station_code=destination_station_code,
        return_option=return_option,
        weekends_only=weekends_only,
        search_limit_days=search_limit_days)

    train_logging(ip=ip,
                  origin_station_code=origin_station_code,
                  origin_departure_time=origin_departure_time,
                  destination_station_code=destination_station_code,
                  destination_departure_time=destination_departure_time,
                  return_option=return_option,
                  weekends_only=weekends_only,
                  search_limit_days=search_limit_days)

    return render_template('result.html',
                           origin=origin,
                           destination=destination,
                           list_of_tickets=list_of_tickets)


if __name__ == '__main__':
    application.run()
