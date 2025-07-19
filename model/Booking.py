import logging
import requests
import webbrowser
import json
from .data_classes import SearchQuery

class Booking:

    def parse(self, query: SearchQuery):
        startTrip = query.start_date.strftime(query.params.get("dateFormat"))
        endTrip = query.end_date.strftime(query.params.get("dateFormat"))

        headers = {
            "Content-Length": "53",
            "Host": "accommodations.booking.com"
        }

        data = {"query": f"{query.to_city},{query.to_country}", "language": "en-us", "size": 5}
        response = requests.post("https://accommodations.booking.com/autocomplete.json", data=json.dumps(data), headers=headers)

        logging.info(response.json().get("results"))

        place = response.json().get("results")[0]

        url = query.params.get("url") + query.params.get("queryParams")
        value = place.get("value").replace(", ", ",").replace(" ", "%20")
        url = url.format(
            arrival=value,
            dateFrom=startTrip,
            dateBack=endTrip,
            adults=query.adults,
            destId=place.get("labels")[0].get("dest_id")
        )

        logging.info("url: " + url)
        webbrowser.open(url)

        return ""
