
import datetime
import airportsdata
import webbrowser

from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from country_list import countries_for_language

def searchFlight(fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : str, endDate : str, adults : int, flights : list) -> str:

    # print(flights)
    countries = dict(countries_for_language('en'))

    message = """Searching flights from {fromCity} in {fromCountry} to {toCity} in {toCountry}. Bettween {startDate} and {endDate}""".format(fromCity = fromCity, fromCountry = countries.get(fromCountry), toCity = toCity, toCountry = countries.get(toCountry), startDate = startDate, endDate = endDate)
    print(message)

    start = datetime.datetime.strptime(startDate,"%Y-%m-%dT%H:%M")
    end = datetime.datetime.strptime(endDate,"%Y-%m-%dT%H:%M")

    # https://www.skyscanner.es/transporte/vuelos/bcn/grx/230920/230930/?adultsv2=1&inboundaltsenabled=false&outboundaltsenabled=false&preferdirects=true&ref=home&rtn=1&stops=!twoPlusStops

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

            #webbrowser.open(url)

        elif flight.get("type") == "parseWeb":

            # classes and all that jazz ?
            if flight.get("company").lower() == "vueling":
                parseVueling(fromCity, fromCountry, toCity, toCountry, roundTrip, startDate, endDate, adults, flight)

    return ""

def findAirportCode( country : str, city : str, type : str = "IATA") -> str:

    airports = airportsdata.load(type)

    for code, airport in airports.items():

        if (airport.get("city") == city and airport.get("country") == country):
            return code

    return ""

def parseVueling(fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : str, endDate : str, adults : int, flight : dict) -> str:

    # convert dates for specific Vueling format
    start = datetime.datetime.strptime(startDate,"%Y-%m-%dT%H:%M")
    end = datetime.datetime.strptime(endDate,"%Y-%m-%dT%H:%M")

    # they count from 0 -> January is 0
    start = start - relativedelta(months=1)
    end = end - relativedelta(months=1)

    startFlight = start.strftime(flight.get("dateFormat"))
    endFlight = end.strftime(flight.get("dateFormat"))

    url = flight.get("url")
    params = flight.get("params")

    fromAirportCode = findAirportCode(fromCountry, fromCity, flight.get("airportCode"))
    toAirportCode = findAirportCode(toCountry, toCity, flight.get("airportCode"))

    print("Open Browser " + url + " in browser")
    browser = webdriver.Firefox()
    browser.get(url)
    browser.implicitly_wait(10) # seconds

    # accept cookies
    if "cookiesAccept" in params:
        cookiesAccept = browser.find_element(By.ID, params.get("cookiesAccept"))
        cookiesAccept.click()

    departure = browser.find_element(By.ID, params.get("departure"))
    departure.send_keys(fromAirportCode)
    departure.send_keys(Keys.ENTER)

    arrival = browser.find_element(By.ID, params.get("arrival"))
    arrival.send_keys(toAirportCode)
    arrival.send_keys(Keys.ENTER)

    if roundTrip != "on":
        print("Handle one way trip")
        browser.find_element(By.ID, params.get("oneWay")).click()
        browser.implicitly_wait(5) # seconds
        browser.find_element(By.ID, "calendarDaysTable" + startFlight).click()
    else:
        browser.find_element(By.ID, "calendarDaysTable" + startFlight).click()
        browser.implicitly_wait(20) # seconds
        browser.find_element(By.ID, "calendarDaysTable" + endFlight).click()

    # handle passengers number
    currentAdults = 1

    while currentAdults < int(adults):
        browser.find_element(By.ID, params.get("adults")).click()
        currentAdults = currentAdults + 1

    #submit form
    browser.find_element(By.ID, params.get("submit")).click()

    return ""