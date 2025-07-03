import logging
import re
import time
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from .data_classes import SearchQuery

class Renfe:
    def parse(self, query: SearchQuery):
        startTrip = query.start_date.strftime(query.params.get("dateFormat"))
        endTrip = query.end_date.strftime(query.params.get("dateFormat"))
        config = query.params.get("params")

        estaciones_req = requests.get("https://www.renfe.com/content/dam/renfe/es/General/buscadores/javascript/estacionesEstaticas.js")
        pattern = r'var estacionesEstatico=(.+);'
        match = re.search(pattern, estaciones_req.text)

        if match:
            estaciones_json = match.group(1)
            stations = json.loads(estaciones_json)
            departureCode = self.findStation(query.from_city, stations, True)
            arrivalCode = self.findStation(query.to_city, stations, True)

            browser = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
            browser.get(query.params.get("url"))
            time.sleep(5)

            # accept cookies
            if "cookiesAccept" in config:
                cookiesAccept = browser.find_element(By.ID, config.get("cookiesAccept"))
                cookiesAccept.click()

            command = "document.querySelector('.rf-search__filters').style.display='block';"
            browser.execute_script(command)

            command = f"document.querySelector(\"input[name='{config.get('adults')}']\").value='{query.adults}';"
            browser.execute_script(command)

            command = f"document.querySelector(\"input[name='{config.get('departure')}']\").value='{departureCode.get('clave')}';"
            browser.execute_script(command)

            command = f"document.querySelector(\"input[name='{config.get('arrival')}']\").value='{arrivalCode.get('clave')}';"
            browser.execute_script(command)

            command = f"document.querySelector(\"input[name='{config.get('dateFrom')}']\").value='{startTrip}';"
            browser.execute_script(command)

            if query.round_trip:
                logging.info("Set date back for roundtrip")
                command = f"document.querySelector(\"input[name='{config.get('dateBack')}']\").value='{endTrip}';"
                browser.execute_script(command)
            else:
                logging.info("Set only to one way trip")
                command = "document.querySelector('button.rf-select__list-text:first-child').click();"
                browser.execute_script(command)

            command = "document.querySelector('form').submit();"
            browser.execute_script(command)

    def findStation(self, city, stations: dict, strict: bool = False) -> dict:
        result = {}
        for station in stations:
            desgEstacion_lower = station.get("desgEstacion", "").lower()
            city_lower = city.lower()
            if not strict and desgEstacion_lower == f"{city_lower} (todas)":
                result = station
                break
            elif not result and not strict and desgEstacion_lower == f"{city_lower}-":
                result = station
                break
            elif strict and city_lower in desgEstacion_lower:
                result = station
                break
        if strict and not result:
            result = self.findStation(city, stations, False)
        return result
