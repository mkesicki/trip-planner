import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from .data_classes import SearchQuery

class Vueling:

    def parse(self, query: SearchQuery):
        startTrip = query.start_date.strftime(query.params.get("dateFormat"))
        endTrip = query.end_date.strftime(query.params.get("dateFormat"))

        url = query.params.get("url")
        self.config = query.params.get("params")

        logging.info("Open Browser " + url)
        browser = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        browser.get(url)
        time.sleep(10)

        # accept cookies
        if "cookiesAccept" in self.config:
            button = browser.find_element(By.ID, self.config.get("cookiesAccept"))
            browser.execute_script("arguments[0].click();", button)

        departure = browser.find_element(By.ID, self.config.get("departure"))
        departure.send_keys(query.from_city)
        confirm = browser.find_element(By.CLASS_NAME, "vy-list-dropdown_item_button")
        browser.execute_script("arguments[0].click();", confirm)
        time.sleep(2)

        arrival = browser.find_element(By.ID, self.config.get("arrival"))
        arrival.send_keys(query.to_city)
        confirm = browser.find_element(By.CLASS_NAME, "vy-list-dropdown_item_button")
        browser.execute_script("arguments[0].click();", confirm)
        time.sleep(2)

        startTrip_input = browser.find_element(By.ID, self.config.get("dateFrom"))
        browser.execute_script(f"arguments[0].value = '{startTrip}';", startTrip_input)

        if query.round_trip:
            endTrip_input = browser.find_element(By.ID, self.config.get("dateBack"))
            browser.execute_script(f"arguments[0].value = '{endTrip}';", endTrip_input)
        else:
            logging.info("Handle one way trip")
            browser.find_element(By.CLASS_NAME, self.config.get("oneWay")).click()


        # handle passengers number
        passengers_input = browser.find_element(By.ID, self.config.get("passengersSelector"))
        browser.execute_script("arguments[0].click();", passengers_input)
        time.sleep(2)
        currentAdults = 1
        while currentAdults < query.adults:
            browser.find_element(By.ID, self.config.get("adults")).click()
            currentAdults += 1

        # submit form
        browser.find_element(By.ID, self.config.get("submit")).click()

        return ""


