import time
import datetime
import webbrowser

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

class OkMobility:

    def parse(self, fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : datetime.date, endDate : datetime.date, adults : int, params : dict):

        startTrip = startDate.strftime(params.get("dateFormat"))
        endTrip = endDate.strftime(params.get("dateFormat"))

        startTime = startDate.strftime("%H:00")
        endTime = endDate.strftime("%H:00")

        self.url = params.get("initUrl")
        self.config = params.get("params")

        pickupId = self.getLocation(fromCity)

        if (roundTrip == True):
            dropoffId = pickupId
        else:
            dropoffId = self.getLocation(toCity)

        print("pikup location: " + pickupId)
        print("dropoff location: " + dropoffId)

        url =  params.get("url")
        url = url + params.get("queryParams")
        url = url.format(id = pickupId, dropoffId = dropoffId, departure = fromCity, arrival = toCity, dateFrom = startTrip, dateBack = endTrip, startTime = startTime, endTime = endTime)

        print("url: " + url)
        webbrowser.open(url)

        return ""

    def getLocation(self, city : str):

        print("Open Browser " + self.url + " in browser")

        options = Options()
        options.add_argument("-headless") # Here
        browser = webdriver.Firefox(options=options)
        browser.get(self.url)
        browser.implicitly_wait(15) # seconds

        # # accept cookies
        # if "cookiesAccept" in config:
        #     cookiesAccept = browser.find_element(By.ID, config.get("cookiesAccept"))
        #     cookiesAccept.click()

        departure = browser.find_element(By.ID, self.config.get("departure"))
        departure.send_keys(city)
        time.sleep(2)

        command = "document.querySelector('.tt-suggestion').click();"
        browser.execute_script(command)
        browser.implicitly_wait(10) # seconds

        image = browser.find_element(By.CSS_SELECTOR, "img.rounded-circle")
        pickupId = image.get_property("alt")
        browser.close()

        return pickupId
