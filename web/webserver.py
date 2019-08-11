from flask import Flask, flash, redirect, render_template, \
                  request, url_for, jsonify
import csv
from config import Config
from parse import launcher
from forms import LoginForm


application = Flask(__name__)
application.config.from_object(Config)
station_codes = {}


with open('station_codes.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        station_codes[row[1]] = row[0]


@application.route('/')
def home():
    form = LoginForm()
    return render_template(
        'index.html',
        origin_station=station_codes,
        destination_station=station_codes,
		form=form)

@application.route("/result" , methods=['GET', 'POST'])
def result():
    origin = request.form.get('origin_station')
    destination = request.form.get('destination_station')
    same_day_return = request.form.get('same_day_return')
    origin_station_code = [key for key,value in station_codes.items() if value == origin][0]
    destination_station_code = [key for key,value in station_codes.items() if value == destination][0]
    list_of_tickets = launcher(origin_station_code, destination_station_code, same_day_return)

    return render_template('result.html',
                           list_of_tickets=list_of_tickets)

if __name__=='__main__':
     application.run()
