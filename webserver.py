from flask import Flask, Response, render_template, request, url_for, flash, redirect # noqa
from config import Config
from parse import launcher
from ticket import flask_logging
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
    destination = request.form.get('destination')
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
        destination=destination,
        destination_station_code=destination_station_code,
        return_option=return_option,
        weekends_only=weekends_only,
        search_limit_days=search_limit_days)

    flask_logging(ip=ip,
                  origin_station_code=origin_station_code,
                  destination_station_code=destination_station_code,
                  return_option=return_option,
                  weekends_only=weekends_only,
                  search_limit_days=search_limit_days)

    return render_template('result.html',
                           origin=origin,
                           destination=destination,
                           list_of_tickets=list_of_tickets)


if __name__ == '__main__':
    application.run()
