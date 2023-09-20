import time
import datetime

from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains

class Doyouspain:

    def parse(self, fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : datetime.date, endDate : datetime.date, adults : int, params : dict):

        startTrip = startDate.strftime(params.get("dateFormat"))
        endTrip = endDate.strftime(params.get("dateFormat"))

        timeStart = startDate.strftime("%H:00")
        timeEnd = endDate.strftime("%H:00")

        url = params.get("url")
        config = params.get("params")

        print("Open Browser " + url + " in browser")
        browser = webdriver.Firefox()
        browser.get(url)
        browser.implicitly_wait(10) # seconds

        # accept cookies
        # if "cookiesAccept" in config:
        #     cookiesAccept = browser.find_element(By.ID, config.get("cookiesAccept"))
        #     cookiesAccept.click()

        departure = browser.find_element(By.ID, config.get("departure"))
        departure.send_keys(fromCity)
        browser.find_element(By.CLASS_NAME, "autocomplete-DWN").click() #click first "city" option

        commanDateFrom = "document.getElementById('{dateFrom}').value='{date}';".format(dateFrom = config.get("dateFrom"), date = startTrip)
        commandDateBack = "document.getElementById('{dateBack}').value='{date}';".format(dateBack = config.get("dateBack"), date=  endTrip)
        browser.execute_script(commanDateFrom)
        browser.execute_script(commandDateBack)

        commandTimeFrom = "document.querySelector(\"#{timeFrom} option[value='{time}']\").selected='selected';".format(timeFrom = config.get("timeFrom"), time = timeStart)
        commandTimeEnd = "document.querySelector(\"#{timeBack} option[value='{time}']\").selected='selected';".format(timeBack = config.get("timeBack"), time = timeEnd)

        browser.implicitly_wait(10) # seconds
        browser.execute_script(commandTimeFrom)
        browser.execute_script(commandTimeEnd)

        if roundTrip != "on":
            print("Handle one way trip")
            browser.find_element(By.ID, config.get("oneWay")).click()
            arrival = browser.find_element(By.ID, config.get("arrival"))
            arrival.send_keys(toCity)
            browser.implicitly_wait(10) # seconds

            browser.find_element(By.CSS_SELECTOR, "#devolucion_lista .autocomplete-DWN").click() #click first "city" option

        #submit form
        browser.find_element(By.ID, config.get("submit")).click()

        return ""