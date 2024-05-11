import os
import json
import datetime
import time
import sys

from pathlib import Path
from flask import Flask , render_template, request
from country_list import countries_for_language
from model.Parser import Parser

countries = dict(countries_for_language('en'))

app = Flask(__name__)

@app.route("/")
def start():
       return render_template('index.html', countries = countries)

@app.route("/planner", methods=['GET'])

def planner():

    args = request.args

    fromCountry = args['fromCountry']
    startDate = args['start']
    endDate = args['end']
    backTime = args['backTime']
    tripCountries = args.getlist("countries[]")

    toCountry = tripCountries[-1]

    if 'roundtrip' in args:
        roundtrip = args['roundtrip']
    else:
        roundtrip = "off"

    if 'hotelsOnly' in args:
        hotelsOnly = args['hotelsOnly']
    else:
        hotelsOnly = "off"

    if 'transportOnly' in args:
        transportOnly = args['transportOnly']
    else:
        transportOnly = "off"

    transportStart = args['transportStart']
    transportEnd = args['transportEnd']
    fromCity = args['fromCity']
    places = args.getlist('places[]')
    nights = args.getlist('nights[]')
    adults = args['adults']

    if transportStart == "cars":
        pickupPlace = args['pickupPlace']

    if transportEnd == "cars":
        returnPlace = args['returnPlace']

    if roundtrip == "on":
        returnPlace = pickupPlace

    basePath = Path(os.getcwd())
    filePath = basePath  / "static" / "configs" / ("config-" + fromCountry.lower() + ".json")

    #Read config files
    configLocal = {}
    if filePath.is_file():
         with filePath.open('r+') as fp:
          configLocal = json.loads(fp.read())

    path = basePath / "static" / "configs" / "config.json"
    with path.open('r+') as fp:
        configMain = json.loads(fp.read())

    config = {
        "cars": configMain["cars"] + configLocal["cars"],
        "flights": configMain["flights"] + configLocal["flights"],
        "trains": configMain["trains"] + configLocal["trains"],
        "hotels": configMain["hotels"] + configLocal["hotels"]
    }

    # handle start trip transport
    settings = config[transportStart]
    toCity = places[0]

    if hotelsOnly != "on":
        message = """Searching {type} from {fromCity} in {fromCountry} to {toCity} in {toCountry}. Bettween {startDate} and {endDate}""".format(fromCity = fromCity, fromCountry = countries.get(fromCountry), toCity = toCity, toCountry = countries.get(toCountry), startDate = startDate, endDate = endDate, type = transportStart)
        print(message)

        for params in settings:

            transport = Parser(fromCity = fromCity, fromCountry = fromCountry, toCity = toCity, toCountry = toCountry, roundTrip = roundtrip, startDate = startDate, endDate = endDate, adults = adults, params = params, pickupPlace = pickupPlace, returnPlace = returnPlace)
            transport.search()

        if (roundtrip != "on"):
            # handle back trip
            print("Handle back trip")

            settings = config[transportEnd]

            for params in settings:
                # reverse places and dates
                newEndDate = endDate[:10] +"T" + backTime

                transport = Parser(fromCity = places[-1], fromCountry = toCountry, toCity = fromCity, toCountry = fromCountry, roundTrip = "off", startDate = endDate, endDate = newEndDate, adults = adults, params = params, pickupPlace = returnPlace, returnPlace = pickupPlace)
                transport.search()

    if transportOnly != "on":

        print("Search hotels!")
        settings = config["hotels"]

        for params in settings:

            hotelCheckin = datetime.datetime.strptime(startDate,"%Y-%m-%dT%H:%M")

            for place in places:

                hotelCheckout = hotelCheckin + datetime.timedelta(days=int(nights[places.index(place)]))
                country =  tripCountries[places.index(place)]
                fromCity = ""
                toCity = place

                hotels = Parser(fromCity = fromCity, fromCountry = fromCountry, toCity = toCity, toCountry = countries[country], roundTrip = roundtrip,
                                startDate = hotelCheckin.strftime("%Y-%m-%dT%H:%M"),
                                endDate = hotelCheckout.strftime("%Y-%m-%dT%H:%M"),
                                adults = adults, params = params)
                hotels.search()
                hotelCheckin = hotelCheckout
                time.sleep(3)

    return render_template('planner.html', countries = countries)

if __name__ == "__main__":
    app.run(debug=True)
    # app.run()


# # 127.0.0.1:5000/planner?start=2024-01-01T11%3A00&end=2024-02-01T13%3A00&roundtrip=on&adults=3&transportStart=flights&transportEnd=flight&fromCity=Barcelona&fromCountry=ES&toCountry=ES&days=12&nights=11&places[]=malaga&nights[]=11&submit=Search
# 127.0.0.1:5000/planner?start=2024-01-01T11%3A00&end=2024-02-01T13%3A00&roundtrip=on&adults=3&transportStart=cars&transportEnd=cars&fromCity=Barcelona&fromCountry=ES&toCountry=ES&days=12&nights=11&places[]=malaga&nights[]=11&submit=Search