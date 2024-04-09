import time
import datetime
import webbrowser
import requests
import json

from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

class Sixt:

    def parse(self, fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : datetime.date, endDate : datetime.date, adults : int, params : dict):

        startTrip = startDate.strftime(params.get("dateFormat"))
        endTrip = endDate.strftime(params.get("dateFormat"))

        pickup = self.getLocation(fromCity, fromCountry)

        if (roundTrip == True):
            dropoff = pickup
        else:
            dropoff = self.getLocation(toCity, toCountry)

        print("pickup location:")
        print(pickup)
        print("dropoff location:")
        print(dropoff)

        url =  params.get("url")
        url = url + params.get("queryParams")
        url = url.format(departureLocationId = pickup.get("locationId"), arrivalLocationId = dropoff.get("locationId"),departureLocation = pickup.get("title") , arrivalLocation = dropoff.get("title") ,departureBranch = pickup.get("branch") , arrivalBranch = dropoff.get("branch"), dateFrom = startTrip, dateBack = endTrip, adults = adults, startTrip = startTrip, endTrip = endTrip)

        print("url: " + url)
        webbrowser.open(url)

        return ""

    def getLocation(self, city : str, country : str):

        headers = {
            "Content-Type": "application/json",
            "Host": "grpc-prod.orange.sixt.com",
            "Content-Length": "21",
        }

        print("Get sixt location for: " + city)
        response = requests.post("https://grpc-prod.orange.sixt.com/com.sixt.service.rent_booking.api.SearchService/SuggestLocations", data = json.dumps({"query": city + " " + country }), headers = headers)

        time.sleep(3)
        locationId = response.json().get("suggestions")[0].get("location").get("location_id")
        response = requests.post("https://grpc-prod.orange.sixt.com/com.sixt.service.rent_booking.api.SearchService/SelectLocation", data = json.dumps({"location_id": locationId}), headers = headers)

        location = response.json()
        details = location.get("selected_location")

        return {
            "locationId": location.get("location_selection_id"),
            "title": details.get("title").replace(" ", "%20"),
            "branch": details.get("location_id"),
        }
