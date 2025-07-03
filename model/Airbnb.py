import logging
import json
import requests
import webbrowser

from .data_classes import SearchQuery

class Airbnb:

    def parse(self, query: SearchQuery):
        startTrip = query.start_date.strftime(query.params.get("dateFormat"))
        endTrip = query.end_date.strftime(query.params.get("dateFormat"))

        headers = {
            "Content-Length": "53",
            "Host": "accommodations.booking.com"
        }

        data = {"query": f"{query.to_city} {query.to_country}", "language": "en-us", "size": 5}
        response = requests.post("https://accommodations.booking.com/autocomplete.json", data=json.dumps(data), headers=headers)

        place = response.json().get("results")[0]

        url = query.params.get("url") + query.params.get("queryParams")
        url = url.format(
            arrival=place.get("value").replace(" ", "%20"),
            dateFrom=startTrip,
            dateBack=endTrip,
            adults=query.adults,
            destId=place.get("labels")[0].get("dest_id")
        )

        logging.info("url: " + url)
        webbrowser.open(url)

        return ""