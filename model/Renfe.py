import logging
import re
import requests
import json
from playwright.sync_api import sync_playwright
from .data_classes import SearchQuery

class Renfe:
    def _get_stations(self):
        """Fetches and parses the station data from Renfe's static JS file."""
        try:
            response = requests.get("https://www.renfe.com/content/dam/renfe/es/General/buscadores/javascript/estacionesEstaticas.js")
            response.raise_for_status()
            match = re.search(r'var estacionesEstatico=(.+);', response.text)
            if match:
                return json.loads(match.group(1))
        except requests.RequestException as e:
            logging.error(f"Failed to fetch Renfe station data: {e}")
        except (json.JSONDecodeError, IndexError) as e:
            logging.error(f"Failed to parse Renfe station data: {e}")
        return []

    def findStation(self, city: str, stations: list) -> dict:
        """Finds a station from the list with a prioritized search."""
        city_lower = city.lower()

        # Priority 1: Exact match for "City (todas)"
        for station in stations:
            if station.get("desgEstacion", "").lower() == f"{city_lower} (todas)":
                return station

        # Priority 2: Match for "City-"
        for station in stations:
            if station.get("desgEstacion", "").lower() == f"{city_lower}-":
                return station

        # Priority 3: Substring match
        for station in stations:
            if city_lower in station.get("desgEstacion", "").lower():
                return station

        return {} # Return empty dict if no station is found

    def parse(self, query: SearchQuery):
        startTrip = query.start_date.strftime(query.params.get("dateFormat"))
        endTrip = query.end_date.strftime(query.params.get("dateFormat"))
        config = query.params.get("params")

        stations = self._get_stations()
        if not stations:
            logging.error("Could not retrieve station list. Aborting Renfe search.")
            return

        departure_code = self.findStation(query.from_city, stations)
        arrival_code = self.findStation(query.to_city, stations)

        if not departure_code or not arrival_code:
            logging.error(f"Could not find station for {query.from_city} or {query.to_city}")
            return

        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(query.params.get("url"))
        page.wait_for_load_state('load', timeout=5000)

        # Accept cookies
        if "cookiesAccept" in config:
            page.click(f"#{config.get('cookiesAccept')}")

        # Consolidate all form filling and submission into a single JS block
        round_trip_js = f"document.querySelector(\"input[name='{config.get('dateBack')}']\").value='{endTrip}';" if query.round_trip else "document.querySelector('button.rf-select__list-text:first-child').click();"

        form_script = f"""
        (function() {{
            document.querySelector("input[name='{config.get('adults')}']").value = '{query.adults}';
            document.querySelector("input[name='{config.get('departure')}']").value = '{departure_code.get('clave')}';
            document.querySelector("input[name='{config.get('arrival')}']").value = '{arrival_code.get('clave')}';
            document.querySelector("input[name='{config.get('dateFrom')}']").value = '{startTrip}';
            {round_trip_js}
            document.querySelector('form').submit();
        }})();
        """

        page.evaluate(form_script)
        page.wait_for_load_state('networkidle', timeout=30000)

