import datetime
import requests
import webbrowser
import json

class Airbnb:

    def parse(self, fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : datetime.date, endDate : datetime.date, adults : int, params : dict):

        startTrip = startDate.strftime(params.get("dateFormat"))
        endTrip = endDate.strftime(params.get("dateFormat"))

        headers = {
            "Content-Length": "53",
            "Host": "accommodations.booking.com"
        }

        data = {"query":toCity + " " + toCountry,"language":"en-us","size":5}

        print(json.dumps(data))
        response = requests.post("https://accommodations.booking.com/autocomplete.json", data = json.dumps(data), headers = headers)

        place = response.json().get("results")[0]

        url = params.get("url")
        url = url + params.get("queryParams")
        url = url.format(arrival = place.get("value").replace(" ", "%20"), dateFrom = startTrip, dateBack = endTrip, adults = adults, destId = place.get("labels")[0].get("dest_id"))

        print("url: " + url)
        webbrowser.open(url)

        return ""