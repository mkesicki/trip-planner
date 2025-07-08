import logging
import re
import time
import requests
import json
from playwright.sync_api import sync_playwright
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

            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(query.params.get("url"))
            page.wait_for_load_state('load', timeout=5000)

            # accept cookies
            if "cookiesAccept" in config:
                page.click(f"#{config.get('cookiesAccept')}")

            # Execute JavaScript to fill the form, mimicking the Selenium implementation
            page.evaluate(f"document.querySelector(\"input[name='{config.get('adults')}']\").value='{query.adults}';")
            page.evaluate(f"document.querySelector(\"input[name='{config.get('departure')}']\").value='{departureCode.get('clave')}';")
            page.evaluate(f"document.querySelector(\"input[name='{config.get('arrival')}']\").value='{arrivalCode.get('clave')}';")
            page.evaluate(f"document.querySelector(\"input[name='{config.get('dateFrom')}']\").value='{startTrip}';")

            if query.round_trip:
                logging.info("Set date back for roundtrip")
                page.evaluate(f"document.querySelector(\"input[name='{config.get('dateBack')}']\").value='{endTrip}';")
            else:
                logging.info("Set only to one way trip")
                page.evaluate("document.querySelector('button.rf-select__list-text:first-child').click();")

            page.evaluate("document.querySelector('form').submit();")
            page.wait_for_load_state('networkidle', timeout=30000)

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
