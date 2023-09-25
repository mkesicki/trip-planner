
import datetime
import airportsdata
import webbrowser
import importlib.util

from country_list import countries_for_language

class Parser:

    def __init__(self, fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : str, endDate : str, adults : int, params : dict):

        self.fromCity = fromCity
        self.fromCountry = fromCountry
        self.toCity = toCity
        self.toCountry = toCountry
        self.roundTrip = roundTrip
        self.startDate = startDate
        self.endDate = endDate
        self.adults = adults
        self.params = params
        self.countries = dict(countries_for_language('en'))

        self.start = datetime.datetime.strptime(startDate,"%Y-%m-%dT%H:%M")
        self.end = datetime.datetime.strptime(endDate,"%Y-%m-%dT%H:%M")

        self.startTrip = self.start.strftime(self.params.get("dateFormat"))
        self.endTrip = self.end.strftime(self.params.get("dateFormat"))

        self.timeStart = self.start.strftime("%H:00")
        self.timeEnd = self.end.strftime("%H:00")

        if "airportCode" in self.params:

            self.fromCity = self.findAirportCode(self.fromCountry, self.fromCity, self.params.get("airportCode"))
            self.toCity = self.findAirportCode(self.toCountry, self.toCity, self.params.get("airportCode"))

    def search(self) :

        if self.params.get("type") == "browser":

            url =  self.params.get("url") if (self.roundTrip == "on") else  self.params.get("urlOneWay")
            url = url + self.params.get("queryParams")
            url = url.format(departure = self.fromCity, arrival = self.toCity, dateFrom = self.startTrip, dateBack = self.endTrip, adults = self.adults, timeStart = self.timeStart, timeEnd = self.timeEnd, arrivalCountry = self.toCountry, departureCountry = self.fromCountry )

            print("url: " + url)
            webbrowser.open(url)

        elif self.params.get("type") == "parseWeb":

            company = self.params.get("company")

            if importlib.util.find_spec("model."+company,"./" + company +".py") is not None:

                print("Parse: " + company)
                module = importlib.import_module("model."+company,"./" + company +".py")
                obj = getattr(module, company)()
                obj.parse(self.fromCity, self.fromCountry, self.toCity, self.toCountry, self.roundTrip == "on", self.start, self.end, self.adults, self.params)

    def findAirportCode(self,  country : str, city : str, type : str = "IATA") -> str:

        airports = airportsdata.load(type)

        for code, airport in airports.items():

            if (airport.get("city").lower() == city.lower() and airport.get("country").lower() == country.lower()):
                return code

        return ""

