import datetime

from planes import *
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

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