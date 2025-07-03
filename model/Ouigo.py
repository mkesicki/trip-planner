import logging
import time
import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from .data_classes import SearchQuery

class Ouigo:

    def parse(self, query: SearchQuery):
        startTrip = query.start_date.strftime(query.params.get("dateFormat"))
        endTrip = query.end_date.strftime(query.params.get("dateFormat"))
        config = query.params.get("params")

        browser = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        browser.get(query.params.get("url"))
        time.sleep(2)

        # accept cookies
        if "cookiesAccept" in config:
            cookiesAccept = browser.find_element(By.ID, config.get("cookiesAccept"))
            cookiesAccept.click()

        time.sleep(2)

        # switch to iframe
        frames = browser.find_elements(By.TAG_NAME, "iframe")
        browser.switch_to.frame(frames[1])

        browser.find_element(By.ID, config.get("departure")).click()
        stations = browser.find_elements(By.CSS_SELECTOR, "#origin-station-input-listbox li")
        self.findStation(query.from_city, stations, browser)

        browser.find_element(By.ID, config.get("arrival")).click()
        stations = browser.find_elements(By.CSS_SELECTOR, "#destination-station-input-listbox li")
        self.findStation(query.to_city, stations, browser)

        command = f"document.getElementById('{config.get('dateFrom')}').removeAttribute('readonly');"
        browser.execute_script(command)

        startDate = browser.find_element(By.ID, config.get("dateFrom"))
        startDate.send_keys(Keys.ESCAPE)
        startDate.send_keys(Keys.CONTROL + "a")
        startDate.send_keys(startTrip)
        startDate.send_keys(Keys.ESCAPE)

        if query.round_trip:
            command = f"document.getElementById('{config.get('dateBack')}').removeAttribute('readonly');"
            browser.execute_script(command)

            endDate = browser.find_element(By.ID, config.get("dateBack"))
            endDate.send_keys(Keys.ESCAPE)
            endDate.send_keys(Keys.CONTROL + "a")
            endDate.send_keys(endTrip)
            endDate.send_keys(Keys.ESCAPE)

        if query.adults > 1:
            browser.find_element(By.XPATH, "/html/body/div[1]/div/form/div[3]/div[1]/div/div/button").click()

        time.sleep(2)
        currentAdults = 1
        while currentAdults < query.adults:
            logging.info("Add passenger")
            command = f"document.querySelector('#{config.get('adults')}').click();"
            browser.execute_script(command)
            currentAdults += 1
            if currentAdults == query.adults:
                # close passengers modal
                browser.find_element(By.XPATH, "/html/body/div[1]/div/form/div[3]/div[1]/div/div/button").click()

        # submit form
        browser.find_element(By.XPATH, config.get("submit")).click()

        return ""

    def findStation(self, city, stations, browser):
        for station in stations:
            if city.lower() in station.text.lower():
                station.click()
                return station
        logging.info(f"Station for {city} not found!")
        return ""