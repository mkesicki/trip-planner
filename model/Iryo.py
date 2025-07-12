import logging
import requests
import webbrowser
import json
import urllib.parse

from .data_classes import SearchQuery

class Iryo:

    def parse(self, query: SearchQuery):

        startTrip = query.start_date.strftime(query.params.get("dateFormat"))
        endTrip = query.end_date.strftime(query.params.get("dateFormat"))

        tripDirection =  "outboundAndInbound" if query.round_trip is True else "outbound"

        headers = {
            "Origin": "https://iryo.eu",
            "Ocp-Apim-Subscription-Key": "7c9b9b1ea0fe4f0c9d1739fcbf8b5438",
            "User-Agent": "PostmanRuntime/7.44.1"
        }
        stations = requests.get("https://api.iryo.eu/b2c/support/stations?mappings=true&mappings-usage=GTM&lang=es&kcClient=b2c&requestChannel=WEB", headers=headers)

        data = stations.json()
        passengers = []

        adults = query.adults
        for i in (1, adults + 1) :
            passengers.append({"type":"AD","discountCards":[],"id":f"passenger_{i}"})

        origin = self.findStation(city=query.from_city, stations=data.get("data"))
        destination = self.findStation(city=query.to_city, stations=data.get("data"))

        travels = []

        travels.append({"origin":origin.get("uicStationCode"),"destination":destination.get("uicStationCode"),"direction":"outbound","departure":startTrip})

        if query.round_trip is True:
            travels.append({"origin":destination.get("uicStationCode"),"destination":origin.get("uicStationCode"),"direction":"inbound","departure":endTrip})

        params_dict = {
            'passengers': json.dumps(passengers),
            'origin': json.dumps(origin),
            'destination': json.dumps(destination),
            'tripDirection': tripDirection,
            'travels': json.dumps(travels),
            'payWithPoints': 'false',
            'currency': 'EUR',
            'tripIntention': 'forLeisure',
            'passengerHSelected': 'false'
        }

        query_string = urllib.parse.urlencode(params_dict)
        url = f"https://iryo.eu/es/booking/travels?{query_string}"

        webbrowser.open(url)

    def findStation(self, city, stations):
        for station in stations:
            if city.lower() in station.get("city").lower():
                return station
        logging.info(f"Station for {city} not found!")
        return ""
