import time
import datetime
import webbrowser

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

class Ok:

    def parse(self, fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : datetime.date, endDate : datetime.date, adults : int, params : dict):

        startTrip = startDate.strftime(params.get("dateFormat"))
        endTrip = endDate.strftime(params.get("dateFormat"))

        startTime = startDate.strftime("%H:00")
        endTime = endDate.strftime("%H:00")

        self.url = params.get("initUrl")
        self.config = params.get("params")

        pickupId = self.getLocation(fromCity)

        if (roundTrip == "on"):
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


    # SIXT
        # document.querySelector('div.jFAhhe').click()
        # document.querySelector("time[datetime='2023-09-30']").click()
        # https://www.sixt.com/betafunnel/#/offerlist?zen_pu_location=70c0736f-50da-498e-b7bf-23964501070a&zen_do_location=97abdf8c-e423-447b-80d6-20f0f515953c&zen_pu_title=Barcelona%20%20Sants%20Train%20Station&zen_do_title=Barcelona%20%20Sants%20Train%20Station&zen_pu_time=2023-09-25T12%3A30&zen_do_time=2023-10-01T08%3A30&zen_pu_branch_id=BRANCH%3A2220&zen_do_branch_id=BRANCH%3A2220&zen_offer_matrix_id=ed11346e-df5a-4ccc-bcb3-c0a1bf420a45&zen_vehicle_type=car&zen_pickup_country_code=ES&zen_resident_country_required=false&zen_filters=%7B%22group_type%22%3A%5B%5D%2C%22transmission_type%22%3A%5B%7B%22key%22%3A%22transmission_type%22%2C%22value%22%3A%22TRANSMISSION_TYPE_AUTOMATIC%22%7D%5D%2C%22passengers_count%22%3A%5B%7B%22value%22%3A%222%22%2C%22key%22%3A%22passengers_count%22%7D%5D%2C%22bags_count%22%3A%5B%7B%22value%22%3A%220%22%2C%22key%22%3A%22bags_count%22%7D%5D%2C%22minimum_driver_age%22%3A%5B%7B%22value%22%3A%2231%22%2C%22key%22%3A%22minimum_driver_age%22%7D%5D%7D&zen_resident_country_code=&zen_order_is_ascending=true&zen_order_by=sort_order&zen_booking_id=9253c219-6e0c-4351-9292-7bcd6d6c26db
        #

# POST
# https://grpc-prod.orange.sixt.com/com.sixt.service.rent_booking.api.SearchService/SuggestLocations
# {"query":"barcelona"}