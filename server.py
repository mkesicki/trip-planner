import json

from flask import Flask, render_template, request
from country_list import countries_for_language
from model.TransportFactory import TransportFactory

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

    # handle start trip transport
    settings = config[transportStart]
    toCity = places[0]

    message = """Searching {type} from {fromCity} in {fromCountry} to {toCity} in {toCountry}. Bettween {startDate} and {endDate}""".format(fromCity = fromCity, fromCountry = countries.get(fromCountry), toCity = toCity, toCountry = countries.get(toCountry), startDate = startDate, endDate = endDate, type = transportStart)
    print(message)

    for params in settings:

        transport = TransportFactory().createTransport(transportStart[:-1],fromCity = fromCity, fromCountry = fromCountry, toCity = toCity, toCountry = toCountry, roundTrip = roundtrip, startDate = startDate, endDate = endDate, adults = adults, params = params)
        transport.search()

    # traveling by plane
#     if (transportStart == "Plane"):

#         toCity = places[0]


#         searchFlight(fromCity = fromCity, fromCountry = fromCountry, toCity = toCity, toCountry = toCountry, roundTrip = roundtrip, startDate = startDate, endDate = endDate, adults = adults, flights = config["flights"])

#     # handel train

#     #handle car
#     if (transportStart == "Car"):
# # http://localhost:5000/planner?start=2023-09-20T10%3A00&end=2023-10-01T10%3A00&roundtrip=on&adults=1&transportStart=Car&transportEnd=Train&fromCity=Barcelona&fromCountry=ES&toCountry=ES&days=12&nights=11&places%5B%5D=Granada&nights%5B%5D=11&submit=Search
#         toCity = places[0]
#         searchCar(fromCity = fromCity, fromCountry = fromCountry, toCity = toCity, toCountry = toCountry, roundTrip = roundtrip, startDate = startDate, endDate = endDate, adults = adults, cars = config["cars"])





    if (roundtrip == "on"):
        return render_template('planner.html')

    # handle back trip
    print("Handle back trip")

    # if (transportEnd == "Plane"):

        # traveling by plane
        # if (transportEnd == "Plane"):

            # reverse places
            # searchFlight(fromCity = places[-1], fromCountry = toCountry, toCity = fromCity, toCountry = fromCountry, roundTrip = "off", startDate = endDate, endDate = endDate, adults = adults, flights = config["flights"])

    # Add case for roadtrip ??

    return render_template('planner.html')

if __name__ == "__main__":
    app.run(debug=True)