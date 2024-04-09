import re

from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

def planner(city, country, min: int, max : int , pages : str = "https://www.tripadvisor.com, https://www.thecrazytourist.com", model='gpt-3.5-turbo-1106') :

    print("Let's plan trip to " + city.title() + " in " + country.title())

    prompt = """I want to visit {city} in {country}.
                Please list the most important and popular tourist attractions.
                During your search use recommendations from {pages}.
                Provide name, short description. {{places}}
                Return between {min} to {max} attractions.
                Return as HTML with following structure, return only HTML:
                <ol class="places">
                    <li class="place">
                        <dl class="name"><b>{{place name}}</b></dl>
                            <dt class="description"><i>{{place description}}</i></dt>
                            <dt class="links-{{counter}}"></dt>
                        </dl>
                    </li>
                <ol>""".format(city = city, country = country, min = min, max = max, pages = pages)

    chat = ChatOpenAI(model_name=model, temperature=0.2)
    response = chat.invoke(
    [
         SystemMessage(
            content=[
                {"type": "text", "text": "You are heplfull trip advisor. Please follow instruction in customer prompt."},
            ]
        ),
        HumanMessage(
            content=[
                {"type": "text", "text": prompt},
            ]
        )
    ]
    )

    return response.content

    # example of returned data -> for testing
    #     data = """<ol class="places">
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

    m = re.search('```html(.+)```', data, re.S)
    return m.group(1)
