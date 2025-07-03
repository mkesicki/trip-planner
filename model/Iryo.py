import time
import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from .data_classes import SearchQuery

class Iryo:

    def parse(self, query: SearchQuery):
        startTrip = query.start_date.strftime(query.params.get("dateFormat"))
        endTrip = query.end_date.strftime(query.params.get("dateFormat"))
        config = query.params.get("params")

        browser = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        browser.get(query.params.get("url"))
        time.sleep(2)

        # accept cookies
        if "cookiesAccept" in config:
            cookiesAccept = browser.find_element(By.XPATH, config.get("cookiesAccept"))
            cookiesAccept.click()

        time.sleep(2)

        browser.find_element(By.XPATH, config.get("departure")).click()
        stations = browser.find_elements(By.CSS_SELECTOR, ".menu__item span")
        self.findStation(query.from_city, stations, browser)

        time.sleep(2)

        browser.find_element(By.XPATH, config.get("arrival")).click()
        stations = browser.find_elements(By.CSS_SELECTOR, ".menu__item span")
        self.findStation(query.to_city, stations, browser)

        startDate = browser.find_element(By.XPATH, config.get("dateFrom"))
        startDate.clear()
        startDate.send_keys(startTrip)
        startDate.send_keys(Keys.ENTER)

        if query.round_trip:
            endDate = browser.find_element(By.XPATH, config.get("dateBack"))
            endDate.clear()
            endDate.send_keys(endTrip)
            endDate.send_keys(Keys.ENTER)
        else:
            browser.find_element(By.XPATH, config.get("oneWay")).click()

        if query.adults > 1:
            browser.find_element(By.XPATH, "/html/body/app-root/main/b2c-view-home/div[2]/section/div/div[1]/b2c-main-search/ilsa-main-search/div/div[2]/ilsa-passengers-picker/div/div[1]").click()

        time.sleep(2)
        currentAdults = 1
        while currentAdults < query.adults:
            print("Add passenger")
            browser.find_element(By.XPATH, config.get("adults")).click()
            currentAdults += 1
            if currentAdults == query.adults:
                # close passengers modal
                browser.find_element(By.XPATH, "/html/body/app-root/main/b2c-view-home/div[2]/section/div/div[1]/b2c-main-search/ilsa-main-search/div/div[2]/ilsa-passengers-picker/div/div[1]").click()

        # submit form
        browser.find_element(By.XPATH, config.get("submit")).click()

        return ""

    def findStation(self, city, stations, browser):
        for station in stations:
            if city.lower() in station.text.lower():
                station.click()
                return station
        print(f"Station for {city} not found!")
        return ""







