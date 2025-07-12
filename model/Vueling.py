import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from .data_classes import SearchQuery

class Vueling:

    def parse(self, query: SearchQuery):
        # they count from 0 -> January is 0
        startMonth = query.start_date.month - 1
        endMonth = query.end_date.month - 1

        startTrip = query.start_date.strftime(query.params.get("dateFormat")).replace("{X}", str(startMonth))
        endTrip = query.end_date.strftime(query.params.get("dateFormat")).replace("{X}", str(endMonth))

        url = query.params.get("url")
        self.config = query.params.get("params")

        logging.info("Open Browser " + url)
        browser = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        browser.get(url)
        browser.implicitly_wait(10)  # seconds

        # accept cookies
        if "cookiesAccept" in self.config:
            browser.find_element(By.ID, self.config.get("cookiesAccept")).click()

        departure = browser.find_element(By.ID, self.config.get("departure"))
        departure.send_keys(query.from_city)
        departure.send_keys(Keys.ENTER)

        browser.implicitly_wait(2)  # seconds

        arrival = browser.find_element(By.ID, self.config.get("arrival"))
        arrival.send_keys(query.to_city)
        arrival.send_keys(Keys.ENTER)

        browser.implicitly_wait(2)  # seconds

        self.findDate(browser, startTrip)

        if not query.round_trip:
            logging.info("Handle one way trip")
            browser.find_element(By.ID, self.config.get("oneWay")).click()
            browser.implicitly_wait(5)  # seconds
            browser.find_element(By.ID, f"calendarDaysTable{startTrip}").click()
        else:
            browser.find_element(By.ID, f"calendarDaysTable{startTrip}").click()
            browser.implicitly_wait(5)  # seconds
            self.findDate(browser, endTrip)
            browser.find_element(By.ID, f"calendarDaysTable{endTrip}").click()

        # handle passengers number
        currentAdults = 1
        while currentAdults < query.adults:
            browser.find_element(By.ID, self.config.get("adults")).click()
            currentAdults += 1

        # submit form
        browser.find_element(By.ID, self.config.get("submit")).click()

        return ""

    def findDate(self, browser, date):
        try:
            browser.find_element(By.ID, f"calendarDaysTable{date}")
            logging.info("Date found !")
            return
        except NoSuchElementException:
            logging.info("search month in calendar")
            browser.find_element(By.ID, self.config.get("dateForward")).click()
            self.findDate(browser, date)
