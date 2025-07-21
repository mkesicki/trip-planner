import logging
import airportsdata
import webbrowser
import importlib.util

from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from country_list import countries_for_language
from .data_classes import SearchQuery

class Parser:

    def __init__(self, query: SearchQuery):
        self.query = query
        self.countries = dict(countries_for_language('en'))

        self.start = self.query.start_date
        self.end = self.query.end_date

        self.startTrip = self.start.strftime(self.query.params.get("dateFormat"))
        self.endTrip = self.end.strftime(self.query.params.get("dateFormat"))

        self.timeStart = self.start.strftime("%H:00")
        self.timeEnd = self.end.strftime("%H:00")

        if "airportCode" in self.query.params:
            self.query.from_city = self.findAirportCode(self.query.from_country, self.query.from_city, self.query.params.get("airportCode"))
            self.query.to_city = self.findAirportCode(self.query.to_country, self.query.to_city, self.query.params.get("airportCode"))

    def search(self):
        if self.query.params.get("type") == "browser":
            url = self.query.params.get("url") if self.query.round_trip else self.query.params.get("urlOneWay")
            url = url + self.query.params.get("queryParams")
            url = url.format(
                departure=self.query.from_city,
                arrival=self.query.to_city,
                dateFrom=self.startTrip,
                dateBack=self.endTrip,
                adults=self.query.adults,
                timeStart=self.timeStart,
                timeEnd=self.timeEnd,
                arrivalCountry=self.query.to_country,
                departureCountry=self.query.from_country
            )
            logging.info("url: " + url)
            return url

        elif self.query.params.get("type") == "parseWeb":
            # TODO: This needs to be handled. For now, it will not do anything.
            company = self.query.params.get("company")
            if importlib.util.find_spec(f"model.{company}", f"./{company}.py") is not None:
                try:
                    logging.info("Parse: " + company)
                    module = importlib.import_module(f"model.{company}", f"./{company}.py")
                    obj = getattr(module, company)()
                    obj.parse(self.query)
                except (NoSuchElementException, ElementClickInterceptedException) as e:
                    logging.error(f"Handle selenium exception: {e}")
        return None

    def findAirportCode(self, country: str, city: str, type: str = "IATA") -> str:
        airports = airportsdata.load(type)
        for code, airport in airports.items():
            if airport.get("city").lower() == city.lower() and airport.get("country").lower() == country.lower():
                return code
        return ""
