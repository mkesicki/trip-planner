import datetime
import webbrowser
import requests
import urllib.parse
from .data_classes import SearchQuery

class RentalCars:

    def parse(self, query: SearchQuery):
        time = self.parseDate(query.start_date, "pu")
        time += self.parseDate(query.end_date, "do")

        pickupPlace = query.pickup_place.replace("train", "railway")
        returnPlace = query.return_place.replace("train", "railway")

        pickup = self.getLocation(f"{query.from_city} {pickupPlace}", query.from_country)

        if query.round_trip:
            dropoff = pickup
        else:
            dropoff = self.getLocation(f"{query.to_city} {returnPlace}", query.to_country)

        print("pickup location:")
        print(pickup)
        print("dropoff location:")
        print(dropoff)

        url = query.params.get("url") + query.params.get("queryParams")
        url = url.format(
            pickupCords=pickup.get("cords"),
            times=time,
            dropCords=dropoff.get("cords"),
            pickupLocationName=pickup.get("name"),
            dropLocationName=dropoff.get("name")
        )

        print("url: " + url)
        webbrowser.open(url)

        return ""

    def getLocation(self, city: str, country: str):
        print(f"Get RentalCars location for: {city}")
        response = requests.post(f"https://cars.booking.com/api/location-suggestions?term={city}")
        print(response.json())
        data = response.json()
        return {
            "name": urllib.parse.quote_plus(data[0]["name"]),
            "type": data[0]["placeType"],
            "cords": f"{data[0]['lat']}%2C{data[0]['lng']}",
        }

    def parseDate(self, date: datetime.datetime, prefix: str) -> str:
        return f"&{prefix}Day={date.day}&{prefix}Hour={date.hour}&{prefix}Minute={date.minute}&{prefix}Month={date.month}&{prefix}Year={date.year}"
