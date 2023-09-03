import os
import openai
import json
import re

from openai_functions import Conversation

openai.api_key = os.environ['OPENAI_API_KEY']

conversation = Conversation()

@conversation.add_function
def getPlacesOfInterest(city: str, country: str, pages: str, max : int, home : str) -> dict:

        """Get touristic places in a city and country.

        Args:
            city (str): The city, e.g., Barcelona
            country (str): The country to use, e.g., Spain
            pages (str): The pages where to look attractions for, e.g. https://www.thecrazytourist.com
            max (integer): Maximum number of returned attractions, e.g. 10
            home (str): Home city for driving directions, e.g. Barcelona
        """

        return {
            "city": city,
            "country": country,
            "pages": pages,
            "max": max,
            "home": home
        }

def planner(city, country, max : int , home : str, pages : str = "https://www.tripadvisor.com, https://www.thecrazytourist.com") :

    print("Let's plan trip to " + city.title() + " in " + country.title())

    prompt = """I want to visit {city} in {country}.
                Please list the most important and popular tourist attractions.
                During your search use recommendations from {pages}.
                Provide name, short description, link to google maps, link to google and link to wikipedia. {{places}}
                Return maximum {max} attractions.
                Return as HTML with following structure (do not add code snippet):
                <!DOCTYPE html>
                <html>
                    <head>
                        <title>{{city}} {{country}}</title>
                    </head>
                    <body>
                        <p><b>Mapa mia:</b></p>
                        <div>&nbsp;</div>
                        <p><b>Driving directions:</b></p>
                        <div class="directions"><a href="https://www.google.com/maps/dir/{home}/{city}">Driving Directions from {home}</a></div>
                        <div>&nbsp;</div>
                        <p><b>Points of interest:</b></p>
                        <ol class="places">
                            <li class="place">
                                <dl class="name"><b>{{place name}}</b></dl>
                                    <dt class="description"><i>{{place description}}</i></dt>
                                    <dt class="links">
                                        <span class="map">{{place linkGMap}}</span> * <span class="google">{{ place linkGoogle}}</span> * <span class="wiki">{{ place linkWiki}}</span>
                                    </dt>
                                </dl>
                            </li>
                        <ol>
                        <div>[REPLACE HERE]</div>
                    </body>
                </html>
               """.format(city = city, country = country, home = home, max = max, pages = pages)

    data =  conversation.ask(prompt)

    # sometimes reply is duplicated
    if data.count("<html>") > 1:

        m = re.search('(<!DOCTYPE html>.+</html>).', data, flags = re.S)
        print("*** more than 1 html tag ***")
        if m is not None:
            data = m.group(0)

    # removed this from prompt to see if it helps to get better results
    pagesHTML = ""
    for page in pages.split(","):
         pagesHTML = pagesHTML + "<li class=\"page\"><a href=\"" + page + "\">" + page + "</a></li>"

    insert = """
        <div>&nbsp;</div>
        <p><b>Reference pages:</b></p>
        <ul class="pages">
            {pagesHTML}
        </ul>
        <div class="wikiloc">&nbsp;</div>
        <object
            data-attachment="map.kml"
            data="name:map"
            type="text/text" />
    """.format(pagesHTML = pagesHTML)
    data = data.replace("<div>[REPLACE HERE]</div>", insert)

    print(data)

    return data
