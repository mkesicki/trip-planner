import time

from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from model.Plane import Plane

class Vueling(Plane):

    def __init__(self, fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : str, endDate : str, adults : int, params : dict):
        super().__init__(fromCity,fromCountry, toCity, toCountry, roundTrip, startDate, endDate, adults, params)

    def parse(self):

        # they count from 0 -> January is 0
        self.start = self.start - relativedelta(months=1)
        self.end = self.end - relativedelta(months=1)

        self.startFlight = self.start.strftime(self.params.get("dateFormat"))
        self.endFlight = self.end.strftime(self.params.get("dateFormat"))

        url = self.params.get("url")
        config = self.params.get("params")

        print("Open Browser " + url + " in browser")
        browser = webdriver.Firefox()
        browser.get(url)
        browser.implicitly_wait(10) # seconds

        # accept cookies
        if "cookiesAccept" in config:
            cookiesAccept = browser.find_element(By.ID, config.get("cookiesAccept"))
            cookiesAccept.click()

        departure = browser.find_element(By.ID, config.get("departure"))
        departure.send_keys(self.fromAirportCode)
        departure.send_keys(Keys.ENTER)

        arrival = browser.find_element(By.ID, config.get("arrival"))
        arrival.send_keys(self.toAirportCode)
        arrival.send_keys(Keys.ENTER)

        time.sleep(5)

        if self.roundTrip != "on":
            print("Handle one way trip")
            browser.find_element(By.ID, config.get("oneWay")).click()
            browser.implicitly_wait(5) # seconds
            browser.find_element(By.ID, "calendarDaysTable" + self.startFlight).click()
        else:
            browser.find_element(By.ID, "calendarDaysTable" + self.startFlight).click()
            browser.implicitly_wait(20) # seconds
            browser.find_element(By.ID, "calendarDaysTable" + self.endFlight).click()

        # handle passengers number
        currentAdults = 1

        while currentAdults < int(self.adults):
            browser.find_element(By.ID, config.get("adults")).click()
            currentAdults = currentAdults + 1

        #submit form
        browser.find_element(By.ID, config.get("submit")).click()

        return ""