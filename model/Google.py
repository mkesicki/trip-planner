import time
import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class Google:

    def parse(self, fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : datetime.date, endDate : datetime.date, adults : int, params : dict):

        url = params.get("url")
        config = params.get("params")

        startTrip = startDate.strftime(params.get("dateFormat"))
        endTrip = endDate.strftime(params.get("dateFormat"))

        print("Open Browser " + url)
        browser = webdriver.Firefox()
        browser.get(url)
        browser.implicitly_wait(10) # seconds

        # accept cookies
        if "cookiesAccept" in config:
            cookiesAccept = browser.find_element(By.XPATH, config.get("cookiesAccept"))
            cookiesAccept.click()

        departure = browser.find_element(By.XPATH, config.get("departure"))
        departure.clear()
        departure.send_keys(fromCity)
        confirm = browser.find_element(By.CLASS_NAME, config.get("confirmAirportClass"))
        confirm.click()
        time.sleep(1)

        arrival = browser.find_element(By.XPATH, config.get("arrival"))
        arrival.send_keys(toCity)
        confirm = browser.find_element(By.CLASS_NAME, config.get("confirmAirportClass"))
        confirm.click()
        time.sleep(1)

        # handle passengers number
        currentAdults = 1
        browser.find_element(By.XPATH, config.get("adultsInit")).click()
        time.sleep(2)

        while currentAdults < int(adults):

            browser.find_element(By.XPATH, config.get("adults")).click()
            currentAdults = currentAdults + 1

        if int(adults) > 1:
            browser.find_element(By.XPATH, config.get("adultsConfirm")).click()

        time.sleep(2)

        if roundTrip != True:
            print("Handle one way trip")
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

        #submit form
        time.sleep(2)
        browser.find_element(By.XPATH, config.get("submit")).click()

        return ""