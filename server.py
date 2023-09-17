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
    # print(args)

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
    # print(config)



    # traveling by plane
    if (transportStart == "Plane"):

        toCity = places[0]
        searchFlight(fromCity = fromCity, fromCountry = fromCountry, toCity = toCity, toCountry = toCountry, roundTrip = roundtrip, startDate = startDate, endDate = endDate, adults = adults, flights = config["flights"])

    # handel train

    #handle car


    if (roundtrip == "on"):

        transportEnd = transportStart
        # exit(0)
        return render_template('planner.html')


    # handle back trip
    if (transportEnd == "Plane"):

        print("Handle back trip")

        #  handle plane
          # traveling by plane
        if (transportEnd == "Plane"):

            # reverse places
            searchFlight(fromCity = places[-1], fromCountry = toCountry, toCity = fromCity, toCountry = fromCountry, roundTrip = "off", startDate = endDate, endDate = endDate, adults = adults, flights = config["flights"])

    # Add case for roadtrip ??

#   127.0.0.1:5000/planner?start=2023-09-23T10%3A00&end=2023-10-01T10%3A00&roundtrip=on&adults=3&transportStart=Plane&transportEnd=Train&fromCity=Barcelona&fromCountry=ES&toCountry=ES&days=11&nights=10&places[]=Granada&nights[]=10&submit=Search
# http://127.0.0.1:5000/planner?start=2023-09-23T10%3A00&end=2023-10-01T10%3A00&adults=3&transportStart=Plane&transportEnd=Train&fromCity=Barcelona&fromCountry=ES&toCountry=ES&days=11&nights=10&places[]=Granada&nights[]=10&submit=Search
    return render_template('planner.html')


if __name__ == "__main__":
    app.run(debug=True)