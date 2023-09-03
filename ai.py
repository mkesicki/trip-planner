import os
import openai
import json
import re

from openai_functions import Conversation
# from openai_functions import FunctionWrapper
# from openai_functions import BasicFunctionSet

openai.api_key = os.environ['OPENAI_API_KEY']

def askOpenAI(city, country):

    print("Let's plan trip to", city, "in", country)

    # message = openai.ChatCompletion.create(
    #   model="gpt-3.5-turbo",
    #   messages=[
    #     {"role": "user", "content": "I want to visit " + city + " [city] in " + country + " [country]. Please list the most important and popular attractions. During your search use recommendations from https://www.tripadvisor.com [Page1] & https://www.thecrazytourist.com [Page2] as reference. Provide short description, and link to google maps. Provide minimum 15 items (if accessible) but not more than 20. Finish each listed item  '**' characters. Provide link to [city] in [country] on webpages [Page1] and [Page2]. Additional provide link to driving directions to the [city] from Barcelona. Please provide search link to [city] on [Page1] and [Page2]"}
    #   ]
    # )

    message = '{"id": "chatcmpl-7szK8fs4FH8j3vvYvrkHvrMtQ16EZ","object": "chat.completion","created": 1693339796,"model": "gpt-3.5-turbo-0613","choices": [{"index": 0,"message": {"role": "assistant","content": "Here is a list of the most important and popular attractions in Malaga, Spain, based on recommendations from TripAdvisor [Page1] and The Crazy Tourist [Page2]:\n\n1. Alcazaba de Malaga: A stunning Moorish fortress offering panoramic views of the city. Google Maps: https://goo.gl/maps/pWZ6CCK8dwnMMaxy9\n\n2. Museo Picasso Malaga: This museum displays a vast collection of Picasso artwork. Google Maps: https://goo.gl/maps/9d4ontCQSi2T6SG68\n\n3. Malaga Cathedral: Known for its impressive architecture and stunning interior. Google Maps: https://goo.gl/maps/Sx9QbC33hfygkNnJ6\n\n4. Castillo de Gibralfaro: A fortress with a rich history and incredible views. Google Maps: https://goo.gl/maps/1ZHaZLGeceLVToYPA\n\n5. Roman Theatre: An ancient Roman amphitheater that dates back to the 1st century BC. Google Maps: https://goo.gl/maps/YL94qj4BLkPywDew8\n\n6. Museo Carmen Thyssen: Art museum showcasing a wide range of Spanish artists. Google Maps: https://goo.gl/maps/8nRYazd6qS7anJUh7\n\n7. Malaga Park: A peaceful park with beautiful gardens, fountains, and sculptures. Google Maps: https://goo.gl/maps/DHirDPs1oc3t5PJ7A\n\n8. Calle Larios: The main shopping street in Malaga, lined with boutiques and cafes. Google Maps: https://goo.gl/maps/H895jGMCAzD1wNjr7\n\n9. Mercado Central de Atarazanas: A bustling market with a wide variety of fresh produce, meats, and seafood. Google Maps: https://goo.gl/maps/p5BQ6tRUr6rWAnGw7\n\n10. Jardin Botanico-Historico La Concepcion: A stunning botanical garden with beautiful plants and landscapes. Google Maps: https://goo.gl/maps/98tWMytnt8LmX2xs7\n\n11. Malagueta Beach: A popular city beach with golden sand and a lively atmosphere. Google Maps: https://goo.gl/maps/RU6ZJWwCkWdD8Dbs6\n\n12. Plaza de la Merced: A vibrant square with cafes, restaurants, and a statue of Picasso. Google Maps: https://goo.gl/maps/sjNvbrNPvYrQGFpT7\n\n13. Malaga Port: A lively area with bars, restaurants, and boat tours. Google Maps: https://goo.gl/maps/4TrqUuVqQkyqCCTk6\n\n14. Museo Automovilistico y de la Moda: A unique museum displaying vintage cars and fashion. Google Maps: https://goo.gl/maps/nMa4h65qxfDJXFfPA\n\n15. Plaza de Toros de la Malagueta: An iconic bullring where you can learn about Spanish bullfighting culture. Google Maps: https://goo.gl/maps/pJXPMWPaowKkbXor6\n\nTo access the search link for Malaga on TripAdvisor [Page1], click here: https://www.tripadvisor.com/Search?q=Malaga\n\nTo access the search link for Malaga on The Crazy Tourist [Page2], click here: https://www.thecrazytourist.com/?s=Malaga\n\nFor driving directions from Barcelona to Malaga, click here: https://www.google.com/maps/dir/Barcelona/Malaga/"},"finish_reason": "stop"}],"usage": {"prompt_tokens": 152,"completion_tokens": 780,"total_tokens": 932}}'
    body = json.loads(message.replace('\n', '\\n'))
    # print(body["choices"][0]["message"]["content"])

    return body["choices"][0]["message"]["content"]

def parseReply(message):

    lines = message.split("\n");

    m = re.search('(https:\/\/.+\/)', lines[-1])
    google = m.group(0)

    m = re.search('(https:\/\/.+)', lines[-3])
    crazyToursit = m.group(0)

    m = re.search('(https:\/\/.+)', lines[-5])
    tripAdvisor = m.group(0)

    places = list(filter(lambda x : x != "", lines[2:-6]))

    # print("google: " + google);
    # print("trip: " + tripAdvisor);
    # print("crazy: " + crazyToursit);
    # print(places)

    return {"places": places, "google": google, "tripAdvisor":tripAdvisor, "crazyTourist": crazyToursit}

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
