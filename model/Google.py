import logging
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from .data_classes import SearchQuery

class Google:

    def parse(self, query: SearchQuery):
        url = query.params.get("url")
        config = query.params.get("params")

        startTrip = query.start_date.strftime(query.params.get("dateFormat"))
        endTrip = query.end_date.strftime(query.params.get("dateFormat"))

        logging.info("Open Browser " + url)
        browser = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        browser.get(url)
        browser.implicitly_wait(10)  # seconds

        # accept cookies
        if "cookiesAccept" in config:
            cookiesAccept = browser.find_element(By.XPATH, config.get("cookiesAccept"))
            cookiesAccept.click()

        departure = browser.find_element(By.XPATH, config.get("departure"))
        departure.clear()
        departure.send_keys(query.from_city)
        confirm = browser.find_element(By.CLASS_NAME, config.get("confirmAirportClass"))
        confirm.click()
        time.sleep(1)

        arrival = browser.find_element(By.XPATH, config.get("arrival"))
        arrival.send_keys(query.to_city)
        confirm = browser.find_element(By.CLASS_NAME, config.get("confirmAirportClass"))
        confirm.click()
        time.sleep(1)

        # handle passengers number
        currentAdults = 1
        if query.adults > 1:
            browser.find_element(By.XPATH, config.get("adultsInit")).click()
            time.sleep(2)

        while currentAdults < query.adults:
            browser.find_element(By.XPATH, config.get("adults")).click()
            currentAdults += 1

        if query.adults > 1:
            browser.find_element(By.XPATH, config.get("adultsConfirm")).click()

        time.sleep(2)

        if not query.round_trip:
            logging.info("Handle one way trip")
            browser.find_element(By.XPATH, config.get("oneWayInit")).click()
            browser.find_element(By.XPATH, config.get("oneWay")).click()
            dateFrom = browser.find_element(By.XPATH, config.get("dateFrom"))
            dateFrom.send_keys(startTrip)
            dateFrom.send_keys(Keys.ENTER)
        else:
            dateFrom = browser.find_element(By.XPATH, config.get("dateFrom"))
            dateFrom.send_keys(startTrip)
            dateBack = browser.find_element(By.XPATH, config.get("dateBack"))
            dateBack.send_keys(endTrip)
            dateBack.send_keys(Keys.ENTER)

        # submit form
        time.sleep(2)
        browser.find_element(By.XPATH, config.get("submit")).click()

        return ""
