import os
import openai
import json
import re

from openai_functions import Conversation

openai.api_key = os.environ['OPENAI_API_KEY']

conversation = Conversation(model='gpt-3.5-turbo-16k')

@conversation.add_function
def getPlacesOfInterest(city: str, country: str, pages: str, max : int, min : int) -> dict:

        """Get touristic places in a city and country.

        Args:
            city (str): The city, e.g., Barcelona
            country (str): The country to use, e.g., Spain
            pages (str): The pages where to look attractions for, e.g. https://www.thecrazytourist.com
            max (integer): Maximum number of returned attractions, e.g. 10
            min (integer): Minimum number of returned attractions, e.g. 5

        """

        return {
            "city": city,
            "country": country,
            "pages": pages,
            "max": max,
            "min": min,
        }

def planner(city, country, min: int, max : int , pages : str = "https://www.tripadvisor.com, https://www.thecrazytourist.com") :

    print("Let's plan trip to " + city.title() + " in " + country.title())

    prompt = """I want to visit {city} in {country}.
                Please list the most important and popular tourist attractions.
                During your search use recommendations from {pages}.
                Provide name, short description. {{places}}
                Return between {min} to {max} attractions.
                Return as HTML with following structure:
                <ol class="places">
                    <li class="place">
                        <dl class="name"><b>{{place name}}</b></dl>
                            <dt class="description"><i>{{place description}}</i></dt>
                            <dt class="links-{{counter}}"></dt>
                        </dl>
                    </li>
                <ol>
               """.format(city = city, country = country, min = min, max = max, pages = pages)

    data =  conversation.ask(prompt)

    # example of returned data -> for testing

    #      data = """<ol class="places">
    #     <li class="place">
    #         <dl class="name"><b>Alcazaba</b></dl>
    #         <dt class="description"><i>The Alcazaba is a medieval fortress in Almeria, Spain. It was built by the Moors in the 10th century and is one of the largest Muslim fortifications in Spain. The fortress offers panoramic views of the city and the Mediterranean Sea. Visitors can explore its impressive walls, towers, gardens, and courtyards.</i></dt>
    #         <dt class="links-1"></dt>
    #     </li>
    #     <li class="place">
    #         <dl class="name"><b>Cathedral of Almeria</b></dl>
    #         <dt class="description"><i>The Cathedral of Almeria is a splendid example of Spanish Renaissance architecture. Built between the 16th and 18th centuries, it features a unique mix of Gothic, Renaissance, and Baroque styles. The cathedral houses beautiful chapels, a museum, and the tomb of the Catholic Monarchs. Its striking towers and ornate facade make it a must-visit attraction in Almeria.</i></dt>
    #         <dt class="links-2"></dt>
    #     </li>
    # </ol>"""

    return data