#!/usr/bin/env python3
import requests
import os
from typing import Dict, List, Optional

class GooglePlacesAPI:
    """Simple Google Places API client"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://places.googleapis.com/v1/places"
        self.headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key
        }

    def get_city_coordinates(self, city: str, country: str = "") -> Optional[Dict]:

        """
        Step 1: Get coordinates for a city
        """
        query = f"{city}"
        if country:
            query += f" {country}"

        url = f"{self.base_url}:searchText"
        headers = {
            **self.headers,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location"
        }

        data = {
            "textQuery": query,
            "maxResultCount": 1
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()

            result = response.json()
            if "places" in result and len(result["places"]) > 0:
                place = result["places"][0]
                return {
                    "city_name": place.get("displayName", {}).get("text", ""),
                    "address": place.get("formattedAddress", ""),
                    "latitude": place.get("location", {}).get("latitude"),
                    "longitude": place.get("location", {}).get("longitude"),
                    "place_id": place.get("id", "")
                }
            return None

        except Exception as e:
            print(f"Error getting city coordinates: {e}")
            return None

    def search_attractions_by_coordinates(self, latitude: float, longitude: float, max_results: int = 20) -> List[Dict]:
        """
        Step 2: Search attractions near coordinates
        """
        url = f"{self.base_url}:searchNearby"
        headers = {
            **self.headers,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.types,places.websiteUri,places.googleMapsUri"
        }

        data = {
            "includedTypes": [
                "tourist_attraction",
                "museum",
                "church",
                "art_gallery",
                "zoo",
                "amusement_park",
                "park",
                "observation_deck",
                "historical_landmark",
                "historical_place",
                "cultural_landmark",
                "monument",
                "national_park",
                "state_park",
                "hiking_area",
                "botanical_garden",
                "plaza",
                "hindu_temple",
                "mosque",
                "synagogue"
            ],
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude
                    },
                    "radius": 15000
                }
            },
            "maxResultCount": max_results
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=15)
            response.raise_for_status()

            result = response.json()
            attractions = []

            if "places" in result:
                for place in result["places"]:
                    attraction = {
                        "name": place.get("displayName", {}).get("text", ""),
                        "place_id": place.get("id", ""),
                        "address": place.get("formattedAddress", ""),
                        "latitude": place.get("location", {}).get("latitude"),
                        "longitude": place.get("location", {}).get("longitude"),
                        "rating": place.get("rating"),
                        "review_count": place.get("userRatingCount"),
                        "types": place.get("types", []),
                        "website": place.get("websiteUri"),
                        "google_maps_url": place.get("googleMapsUri")
                    }
                    attractions.append(attraction)

            return attractions

        except Exception as e:
            print(f"Error searching attractions: {e}")
            return []

def find_attractions(city: str, country: str) -> List:

    api_key = os.getenv("GOOGLE_API_KEY")
    client = GooglePlacesAPI(api_key)
    city_info = client.get_city_coordinates(city, country)

    if not city_info:
        print(f"❌ Could not find coordinates for {city} {country}")
        return

    return client.search_attractions_by_coordinates(
        city_info['latitude'],
        city_info['longitude']
    )

if __name__ == "__main__":

    city = "Barcelona"
    country = "Spain"

    attractions = find_attractions(city, country)