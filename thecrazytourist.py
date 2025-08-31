import requests
import json
from typing import Dict
from bs4 import BeautifulSoup

MAX_DESCRIPTION_LENGTH = 200
def search_crazy_tourist(city: str, country: str) -> Dict:

    city = "Barcelona"
    country = "Spain"

    results = []
    follow = f"https://www.thecrazytourist.com?s={city} {country}"

    r = requests.get(follow)
    soup = BeautifulSoup(r.text, 'html.parser').find_all("a", {'rel': 'bookmark'}, href = True)

    for link in soup:
        if city.lower() in link['href'].lower() :
            follow = link["href"]
            break

    response = requests.get(follow)

    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        h2_elements = soup.find_all('h2')

        for h2 in h2_elements:
            h2_text = h2.get_text(strip=True)
            paragraphs = []
            current_element = h2.next_sibling

            while current_element and len(paragraphs) < 5:

                if hasattr(current_element, 'name'):
                    if current_element.name == 'p':
                        para_text = current_element.get_text(strip=True)
                        if para_text:
                            paragraphs.append(para_text)

                current_element = current_element.next_sibling

            description = "\n".join(paragraphs)
            if len(description) > MAX_DESCRIPTION_LENGTH:
                description = description[:MAX_DESCRIPTION_LENGTH] + "..."

            results.append({
                'name': h2_text,
                'description': description
            })

    except requests.RequestException as e:
        pass
    except Exception as e:
        pass

    return {"atrractions": results}

if __name__ == "__main__":

    city = "Barcelona"
    country = "Spain"

    attractions = search_crazy_tourist(city, country)