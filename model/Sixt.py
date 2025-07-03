import logging
import time
import datetime
import webbrowser
import requests
import json
from .data_classes import SearchQuery

class Sixt:

    def parse(self, query: SearchQuery):
        startTrip = query.start_date.strftime(query.params.get("dateFormat"))
        endTrip = query.end_date.strftime(query.params.get("dateFormat"))

        pickup = self.getLocation(query.from_city, query.from_country)

        if query.round_trip:
            dropoff = pickup
        else:
            dropoff = self.getLocation(query.to_city, query.to_country)

        logging.info("pickup location:")
        logging.info(pickup)
        logging.info("dropoff location:")
        logging.info(dropoff)

        url = query.params.get("url") + query.params.get("queryParams")
        url = url.format(
            departureLocationId=pickup.get("locationId"),
            arrivalLocationId=dropoff.get("locationId"),
            departureLocation=pickup.get("title"),
            arrivalLocation=dropoff.get("title"),
            departureBranch=pickup.get("branch"),
            arrivalBranch=dropoff.get("branch"),
            dateFrom=startTrip,
            dateBack=endTrip,
            adults=query.adults,
            startTrip=startTrip,
            endTrip=endTrip
        )

        logging.info("url: " + url)
        webbrowser.open(url)

        return ""

    def getLocation(self, city: str, country: str):
        headers = {
            "Content-Type": "application/json",
            "Host": "grpc-prod.orange.sixt.com",
            "Content-Length": "21",
        }

        logging.info(f"Get sixt location for: {city}")
        response = requests.post(
            "https://grpc-prod.orange.sixt.com/com.sixt.service.rent_booking.api.SearchService/SuggestLocations",
            data=json.dumps({"query": f"{city} {country}"}),
            headers=headers
        )

        time.sleep(3)
        locationId = response.json().get("suggestions")[0].get("location").get("location_id")
        response = requests.post(
            "https://grpc-prod.orange.sixt.com/com.sixt.service.rent_booking.api.SearchService/SelectLocation",
            data=json.dumps({"location_id": locationId}),
            headers=headers
        )

        location = response.json()
        details = location.get("selected_location")

        return {
            "locationId": location.get("location_selection_id"),
            "title": details.get("title").replace(" ", "%20"),
            "branch": details.get("location_id"),
        }