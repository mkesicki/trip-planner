import os
import requests

from bs4 import BeautifulSoup

def getPlacesFromHTML(city : str, country : str, content : str) -> list:

    places = BeautifulSoup(content, 'html.parser').find_all("ol", class_="places")[0].find_all("li")
    body = []

    for place in places:

        body.append(
            {
                "name": place.find_all("dl", class_="name")[0].text + " " + city + ", " + country,
                "description": place.find_all("dt", class_="description")[0].text + " Links: <br />"
                    + place.find_all("span", class_="wiki")[0].find_all("a", href=True)[0].get("href") + " &amp; "
                    + " " + place.find_all("span", class_="google")[0].find_all("a", href=True)[0].get("href") + " "
            })

    exit(1)

    return body

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

    print("* KML File Content * Use it to create map in MyMaps.")
    print(file)
    print("* End of KML File * Also stored in " + filename + " file.")

    f = open("maps/" + filename, "w" )
    f.write(file)
    f.close()

    print(file)

    return file