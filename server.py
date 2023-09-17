import json

from flask import Flask, render_template, request
from country_list import countries_for_language
from planes import *

countries = dict(countries_for_language('en'))

app = Flask(__name__)

@app.route("/")
def start():
       return render_template('index.html', countries = countries)

@app.route("/planner", methods=['GET'])

def planner():

    args = request.args

    fromCountry = args['fromCountry']
    toCountry = args['toCountry']
    startDate = args['start']
    endDate = args['end']

    if 'roundtrip' in args:
        roundtrip = args['roundtrip']
    else:
        roundtrip = "off"

    transportStart = args['transportStart']
    transportEnd = args['transportEnd']
    fromCity = args['fromCity']
    places = args.getlist('places[]')
    nights = args.getlist('nights[]')
    adults = args['adults']

    #Read config file
    f = open("static/configs/config-" + fromCountry.lower() + ".json", "r")
    config = json.loads(f.read())
    f.close()

    # traveling by plane
    if (transportStart == "Plane"):

        toCity = places[0]
        searchFlight(fromCity = fromCity, fromCountry = fromCountry, toCity = toCity, toCountry = toCountry, roundTrip = roundtrip, startDate = startDate, endDate = endDate, adults = adults, flights = config["flights"])

    # handel train

    #handle car


    if (roundtrip == "on"):
        return render_template('planner.html')

    # handle back trip
    print("Handle back trip")

    if (transportEnd == "Plane"):

        # traveling by plane
        if (transportEnd == "Plane"):

            # reverse places
            searchFlight(fromCity = places[-1], fromCountry = toCountry, toCity = fromCity, toCountry = fromCountry, roundTrip = "off", startDate = endDate, endDate = endDate, adults = adults, flights = config["flights"])

    # Add case for roadtrip ??

    return render_template('planner.html')

if __name__ == "__main__":
    app.run(debug=True)