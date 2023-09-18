
import datetime
import airportsdata
import webbrowser
import importlib.util

from model.Transport import Transport

from country_list import countries_for_language

class Plane(Transport):

    def __init__(self, fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : str, endDate : str, adults : int, params : dict):

        super().__init__(fromCity, fromCountry, toCity, toCountry, roundTrip, startDate, endDate, adults, params)

        self.countries = dict(countries_for_language('en'))
        self.start = datetime.datetime.strptime(startDate,"%Y-%m-%dT%H:%M")
        self.end = datetime.datetime.strptime(endDate,"%Y-%m-%dT%H:%M")
        self.fromAirportCode = self.findAirportCode(self.fromCountry, self.fromCity, self.params.get("airportCode"))
        self.toAirportCode = self.findAirportCode(self.toCountry, self.toCity, self.params.get("airportCode"))
        self.startFlight = self.start.strftime(self.params.get("dateFormat"))
        self.endFlight = self.end.strftime(self.params.get("dateFormat"))

    def search(self) :

        if self.params.get("type") == "browser":

            url =  self.params.get("url") if (self.roundTrip == "on") else  self.params.get("urlOneWay")
            url = url + self.params.get("queryParams")
            url = url.format(departure = self.fromAirportCode, arrival = self.toAirportCode, dateFrom = self.startFlight, dateBack = self.endFlight, adults = self.adults)

            # print("url: " + url)

            # webbrowser.open(url)

        elif self.params.get("type") == "parseWeb":

            company = self.params.get("company")



            # vueling = Vueling().parse(self.fromCity, self.fromCountry, self.toCity, self.toCountry, self.roundTrip, self.startDate, self.endDate, self.adults, self.params)
            # exit(1)

            # classes and all that jazz ?

            if importlib.util.find_spec("model."+company.title(),"./" + company.title() +".py") is not None:
                print("Parse: " + company)
                module = importlib.import_module("model."+company.title(),"./" + company.title() +".py")
                obj = getattr(module, company.title())(self.fromCity, self.fromCountry, self.toCity, self.toCountry, self.roundTrip, self.startDate, self.endDate, self.adults, self.params)
                obj.parse()

    def findAirportCode(self,  country : str, city : str, type : str = "IATA") -> str:

        airports = airportsdata.load(type)

        for code, airport in airports.items():

            if (airport.get("city") == city and airport.get("country") == country):
                return code

        return ""

