import requests
import datetime
import re
import html

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from .data_classes import SearchQuery

class DoYouSpain:

    def parse(self, query: SearchQuery):
        startTrip = query.start_date.strftime(query.params.get("dateFormat"))
        endTrip = query.end_date.strftime(query.params.get("dateFormat"))

        timeStart = query.start_date.strftime("%H")
        timeEnd = query.end_date.strftime("%H")

        url = query.params.get("url")
        config = query.params.get("params")

        print("Open Browser " + url)
        browser = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        browser.get(url)
        browser.implicitly_wait(10)  # seconds

        # accept cookies
        if "cookiesAccept" in config:
            try:
                cookiesAccept = browser.find_element(By.ID, config.get("cookiesAccept"))
                cookiesAccept.click()
            except:
                print("No cookies to accept")
                pass

        location = self.getLocation(query.from_city, query.pickup_place)
        departure = f"document.getElementById('destino').value='{location['location_id']}';"
        browser.execute_script(departure)

        departure = f"document.getElementById('{config.get('departure')}').value='{location['location_name']}';"
        browser.execute_script(departure)

        commanDateFrom = f"document.getElementById('{config.get('dateFrom')}').value='{startTrip}';"
        commandDateBack = f"document.getElementById('{config.get('dateBack')}').value='{endTrip}';"
        browser.execute_script(commanDateFrom)
        browser.execute_script(commandDateBack)

        command1 = f'document.getElementById("horarecogida").value="{timeStart}";'
        command2 = 'document.getElementById("minutosrecogida").value="00";'
        command3 = f'document.getElementById("horadevolucion").value="{timeEnd}";'
        command4 = 'document.getElementById("minutosdevolucion").value="00";'
        browser.execute_script(command1)
        browser.execute_script(command2)
        browser.execute_script(command3)
        browser.execute_script(command4)

        if not query.round_trip:
            print("Handle one way trip")
            browser.find_element(By.ID, config.get("oneWay")).click()

            location = self.getLocation(query.to_city, query.return_place)
            arrival = f"document.getElementById('destino_final').value='{location['location_id']}';"
            browser.execute_script(arrival)
            arrival = f"document.getElementById('{config.get('arrival')}').value='{location['location_name']}';"
            browser.execute_script(arrival)

        # submit form
        browser.find_element(By.ID, config.get("submit")).click()

        return ""

    def getLocation(self, city: str, place: str) -> dict:
        city = f"{city} {place}"
        data = {
            "destino": city,
            "idoma": "es",
            "origien": "DY",
            "experimiento": "[CAR]"
        }

        print("Get location for " + city)
        response = requests.post("https://www.doyouspain.com/do/ajax/autocomplete", data=data)
        print(response)

        location_id = ""
        location_name = ""

        data_value = re.search(r"data-destino='([^']+)'", response.text)
        if data_value:
            location_id = data_value.group(1)

        first_span_text = re.search(r"data-destino-description='([^']+)'", response.text)
        if first_span_text:
            location_name = html.unescape(first_span_text.group(1))

        results = {
            "location_id": location_id,
            "location_name": location_name
        }
        print(results)
        return results
