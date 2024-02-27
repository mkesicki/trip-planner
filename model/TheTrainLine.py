import sys
import datetime
import requests
import webbrowser

class TheTrainLine:

     def parse(self, fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : datetime.date, endDate : datetime.date, adults : int, params : dict):

        startTrip = startDate.strftime(params.get("dateFormat"))
        endTrip = endDate.strftime(params.get("dateFormat"))

        urlPrefix = "https://www.thetrainline.com/api/locations-search/v2/search?searchTerm={city} {country}&locale=en-US"
        searchUrl = urlPrefix.format(city = fromCity, country = fromCountry)
        response = requests.get(searchUrl)
        first = response.json()["searchLocations"][0]
        fromCity = first["code"]

        searchUrl = urlPrefix.format(city = toCity, country = toCountry)
        response = requests.get(searchUrl)
        first = response.json()["searchLocations"][0]
        toCity = first["code"]

        url = params.get("url") if (roundTrip == True) else  params.get("urlOneWay")
        url = url.format(departure = fromCity, arrival = toCity, dateFrom = startTrip, dateBack = endTrip )

        today = datetime.date.today()
        years_ago = today - datetime.timedelta(days=30*365)
        passanger_date = years_ago.strftime("%Y-%m-%d")

        passangers = ""
        for i in range(int(adults)):
            passangers = passangers + "&passengers[]=" + passanger_date

        url = url + passangers
        print("Open url: " + url)
        webbrowser.open(url)

        return ""

