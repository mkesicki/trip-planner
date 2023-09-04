import requests
import webbrowser
import easygui
import time
import os
import re

def get_token():

    print("Get access token from graph explorer")

    #wasted so many time trying to get token programmatically
    webbrowser.open("https://developer.microsoft.com/en-us/graph/graph-explorer")
    time.sleep(7)
    token = easygui.enterbox("Please paste access token from graph explorer")

    if token == None or token == "":
        print("No token provided. Exiting.")
        exit(1)

    return token

def prepareOneNoteContent(city : str, country : str, data : str, kml : str) -> str :

    wikiloc = {
        "placeLoop" : "https://www.wikiloc.com/wikiloc/map.do?place="+ city + "&page=1&act=1%2C43%2C57%2C2%2C47%2C144%2C135&sto=4&loop=1",
        "placeNoLoop" : "https://www.wikiloc.com/wikiloc/map.do?place="+ city + "&page=1&act=1%2C43%2C57%2C2%2C47%2C144%2C135&sto=4&loop=0",
        "queryLoop": "https://www.wikiloc.com/wikiloc/map.do?q=" + city + "&page=1&act=1%2C43%2C57%2C2%2C47%2C144%2C135&sto=4&loop=1",
        "queryNoLoop": "https://www.wikiloc.com/wikiloc/map.do?q=" + city + "&page=1&act=1%2C43%2C57%2C2%2C47%2C144%2C135&sto=4&loop=0"
    }

    wikilocContent = """
       <div>&nbsp;</div>
        <p><b>Hiki y Bici (WikiLoc):<b></p>
        <div>
            <ul>
                <li>Place Loop: <a href="{pl}">Link</a></li>
                <li>Place No Loop: <a href="{pnl}">Link</a></li>
                <li>Query Loop: <a href="{ql}">Link</a></li>
                <li>Query No Loop: <a href="{qnl}">Link</a></li>
            </ul>
        </div>
        """.format(pl = wikiloc["placeLoop"], pnl = wikiloc["placeNoLoop"], ql = wikiloc["queryLoop"], qnl = wikiloc["queryNoLoop"])

    data = data.replace("<div class=\"wikiloc\">&nbsp;</div>", wikilocContent)

    page = """--MyAppPartBoundary
Content-Disposition: form-data; name="Presentation"
Content-Type: text/html

"""
    page = page + data + """

--MyAppPartBoundary
Content-Disposition: form-data; name="map"
Content-Type: text/text

{kml}
--MyAppPartBoundary--
""".format(kml = kml)

    return page.replace("\n", "\r\n")

def insertPage(city, country, page):

    token = get_token()

    # token = ""

    sectionId = os.environ['OneNote_Section_Id']

    headers = {'Authorization': 'Bearer ' + token}

    print("Check if page exists")

    query = (city + " " + country).tolower()

    response = requests.get('https://graph.microsoft.com/v1.0/me/onenote/pages?search="'+ query +'"&select=title,id', headers = headers)

    # check if page exists
    for title in response.json()["value"]:

        pageTitle = title["title"].tolower()

        if pageTitle == query or pageTitle == "[V] " + query or pageTitle == "[V] " + city.tolower():
            print("Page for {query} already exists : [{id}]. Will not add new one.".format(query = query.replace(" ", " in "), id = title["id"]))

            return

    # manage map creation
    webbrowser.open("https://www.google.com/maps/d/mp?hl=en&authuser=0&state=create")
    time.sleep(20)
    linkMyMap = easygui.enterbox("Please paste link to newly created map")

    if linkMyMap == None or linkMyMap == "":

        print("No link to map provided. Exiting.")
        exit(1)

    page = page.replace("<p><b>Mapa mia:</b></p>", "<p><b>Mapa mia:</b> <a href=\"{link}\" > map</a></p>".format(link = linkMyMap ))

    print("Create new page in OneNote")

    headers = {'Authorization': 'Bearer ' + token, "Content-Type": "multipart/form-data; boundary=MyAppPartBoundary"}

    response = requests.post("https://graph.microsoft.com/v1.0/me/onenote/sections/" + sectionId + "/pages", data = page, headers = headers);

    print(response.json())

    return ""