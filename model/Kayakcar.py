import logging
import requests
import webbrowser
from .data_classes import SearchQuery

class Kayakcar:

    def parse(self, query: SearchQuery):

        startTrip = query.start_date.strftime(query.params.get("dateFormat"))
        endTrip = query.end_date.strftime(query.params.get("dateFormat"))

        timeStart = query.start_date.strftime("%H")
        timeEnd = query.end_date.strftime("%H")

        searchUrl = f"https://www.kayak.es/mvm/smartyv2/search?f=j&s=car&where={query.from_city}&lc_cc={query.from_country}"
        response = requests.post(searchUrl)
        first = response.json()[0]
        fromCity = f"{query.from_city}-c{first['id']}"

        toCity = ""
        if not query.round_trip:
            searchUrl = f"https://www.kayak.es/mvm/smartyv2/search?f=j&s=car&where={query.to_city}&lc_cc={query.to_country}"
            response = requests.post(searchUrl)
            first = response.json()[0]
            toCity = f"{query.to_city}-c{first['id']}"

        url = query.params.get("url") if query.round_trip else query.params.get("urlOneWay")
        url += query.params.get("queryParams")
        url = url.format(
            departure=fromCity,
            arrival=toCity,
            dateFrom=startTrip,
            dateBack=endTrip,
            timeStart=timeStart,
            timeEnd=timeEnd
        )

        logging.info("url: " + url)
        webbrowser.open(url)

        return ""
