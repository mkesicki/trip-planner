import time
import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

class Iryo:

    def parse(self, fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : datetime.date, endDate : datetime.date, adults : int, params : dict):

        startTrip = startDate.strftime(params.get("dateFormat"))
        endTrip = endDate.strftime(params.get("dateFormat"))

        config = params.get("params")

        browser = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        browser.get(params.get("url"))
        time.sleep(2)

        # accept cookies
        if "cookiesAccept" in config:
            cookiesAccept = browser.find_element(By.XPATH, config.get("cookiesAccept"))
            cookiesAccept.click()

        time.sleep(2)

        browser.find_element(By.XPATH, config.get("departure")).click()
        stations = browser.find_elements(By.CSS_SELECTOR, ".menu__item span")
        self.findStation(fromCity, stations, browser)

        time.sleep(2)

        browser.find_element(By.XPATH, config.get("arrival")).click()
        stations = browser.find_elements(By.CSS_SELECTOR, ".menu__item span")
        self.findStation(toCity, stations, browser)

        startDate = browser.find_element(By.XPATH, config.get("dateFrom"))
        startDate.clear()
        startDate.send_keys(startTrip)
        startDate.send_keys(Keys.ENTER)

        if roundTrip == True:
            endDate = browser.find_element(By.XPATH, config.get("dateBack"))
            endDate.clear()
            endDate.send_keys(endTrip)
            endDate.send_keys(Keys.ENTER)

        else:
            browser.find_element(By.XPATH, config.get("oneWay")).click()

        if int(adults) > 1:
            browser.find_element(By.XPATH,"/html/body/app-root/main/b2c-view-home/div[2]/section/div/div[1]/b2c-main-search/ilsa-main-search/div/div[2]/ilsa-passengers-picker/div/div[1]").click()

        time.sleep(2)
        currentAdults = 1

        while currentAdults < int(adults):
            print("Add passenger")
            browser.find_element(By.XPATH,config.get("adults")).click()

            currentAdults = currentAdults + 1

            if currentAdults == int(adults):
                # close passengers modal
                browser.find_element(By.XPATH,"/html/body/app-root/main/b2c-view-home/div[2]/section/div/div[1]/b2c-main-search/ilsa-main-search/div/div[2]/ilsa-passengers-picker/div/div[1]").click()

        #submit form
        browser.find_element(By.XPATH, config.get("submit")).click()

        return ""

    def findStation(self, city, stations, browser):

        for station in stations:
            if city.lower() in station.text.lower():

                station.click()

                return station

        print("Station for " + city + " not found!")
        # command = "alert('Station for " + city + " not found!');"
        # browser.execute_script(command)

        return ""







