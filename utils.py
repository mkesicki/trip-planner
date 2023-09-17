import requests

from bs4 import BeautifulSoup

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
        if "www.tripadvisor.com" in link["href"].lower() and city.lower() in link["href"].lower():
            return link["href"]

    return ""

def getPlacesFromHTML(city : str, country : str, content : str) -> list:

    places = BeautifulSoup(content, 'html.parser').find_all("ol", class_="places")[0].find_all("li")
    body = []

    for place in places:

        body.append(
            {
                "name": place.find_all("dl", class_="name")[0].text + " " + city + ", " + country,
                "description": place.find_all("dt", class_="description")[0].text
            })

    return body

def addLinksToPlaces(city : str, country : str, content : str) -> str:

    places = BeautifulSoup(content, 'html.parser').find_all("ol", class_="places")[0].find_all("li")

    i =1
    for place in places:

            name = place.find_all("dl", class_="name")[0].text
            links = """
                <dt class="links-{counter}">
                    <span class="map"><a href="https://www.google.com/maps?q={name},{city},{country}">Google Maps</a></span>
                    | <span class="google"><a href="https://www.google.com/search?q={name}">Google Search</a></span>
                    | <span class="wiki"><a href="https://en.wikipedia.org/w/index.php?search={name}">Wikipedia</a></span>
                </dt>
            """.format(name = name.replace(" ", "+"), city = city, country = country, counter = i)

            content = content.replace("<dt class=\"links-{counter}\"></dt>".format(counter = i), links)
            i = i + 1

    return content

def getCrazyTouristLink(city, country) :

    r = requests.get("https://www.thecrazytourist.com?s=" + city + "+" + country)
    soup = BeautifulSoup(r.text, 'html.parser').find_all("a", {'rel': 'bookmark'}, href = True)

    for link in soup:

        if city.lower() in link['href'].lower() :
            return link["href"]

    return ""

def getReferencePages(city : str , country : str) -> list:

    return [getTripAdvisorLink(city, country) , getCrazyTouristLink(city, country)]

