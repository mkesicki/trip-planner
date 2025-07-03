import logging
import os
import requests

from utils import *

def getGeocodeDetails(place : str) -> dict:

        url = "https://maps.googleapis.com/maps/api/geocode/json"

        params = {
            "address": place,
            "key": os.environ['Google_API_Key']
        }

        r = requests.get(url, params = params)

        return r.json()['results'][0]['geometry']['location']

def prepareKMLFile(city : str, country : str, data : str) -> str:

    places = getPlacesFromHTML(city, country, data)
    file = """<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document id="placemarks">"""

    for place in places:

         geo = getGeocodeDetails(place["name"])

         file = file + """
            <Placemark>
                <name>{name}</name>
                <description>{description}</description>
                <Point>
                    <coordinates>{lng},{lat}</coordinates>
                </Point>
            </Placemark>""".format(name = place["name"], description = place["description"], lng = geo["lng"], lat = geo["lat"])

    file = file  + """</Document></kml>"""

    filename  = city.title() + " " + country.title() + " Map.kml"

    logging.info("* KML File Content * Use it to create map in MyMaps.")
    logging.info(file)
    logging.info("* End of KML File * Also stored in " + filename + " file.")

    f = open("maps/" + filename, "w", encoding='utf-8')
    f.write(file)
    f.close()

    return file
