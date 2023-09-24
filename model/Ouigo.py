import time
import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class Ouigo:

    def parse(self, fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : datetime.date, endDate : datetime.date, adults : int, params : dict):

        startTrip = startDate.strftime(params.get("dateFormat"))
        endTrip = endDate.strftime(params.get("dateFormat"))

        config = params.get("params")

        browser = webdriver.Firefox()
        browser.get(params.get("url"))
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
        self.findStation(fromCity, stations, browser)

        browser.find_element(By.ID, config.get("arrival")).click()
        stations = browser.find_elements(By.CSS_SELECTOR, "#destination-station-input-listbox li")
        self.findStation(toCity, stations, browser)

        command = "document.getElementById('" + config.get("dateFrom") + "').removeAttribute('readonly');"
        browser.execute_script(command)

        startDate = browser.find_element(By.ID, config.get("dateFrom"))
        startDate.send_keys(Keys.ESCAPE)
        startDate.send_keys(Keys.CONTROL + "a")
        startDate.send_keys(startTrip)
        startDate.send_keys(Keys.ESCAPE)

        if roundTrip == True:

            command = "document.getElementById('" + config.get("dateBack") + "').removeAttribute('readonly');"
            browser.execute_script(command)

            endDate = browser.find_element(By.ID, config.get("dateBack"))
            endDate.send_keys(Keys.ESCAPE)
            endDate.send_keys(Keys.CONTROL + "a")
            endDate.send_keys(endTrip)
            endDate.send_keys(Keys.ESCAPE)

        if int(adults) > 1:
            browser.find_element(By.XPATH,"/html/body/div[1]/div/form/div[3]/div[1]/div/div/button").click()

        time.sleep(2)
        currentAdults = 1

        while currentAdults < int(adults):
            print("Add passenger")
            command = "document.querySelector('#" + config.get("adults") + "').click();"
            browser.execute_script(command)

            currentAdults = currentAdults + 1

            if currentAdults == int(adults):
                # close passengers modal
                browser.find_element(By.XPATH,"/html/body/div[1]/div/form/div[3]/div[1]/div/div/button").click()

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







