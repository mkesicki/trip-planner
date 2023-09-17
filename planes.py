
import datetime
import airportsdata
import webbrowser
import importlib.util

from country_list import countries_for_language

def searchFlight(fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : str, endDate : str, adults : int, flights : list) -> str:

    # print(flights)
    countries = dict(countries_for_language('en'))

    message = """Searching flights from {fromCity} in {fromCountry} to {toCity} in {toCountry}. Bettween {startDate} and {endDate}""".format(fromCity = fromCity, fromCountry = countries.get(fromCountry), toCity = toCity, toCountry = countries.get(toCountry), startDate = startDate, endDate = endDate)
    print(message)

    start = datetime.datetime.strptime(startDate,"%Y-%m-%dT%H:%M")
    end = datetime.datetime.strptime(endDate,"%Y-%m-%dT%H:%M")

    for flight in flights:

        if flight.get("type") == "browser":

            url =  flight.get("url") if (roundTrip == "on") else  flight.get("urlOneWay")
            startFlight = start.strftime(flight.get("dateFormat"))
            endFlight = end.strftime(flight.get("dateFormat"))

            fromAirportCode = findAirportCode(fromCountry, fromCity, flight.get("airportCode"))
            toAirportCode = findAirportCode(toCountry, toCity, flight.get("airportCode"))

            print(fromAirportCode)
            print(toAirportCode)
            print(startFlight)
            print(endFlight)

            url = url + flight.get("queryParams")
            url = url.format(departure = fromAirportCode, arrival = toAirportCode, dateFrom = startFlight, dateBack = endFlight, adults = adults)

            print("url: " + url)

            webbrowser.open(url)

        elif flight.get("type") == "parseWeb":

            company = flight.get("company")

            print("Parse: " + company)

            # classes and all that jazz ?
            if importlib.util.find_spec("flights."+company.lower(),"./flights/" + company.lower() +".py") is not None:
                module = importlib.import_module("flights."+company.lower(),"./flights/" + company.lower() +".py")
                getattr(module, "parse" + company)(fromCity, fromCountry, toCity, toCountry, roundTrip, startDate, endDate, adults, flight)

    return ""

def findAirportCode( country : str, city : str, type : str = "IATA") -> str:

    airports = airportsdata.load(type)

    for code, airport in airports.items():

        if (airport.get("city") == city and airport.get("country") == country):
            return code

    return ""