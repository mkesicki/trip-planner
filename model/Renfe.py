import re
import time
import datetime
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

class Renfe:

    def parse(self, fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : datetime.date, endDate : datetime.date, adults : int, params : dict):

        startTrip = startDate.strftime(params.get("dateFormat"))
        endTrip = endDate.strftime(params.get("dateFormat"))

        config = params.get("params")

        estaciones = requests.get("https://www.renfe.com/content/dam/renfe/es/General/buscadores/javascript/estacionesEstaticas.js")

        pattern = r'var estacionesEstatico=(.+);'
        match = re.search(pattern, estaciones.text)

        if match:
            estaciones = match.group(1)

        stations = json.loads(estaciones)

        departureCode = self.findStation(fromCity, stations, True)
        arrivalCode = self.findStation(toCity, stations, True)

        browser = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        browser.get(params.get("url"))
        time.sleep(5)

        # accept cookies
        if "cookiesAccept" in config:
            cookiesAccept = browser.find_element(By.ID, config.get("cookiesAccept"))
            cookiesAccept.click()

        command = "document.querySelector('.rf-search__filters').style.display='block';"
        browser.execute_script(command)

        command = "document.querySelector(\"input[name='" + config.get("adults") + "']\").value='" + str(adults) + "';"
        browser.execute_script(command)

        command = "document.querySelector(\"input[name='" + config.get("departure") + "']\").value='" + departureCode.get("clave") + "';"
        browser.execute_script(command)

        command = "document.querySelector(\"input[name='" + config.get("arrival") + "']\").value='" + arrivalCode.get("clave") + "';"
        browser.execute_script(command)

        command = "document.querySelector(\"input[name='" + config.get("dateFrom") + "']\").value='" + startTrip + "';"
        browser.execute_script(command)

        print("roundTrip: " + str(roundTrip))

        if roundTrip == True:

            print("Set date back for roundtrip")
            command = "document.querySelector(\"input[name='" + config.get("dateBack") + "']\").value='" + endTrip + "';"
            browser.execute_script(command)

        else :
            print("Set only to one way trip")
            command = "document.querySelector('button.rf-select__list-text:first-child').click();"
            browser.execute_script(command)

        command = "document.querySelector('form').submit();"
        browser.execute_script(command)

        return ""

    def findStation(self, city, stations :dict, strict :bool = False) -> str:

        result = ""

        for station in stations:

            if strict == False and station.get("desgEstacion").lower() == city.lower() + " (todas)":
                result = station
                break
            elif result == "" and strict == False and station.get("desgEstacion").lower() == city.lower() + "-":
                result = station
                break
            elif strict == True and city.lower() in station.get("desgEstacion").lower():
                result = station
                break

        if strict == True and result == "":
            result = self.findStation(city, stations, False)

        return result







