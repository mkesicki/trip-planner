import logging
import requests
import webbrowser
import easygui
import time
import os
import pyperclip
import webbrowser

from utils import *

def get_token():

    try:
        with open("/tmp/onenote.txt", "r") as f:
            return f.read()
    except:
        logging.error("No token found. Exiting.")
        exit(1)

def prepareOneNoteContent(city : str, country: str, data : str, kml : str, home: str, pages : str) -> str :

    data = addLinksToPlaces(city, country, data)

    header = """--MyAppPartBoundary
Content-Disposition:form-data; name="Presentation"
Content-Type:text/html; charset="utf-8"

<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>{city} {country}</title>
    </head>
    <body>
        <p><b>Mapa mia:</b></p>
        <div>&nbsp;</div>
        <p><b>Driving directions:</b></p>
        <div class="directions"><a href="https://www.google.com/maps/dir/{home}/{city}">Driving Directions from {home}</a></div>
        <div>&nbsp;</div>
        <p><b>Points of interest:</b></p>""".format(city = city.title(), country = country.title(), home = home.title())

    wikiloc = {
        "placeLoop" : "https://www.wikiloc.com/wikiloc/map.do?place="+ city + "&page=1&act=1%2C43%2C57%2C2%2C47%2C144%2C135&sto=4&loop=1",
        "placeNoLoop" : "https://www.wikiloc.com/wikiloc/map.do?place="+ city + "&page=1&act=1%2C43%2C57%2C2%2C47%2C144%2C135&sto=4&loop=0",
        "queryLoop": "https://www.wikiloc.com/wikiloc/map.do?q=" + city + "&page=1&act=1%2C43%2C57%2C2%2C47%2C144%2C135&sto=4&loop=1",
        "queryNoLoop": "https://www.wikiloc.com/wikiloc/map.do?q=" + city + "&page=1&act=1%2C43%2C57%2C2%2C47%2C144%2C135&sto=4&loop=0"
    }

    pagesHTML = ""
    for page in pages.split(","):
         pagesHTML = pagesHTML + "<li class=\"page\"><a href=\"" + page + "\">" + page + "</a></li>"

    pagesContent = """<div>&nbsp;</div>
        <p><b>Reference pages:</b></p>
        <ul class="pages">
            {pagesHTML}
        </ul>""".format(pagesHTML = pagesHTML)

    wikilocContent = """<div>&nbsp;</div>
        <p><b>Hiki y Bici (WikiLoc):<b></p>
        <div>
            <ul>
                <li>Place Loop: <a href="{pl}">Link</a></li>
                <li>Place No Loop: <a href="{pnl}">Link</a></li>
                <li>Query Loop: <a href="{ql}">Link</a></li>
                <li>Query No Loop: <a href="{qnl}">Link</a></li>
            </ul>
        </div>
        <object data-attachment="map.kml" data="name:map" type="text/xml" />""".format(pl = wikiloc["placeLoop"], pnl = wikiloc["placeNoLoop"], ql = wikiloc["queryLoop"], qnl = wikiloc["queryNoLoop"])

    page = header + data + pagesContent + wikilocContent + """</body></html>
--MyAppPartBoundary
Content-Disposition:form-data; name="map"
Content-Type: text/xml; charset="utf-8"

{kml}
--MyAppPartBoundary--
""".format(kml = kml)

    return page

def insertPage(city, country, page):

    token = get_token()

    sectionId = os.environ['OneNote_Section_Id']

    headers = {'Authorization': 'Bearer ' + token}

    logging.info("Check if page exists")

    query = (city + " " + country).lower()

    query_params = {
        "filter": f"contains(tolower(title), '{query}')",
        "select":"id,title",
        "top": 1
    }

    # https://graph.microsoft.com/v1.0/me/onenote/sections/{sectionId}/pages?filter=contains(tolower(title),'madrid')&top=1&$select=id,title

    response = requests.get(f'https://graph.microsoft.com/v1.0/me/onenote/sections/{sectionId}/pages', headers = headers, params=query_params)

    # check if page exists
    for title in response.json()["value"]:

        pageTitle = title["title"].lower()

        if pageTitle == query or pageTitle == "[V] " + query or city.lower() in pageTitle:
            logging.info("Page for {query} already exists : [{id}]. Will not add new one.".format(query = query.replace(" ", " in "), id = title["id"]))

            return

    #manage map creation
    webbrowser.open("https://www.google.com/maps/d/mp?hl=en&authuser=0&state=create")
    pyperclip.copy(query.title())
    time.sleep(15)
    linkMyMap = easygui.enterbox("Please paste link to newly created map (name should be in clipboard)")

    if linkMyMap == None or linkMyMap == "":

        logging.error("No link to map provided. Exiting.")
        exit(1)

    page = page.replace("<p><b>Mapa mia:</b></p>", "<p><b>Mapa mia:</b> <a href=\"{link}\" > map</a></p>".format(link = linkMyMap ))

    logging.info("Create new page in OneNote")

    headers = {
        'Authorization': 'Bearer ' + token,
        "Content-Type": "multipart/form-data; boundary=MyAppPartBoundary"
    }

    response = requests.post("https://graph.microsoft.com/v1.0/me/onenote/sections/" + sectionId + "/pages", data = page.replace("\n", "\r\n").encode("utf-8"), headers = headers);

    logging.info(response.json())

    os.remove("/tmp/onenote.txt")

    return ""
