import datetime
import webbrowser
import requests
import re

class OkMobility:

    def parse(self, fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : datetime.date, endDate : datetime.date, adults : int, params : dict, pickupPlace : str, returnPlace : str):

        startTrip = startDate.strftime(params.get("dateFormat"))
        endTrip = endDate.strftime(params.get("dateFormat"))

        startTime = startDate.strftime("%H:00")
        endTime = endDate.strftime("%H:00")

        self.url = params.get("initUrl")
        self.config = params.get("params")

        pickupId = self.getLocation(fromCity, pickupPlace)

        if (roundTrip == True):
            dropoffId = pickupId
        else:
            dropoffId = self.getLocation(toCity, returnPlace)

        print("pikup location: " + pickupId)
        print("dropoff location: " + dropoffId)

        url =  params.get("url")
        url = url + params.get("queryParams")
        url = url.format(id = pickupId, dropoffId = dropoffId, departure = fromCity, arrival = toCity, dateFrom = startTrip, dateBack = endTrip, startTime = startTime, endTime = endTime)

        print("url: " + url)
        webbrowser.open(url)

        return ""

    def getLocation(self, city : str, place : str) -> str:

        response = requests.get("https://okmobility.com/api/search-widget?type=offices&lang=en&search=" + city + " " + place)

        print("https://okmobility.com/api/search-widget?type=offices&lang=en&search=" + city + " " + place)

        pickupId = ""

        data_value = re.search(r'data-value="(\d+)"', response.text)

        if data_value:
            pickupId = data_value.group(1)

        return pickupId
