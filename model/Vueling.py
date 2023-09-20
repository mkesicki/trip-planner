import time
import datetime

from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class Vueling:

    def parse(self, fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : datetime.date, endDate : datetime.date, adults : int, params : dict):

        # they count from 0 -> January is 0
        start = startDate - relativedelta(months=1)
        end = endDate - relativedelta(months=1)

        startTrip = start.strftime(params.get("dateFormat"))
        endTrip = end.strftime(params.get("dateFormat"))

        url = params.get("url")
        config = params.get("params")

        print("Open Browser " + url + " in browser")
        browser = webdriver.Firefox()
        browser.get(url)
        browser.implicitly_wait(10) # seconds

        # accept cookies
        if "cookiesAccept" in config:
            browser.find_element(By.ID, config.get("cookiesAccept")).click()

        departure = browser.find_element(By.ID, config.get("departure"))
        departure.send_keys(fromCity)
        departure.send_keys(Keys.ENTER)

        arrival = browser.find_element(By.ID, config.get("arrival"))
        arrival.send_keys(toCity)
        arrival.send_keys(Keys.ENTER)

        time.sleep(5)

        if roundTrip != "on":
            print("Handle one way trip")
            browser.find_element(By.ID, get("oneWay")).click()
            browser.implicitly_wait(5) # seconds
            browser.find_element(By.ID, "calendarDaysTable" + startTrip).click()
        else:
            browser.find_element(By.ID, "calendarDaysTable" + startTrip).click()
            browser.implicitly_wait(20) # seconds
            browser.find_element(By.ID, "calendarDaysTable" + endTrip).click()

        # handle passengers number
        currentAdults = 1

        while currentAdults < int(adults):
            browser.find_element(By.ID, config.get("adults")).click()
            currentAdults = currentAdults + 1

        #submit form
        browser.find_element(By.ID, config.get("submit")).click()

        return ""