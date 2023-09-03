import argparse
import requests

from bs4 import BeautifulSoup
from ai import *
from onenote import *
from maps import *

parser = argparse.ArgumentParser(description = 'Plan a trip for selected place in given country.')
parser.add_argument('city', help = 'a city for which to plan the trip')
parser.add_argument('--min', default = 20, help = 'Minimum number of returned attractions, e.g. 5. Default 20')
parser.add_argument('--max', default = 20,  help = 'Maximum number of returned attractions, e.g. 10. Default 20')
parser.add_argument('--country', default = "Spain",  help = 'Optional country. Default Spain')
parser.add_argument('--home', default = "Barcelona",  help = 'Optional home city, it is used to find direction  to selected city. Default Barcelona')

args = parser.parse_args()

def getTripAdvisorLink(city, country) :

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
    }

    url = "https://duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
    }
    params = {
        "q": city + ' ' + country,
        "kl": "us-en",
    }

    r = requests.get(url, headers = headers, params = params)
    soup = BeautifulSoup(r.text, 'html.parser').find_all("a", class_="result__url", href = True)

    for link in soup:
        if "www.tripadvisor.com" in link["href"].lower() and args.city.lower() in link["href"].lower():
            return link["href"]

    return ""

# OpenAI
tripAdvisorLink = getTripAdvisorLink(args.city, args.country)
pages = tripAdvisorLink + ", https://www.thecrazytourist.com?s=" + args.city + "+" + args.country
data = planner(city = args.city, country = args.country, pages = pages, min = args.min , max = args.max, home = args.home)
print(data)

# data = """<!DOCTYPE html> <html> <head> <title>Malaga Spain</title> </head> <body> <p><b>Mapa mia:</b></p> <div>&nbsp;</div> <p><b>Driving directions:</b></p> <div class="directions"><a href="https://www.google.com/maps/dir/Barcelona/malaga"> Driving Directions from Barcelona</a></div> <div>&nbsp;</div> <p><b>Points of interest:</b></p> <ol class="places"> <li class="place"> <dl class="name"><b>Gibralfaro Castle</b></dl> <dt class="description"><i>Gibralfaro Castle is a Moorish castle located on a hilltop overlooking Malaga. It offers stunning views of the city and the coastline.</i></dt> <dt class="links"> <span class="map">Map: <a href="https://www.google.com/maps?q=Gibralfaro+Castle,+Malaga">Gibralfaro Castle</a></span> <span class="google">Google: <a href="https://www.google.com/search?q=Gibralfaro+Castle">Gibralfaro Castle</a></span> <span class="wiki">Wikipedia: <a href="https://en.wikipedia.org/wiki/Gibralfaro">Gibralfaro Castle</a></span> </dt> </li> <li class="place"> <dl class="name"><b>Alcazaba</b></dl> <dt class="description"><i>Alcazaba is a Moorish fortress palace located in the center of Malaga. It is a well-preserved example of Muslim architecture in Spain.</i></dt> <dt class="links"> <span class="map">Map: <a href="https://www.google.com/maps?q=Alcazaba,+Malaga">Alcazaba</a></span> <span class="google">Google: <a href="https://www.google.com/search?q=Alcazaba">Alcazaba</a></span> <span class="wiki">Wikipedia: <a href="https://en.wikipedia.org/wiki/Alcazaba_of_M%C3%A1laga">Alcazaba</a></span> </dt> </li> <li class="place"> <dl class="name"><b>Malaga Cathedral</b></dl> <dt class="description"><i>Malaga Cathedral, also known as La Manquita, is a Renaissance cathedral located in the heart of Malaga. It is famous for its unfinished south tower.</i></dt> <dt class="links"> <span class="map">Map: <a href="https://www.google.com/maps?q=Malaga+Cathedral">Malaga Cathedral</a></span> <span class="google">Google: <a href="https://www.google.com/search?q=Malaga+Cathedral">Malaga Cathedral</a></span> <span class="wiki">Wikipedia: <a href="https://en.wikipedia.org/wiki/Malaga_Cathedral">Malaga Cathedral</a></span> </dt> </li> </ol> <div>&nbsp;</div> <p><b>Reference pages:</b></p> <ul class="pages"> <li class="page"><a href="https://www.tripadvisor.com/Tourism-g187438-Malaga_Costa_del_Sol_Province_of_Malaga_Andalucia-Vacations.html">TripAdvisor</a></li> <li class="page"><a href="https://www.thecrazytourist.com?s=malaga+Spain">The Crazy Tourist</a></li> </ul> <div class="wikiloc">&nbsp;</div> <object data-attachment="map.kml" data="name:map" type="text/text" /> </body> </html>"""

# No API for MyMaps (but there is a hope) -> https://issuetracker.google.com/issues/35820262
# Workaround :
# - create KML file with values returned from geocode API
# - open create new map in MyMaps and import KML file
# - get link to map (paste in some dialog box)
# - update link in OneNote
# - attach file to page in  OneNote

KMLData = prepareKMLFile(args.city.title(), args.country.title(), data)

# OneNote
print("Let's insert page in OneNote")
insertPage(args.city, args.country, prepareOneNoteContent(args.city, args.country, data, KMLData))



