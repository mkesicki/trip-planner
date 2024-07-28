import datetime
import webbrowser
import requests
import urllib.parse

class RentalCars:

    def parse(self, fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : datetime.date, endDate : datetime.date, adults : int, params : dict,  pickupPlace : str, returnPlace : str):

        time = self.parseDate(startDate, "pu")
        time += self.parseDate(endDate, "do")

        pickupPlace = pickupPlace.replace("train", "railway")
        returnPlace = returnPlace.replace("train", "railway")

        pickup = self.getLocation(fromCity + " " + pickupPlace, fromCountry)

        if (roundTrip == True):
            dropoff = pickup
        else:
            dropoff = self.getLocation(toCity + " " + returnPlace, toCountry)

        print("pickup location:")
        print(pickup)
        print("dropoff location:")
        print(dropoff)

        url =  params.get("url")
        url = url + params.get("queryParams")
        url = url.format(pickupCords=pickup.get("cords"), times=time, dropCords=dropoff.get("cords"), pickupLocationName=pickup.get("name"), dropLocationName=dropoff.get("name"))

        print("url: " + url)
        webbrowser.open(url)

        return ""

    def getLocation(self, city : str, country : str):

        print("Get RentalCars location for: " + city)
        response = requests.post(f"https://cars.booking.com/api/location-suggestions?term={city}")

        print(response.json())
        data = response.json()

        return {
            "name": urllib.parse.quote_plus(data[0]["name"]),
            "type": data[0]["placeType"],
            "cords": str(data[0]["lat"]) + "%2C" + str(data[0]["lng"]),
        }

    def parseDate(self, date : datetime, prefix:str) -> str:

        return f"&{prefix}Day={date.day}&{prefix}Hour={date.hour}&{prefix}Minute={date.minute}&{prefix}Month={date.month}&{prefix}Year={date.year}"
