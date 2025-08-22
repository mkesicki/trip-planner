
import json
import os
import requests
import re
from typing import List, Dict


def tripadvisor(city: str, country: str) -> List[Dict]:

    api_key = os.environ.get("TRIP_ADVISOR_API_KEY")

    # response = requests.get(f"https://api.content.tripadvisor.com/api/v1/location/search?key={api_key}&category=geos&language=en&searchQuery={city} {country}")


    # data = response.json()
    # print(data)
    # location_id = data.get("data")[0].get("location_id")
    # print(location_id)

    # response = requests.get(f"https://api.content.tripadvisor.com/api/v1/location/{location_id}/details?key={api_key}&language=en&currency=eur")

    # details = response.json()
    # print(details)

    # url = details.get("web_url")

    location_id = 187497
    url = "https://www.tripadvisor.com/Tourism-g187497-Barcelona_Catalonia-Vacations.html?m=66827"

    replace = f"g{location_id}-"
    print(replace)
    url = url.replace("Tourism", "Attractions")
    url = url.replace(replace, f"{replace}Activities-oa0-")

    print(url)

if __name__ == "__main__":
    tripadvisor("Barcelona", "Spain")