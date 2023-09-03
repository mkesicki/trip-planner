import os
import openai
import json
import re

from openai_functions import Conversation

openai.api_key = os.environ['OPENAI_API_KEY']

def planner(city, country, pages="https://www.tripadvisor.com, https://www.thecrazytourist.com", min : int = 2, max : int = 3, home : str = "Barcelona") :

    print("Let's plan trip to " + city.title() + " in " + country.title())

    conversation = Conversation()

    @conversation.add_function()
    def getPlacesOfInterest(city: str, country: str, pages: str, min : int, max : int, home : str) -> dict:

        """Get touristic places in a city and country.

        Args:
            city (str): The city, e.g., Barcelona
            country (str): The country to use, e.g., Spain
            pages (str): The pages where to look attractions for, e.g. https://www.thecrazytourist.com
            min (integer): Minimum number of returned attractions, e.g. 5
            max (integer): Maximum number of returned attractions, e.g. 10
            home (str): Home city for driving directions, e.g. Barcelona
        """

        return {
            "city": city,
            "country": country,
            "pages": pages,
            "min": min,
            "max": max,
            "home": home
        }

    prompt = """I want to visit {city} in {country}.
                Please list the most important and popular tourist attractions.
                During your search use recommendations from [pages].
                Provide name, short description, link to google maps, link to google and link to wikipedia. {{places}}
                Return minimum {min} atractions but no more than {max}.
                Provide links to {pages} you used to find information.
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
                        <div>&nbsp;</div>
                        <p><b>Reference pages:</b></p>
                        <ul class="pages">
                            <li class="page">{{page}}</li>
                        </ul>
                        <div class="wikiloc">&nbsp;</div>
                        <object
                            data-attachment="map.kml"
                            data="name:map"
                            type="text/text" />
                    </body>
                </html>
               """.format(city = city, country = country, pages = pages, home = home, min = min, max = max)

    return conversation.ask(prompt)
