import datetime
import requests
import webbrowser

from dateutil.relativedelta import relativedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class Kayakcar:

    def parse(self, fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : datetime.date, endDate : datetime.date, adults : int, params : dict):


        startTrip = startDate.strftime(params.get("dateFormat"))
        endTrip = endDate.strftime(params.get("dateFormat"))

        timeStart = startDate.strftime("%H")
        timeEnd = endDate.strftime("%H")

        searchUrl ="https://www.kayak.es/mvm/smartyv2/search?f=j&s=car&where={city}&lc_cc={contry}".format(city = fromCity, contry = fromCountry)
        response = requests.post(searchUrl)
        first = response.json()[0]
        fromCity = fromCity + "-c" + first["id"]

        if roundTrip != "on":
            print("serch return point")
            searchUrl ="https://www.kayak.es/mvm/smartyv2/search?f=j&s=car&where={city}&lc_cc={contry}".format(city = toCity, contry = toCountry)
            response = requests.post(searchUrl)
            first = response.json()[0]
            toCity = toCity + "-c" + first["id"]

        url = params.get("url") if (roundTrip == "on") else  params.get("urlOneWay")
        url = url + params.get("queryParams")
        url = url.format(departure = fromCity, arrival = toCity, dateFrom = startTrip, dateBack = endTrip, timeStart = timeStart, timeEnd = timeEnd)

        print("url: " + url)
        webbrowser.open(url)

        return ""