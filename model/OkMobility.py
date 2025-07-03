import datetime
import webbrowser
import requests
import re
from .data_classes import SearchQuery

class OkMobility:

    def parse(self, query: SearchQuery):
        startTrip = query.start_date.strftime(query.params.get("dateFormat"))
        endTrip = query.end_date.strftime(query.params.get("dateFormat"))

        startTime = query.start_date.strftime("%H:00")
        endTime = query.end_date.strftime("%H:00")

        self.url = query.params.get("initUrl")
        self.config = query.params.get("params")

        pickupId = self.getLocation(query.from_city, query.pickup_place)

        if query.round_trip:
            dropoffId = pickupId
        else:
            dropoffId = self.getLocation(query.to_city, query.return_place)

        print("pickup location: " + pickupId)
        print("dropoff location: " + dropoffId)

        url = query.params.get("url") + query.params.get("queryParams")
        url = url.format(
            id=pickupId,
            dropoffId=dropoffId,
            departure=query.from_city,
            arrival=query.to_city,
            dateFrom=startTrip,
            dateBack=endTrip,
            startTime=startTime,
            endTime=endTime
        )

        print("url: " + url)
        webbrowser.open(url)

        return ""

    def getLocation(self, city: str, place: str) -> str:
        response = requests.get(f"https://okmobility.com/api/search-widget?type=rent-offices&lang=en&search={city} {place}")
        print(f"https://okmobility.com/api/search-widget?type=offices&lang=en&search={city} {place}")

        pickupId = ""
        data_value = re.search(r'data-value="(\d+)"', response.text)
        if data_value:
            pickupId = data_value.group(1)

        return pickupId
