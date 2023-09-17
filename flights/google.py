import datetime
import time

from planes import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def parseGoogle(fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : str, endDate : str, adults : int, flight : dict) -> str:

    # convert dates for specific Vueling format
    start = datetime.datetime.strptime(startDate,"%Y-%m-%dT%H:%M")
    end = datetime.datetime.strptime(endDate,"%Y-%m-%dT%H:%M")

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
        cookiesAccept = browser.find_element(By.XPATH, params.get("cookiesAccept"))
        cookiesAccept.click()

    departure = browser.find_element(By.XPATH, params.get("departure"))
    departure.clear()
    departure.send_keys(fromAirportCode)
    confirm = browser.find_element(By.CLASS_NAME, params.get("confirmAirportClass"))
    confirm.click()
    time.sleep(1)

    arrival = browser.find_element(By.XPATH, params.get("arrival"))
    arrival.send_keys(toAirportCode)
    confirm = browser.find_element(By.CLASS_NAME, params.get("confirmAirportClass"))
    confirm.click()
    time.sleep(1)

    # handle passengers number
    currentAdults = 1
    browser.find_element(By.XPATH, params.get("adultsInit")).click()
    time.sleep(2)

    while currentAdults < int(adults):

        browser.find_element(By.XPATH, params.get("adults")).click()
        currentAdults = currentAdults + 1

    if int(adults) > 1:
        browser.find_element(By.XPATH, params.get("adultsConfirm")).click()

    time.sleep(2)

    if roundTrip != "on":
        print("Handle one way trip")
        browser.find_element(By.XPATH, params.get("oneWayInit")).click()
        browser.find_element(By.XPATH, params.get("oneWay")).click()
        dateFrom = browser.find_element(By.XPATH, params.get("dateFrom"))
        dateFrom.send_keys(startFlight)
        dateFrom.send_keys(Keys.ENTER)
    else:
        dateFrom = browser.find_element(By.XPATH, params.get("dateFrom"))
        dateFrom.send_keys(startFlight)
        dateBack = browser.find_element(By.XPATH, params.get("dateBack"))
        dateBack.send_keys(endFlight)
        dateBack.send_keys(Keys.ENTER)

    #submit form
    time.sleep(2)
    browser.find_element(By.XPATH, params.get("submit")).click()

    return ""