import webbrowser
from .data_classes import SearchQuery
import urllib.parse

class Google:

    def parse(self, query: SearchQuery):
        start_date = query.start_date.strftime("%Y-%m-%d")

        query_string = f"Flights to {query.to_city} from {query.from_city} on {start_date}"

        if query.round_trip:
            end_date = query.end_date.strftime("%Y-%m-%d")
            query_string += f" through {end_date}"
        else:
            query_string += " one way"

        if query.adults > 1:
            query_string += f" for {query.adults} adults"

        encoded_query = urllib.parse.quote(query_string)

        url = f"https://www.google.com/travel/flights?q={encoded_query}"

        webbrowser.open(url)

        return ""
