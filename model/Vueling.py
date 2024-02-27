import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

class Vueling:

    def parse(self, fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : datetime.date, endDate : datetime.date, adults : int, params : dict):

        # they count from 0 -> January is 0
        startMonth = startDate.month - 1
        endMonth = endDate.month - 1

        startTrip = startDate.strftime(params.get("dateFormat"))
        endTrip = endDate.strftime(params.get("dateFormat"))
        startTrip = startTrip.replace("{X}", str(startMonth))
        endTrip = endTrip.replace("{X}", str(endMonth))

        url = params.get("url")
        self.config= params.get("params")

        print("Open Browser " + url)
        browser = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        browser.get(url)
        browser.implicitly_wait(10) # seconds

        # accept cookies
        if "cookiesAccept" in self.config:
            browser.find_element(By.ID, self.config.get("cookiesAccept")).click()

        departure = browser.find_element(By.ID, self.config.get("departure"))
        departure.send_keys(fromCity)
        departure.send_keys(Keys.ENTER)

        browser.implicitly_wait(2) # seconds

        arrival = browser.find_element(By.ID, self.config.get("arrival"))
        arrival.send_keys(toCity)
        arrival.send_keys(Keys.ENTER)

        browser.implicitly_wait(2) # seconds

        self.findDate(browser, startTrip)

        if roundTrip != True:
            print("Handle one way trip")
            browser.find_element(By.ID, self.config.get("oneWay")).click()
            browser.implicitly_wait(5) # seconds
            browser.find_element(By.ID, "calendarDaysTable" + startTrip).click()
        else:
            browser.find_element(By.ID, "calendarDaysTable" + startTrip).click()
            browser.implicitly_wait(5) # seconds
            self.findDate(browser, endTrip)
            browser.find_element(By.ID, "calendarDaysTable" + endTrip).click()

        # handle passengers number
        currentAdults = 1

        while currentAdults < int(adults):
            browser.find_element(By.ID, self.config.get("adults")).click()
            currentAdults = currentAdults + 1

        #submit form
        browser.find_element(By.ID, self.config.get("submit")).click()

        return ""

    def findDate(self, browser, date):

        try:
            date = browser.find_element(By.ID, "calendarDaysTable" + date)
            print("Date found !")
            return

        except NoSuchElementException as e:
            print("search month in calendar")
            browser.find_element(By.ID, self.config.get("dateForward")).click()
            self.findDate(browser, date)
