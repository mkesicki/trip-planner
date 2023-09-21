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

        timeStart = startDate.strftime("%H")
        timeEnd = endDate.strftime("%H")

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
        browser.implicitly_wait(10) # seconds
        browser.find_element(By.CLASS_NAME, "autocomplete-DWN").click() #click first "city" option

        time.sleep(3)

        commanDateFrom = "document.getElementById('{dateFrom}').value='{date}';".format(dateFrom = config.get("dateFrom"), date = startTrip)
        commandDateBack = "document.getElementById('{dateBack}').value='{date}';".format(dateBack = config.get("dateBack"), date =  endTrip)
        browser.execute_script(commanDateFrom)
        browser.execute_script(commandDateBack)

        time.sleep(2)

        command1 = """document.getElementById("horarecogida").value="{timeStart}";""".format(timeStart = timeStart)
        command2 = """document.getElementById("minutosrecogida").value="00";"""
        command3 = """document.getElementById("horadevolucion").value="{timeEnd}";""".format(timeEnd = timeEnd)
        command4 = """document.getElementById("minutosdevolucion").value="00";"""
        browser.execute_script(command1)
        browser.execute_script(command2)
        browser.execute_script(command3)
        browser.execute_script(command4)

        time.sleep(2)

        if roundTrip != "on":
            print("Handle one way trip")
            browser.find_element(By.ID, config.get("oneWay")).click()
            arrival = browser.find_element(By.ID, config.get("arrival"))
            arrival.send_keys(toCity)
            browser.implicitly_wait(5) # seconds
            browser.find_element(By.CSS_SELECTOR, "#devolucion_lista .autocomplete-DWN").click() #click first "city" option

        #submit form
        browser.find_element(By.ID, config.get("submit")).click()

        return ""