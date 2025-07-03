import sys
import datetime
import requests
import webbrowser
from .data_classes import SearchQuery

class TheTrainLine:

    def parse(self, query: SearchQuery):
        startTrip = query.start_date.strftime(query.params.get("dateFormat"))
        endTrip = query.end_date.strftime(query.params.get("dateFormat"))

        urlPrefix = "https://www.thetrainline.com/api/locations-search/v2/search?searchTerm={city} {country}&locale=en-US"
        
        searchUrl = urlPrefix.format(city=query.from_city, country=query.from_country)
        response = requests.get(searchUrl)
        first = response.json()["searchLocations"][0]
        fromCity = first["code"]

        searchUrl = urlPrefix.format(city=query.to_city, country=query.to_country)
        response = requests.get(searchUrl)
        first = response.json()["searchLocations"][0]
        toCity = first["code"]

        url = query.params.get("url") if query.round_trip else query.params.get("urlOneWay")
        url = url.format(departure=fromCity, arrival=toCity, dateFrom=startTrip, dateBack=endTrip)

        today = datetime.date.today()
        years_ago = today - datetime.timedelta(days=30 * 365)
        passenger_date = years_ago.strftime("%Y-%m-%d")

        passengers = ""
        for _ in range(query.adults):
            passengers += f"&passengers[]={passenger_date}"

        url += passengers
        print("Open url: " + url)
        webbrowser.open(url)

        return ""

