import requests
import datetime
import re
import html

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

class DoYouSpain:

    def parse(self, fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : datetime.date, endDate : datetime.date, adults : int, params : dict):

        startTrip = startDate.strftime(params.get("dateFormat"))
        endTrip = endDate.strftime(params.get("dateFormat"))

        timeStart = startDate.strftime("%H")
        timeEnd = endDate.strftime("%H")

        url = params.get("url")
        config = params.get("params")

        print("Open Browser " + url)
        browser = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        browser.get(url)
        browser.implicitly_wait(10) # seconds

        # accept cookies
        if "cookiesAccept" in config:
            try:
                cookiesAccept = browser.find_element(By.ID, config.get("cookiesAccept"))
                cookiesAccept.click()
            except:
                print("No cookies to accept")
                pass

        location = self.getLocation(fromCity)
        departure = "document.getElementById('destino').value='{code}';".format(code=location["location_id"])
        browser.execute_script(departure)

        departure = "document.getElementById('{id}').value='{value}';".format(id=config.get("departure"),value=location["location_name"])
        browser.execute_script(departure)

        commanDateFrom = "document.getElementById('{dateFrom}').value='{date}';".format(dateFrom = config.get("dateFrom"), date = startTrip)
        commandDateBack = "document.getElementById('{dateBack}').value='{date}';".format(dateBack = config.get("dateBack"), date =  endTrip)
        browser.execute_script(commanDateFrom)
        browser.execute_script(commandDateBack)

        command1 = """document.getElementById("horarecogida").value="{timeStart}";""".format(timeStart = timeStart)
        command2 = """document.getElementById("minutosrecogida").value="00";"""
        command3 = """document.getElementById("horadevolucion").value="{timeEnd}";""".format(timeEnd = timeEnd)
        command4 = """document.getElementById("minutosdevolucion").value="00";"""
        browser.execute_script(command1)
        browser.execute_script(command2)
        browser.execute_script(command3)
        browser.execute_script(command4)

        if roundTrip != True:
            print("Handle one way trip")
            browser.find_element(By.ID, config.get("oneWay")).click()

            location = self.getLocation(toCity)
            arrival = "document.getElementById('destino_final').value='{code}';".format(code=location["location_id"])
            arrival = "document.getElementById('{id}').value='{value}';".format(id=config.get("arrival"),value=location["location_name"])
            browser.execute_script(arrival)

        #submit form
        browser.find_element(By.ID, config.get("submit")).click()

        return ""

    def getLocation(self, city : str) -> str:

        city = city + " train station"
        data = {
            "destino": city,
            "idoma": "es",
            "origien": "DY",
            "experimiento": "[CAR]"
        }

        response = requests.post("https://www.doyouspain.com/do/ajax/autocomplete", data = data)
        print(response)

        location_id = ""
        location_name = ""

        data_value = re.search(r"data-destino='([^']+)'", response.text)

        if data_value:
            location_id = data_value.group(1)

        first_span_text = re.search(r"data-destino-description='([^']+)'", response.text)
        if first_span_text:
            location_name =  html.unescape(first_span_text.group(1))


        results = {
            "location_id": location_id,
            "location_name": location_name
        }

        print(results)

        return results