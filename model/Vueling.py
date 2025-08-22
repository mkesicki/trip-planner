import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from .data_classes import SearchQuery


class Vueling:

    def remove_month_leading_zero(self, date_str):
        if len(date_str) == 8:
            year = date_str[:4]
            month = date_str[4:6].lstrip('0') or '0'  # Keep '0' if month becomes empty
            day = date_str[6:8]
            return year + month + day
        return date_str

    def parse(self, query: SearchQuery):

        # they count from 0 -> January is 0
        startMonth = query.start_date.month - 1
        endMonth = query.end_date.month - 1

        url = query.params.get("url")
        self.config = query.params.get("params")

        startTrip = query.start_date.strftime(query.params.get("dateFormat"))
        endTrip = query.end_date.strftime(query.params.get("dateFormat"))

        # Replace the month part with startMonth/endMonth
        startTrip = startTrip.replace(f"{query.start_date.month:02d}", f"{startMonth:02d}")
        endTrip = endTrip.replace(f"{query.end_date.month:02d}", f"{endMonth:02d}")

        startTrip = self.remove_month_leading_zero(startTrip)
        endTrip = self.remove_month_leading_zero(endTrip)

        logging.info("Open Browser " + url)
        browser = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        browser.get(url)
        time.sleep(10)


        # accept cookies
        try:
            if "cookiesAccept" in self.config:
                button = browser.find_element(By.ID, self.config.get("cookiesAccept"))
                browser.execute_script("arguments[0].click();", button)
        except:
            pass

        departure = browser.find_element(By.ID, self.config.get("departure"))
        departure.send_keys(query.from_city)
        confirm = browser.find_element(By.CLASS_NAME, "vy-list-dropdown_item_button")
        browser.execute_script("arguments[0].click();", confirm)
        time.sleep(2)

        arrival = browser.find_element(By.ID, self.config.get("arrival"))
        arrival.send_keys(query.to_city)
        confirm = browser.find_element(By.CLASS_NAME, "vy-list-dropdown_item_button")
        browser.execute_script("arguments[0].click();", confirm)
        time.sleep(2)

        self.findDate(browser, startTrip)
        if not query.round_trip:
            logging.info("Handle one way trip")
            browser.find_element(By.ID, self.config.get("oneWay")).click()
            browser.implicitly_wait(5)  # seconds
            browser.find_element(By.ID, f"calendarDaysTable{startTrip}").click()
        else:
            browser.find_element(By.ID, f"calendarDaysTable{startTrip}").click()
            browser.implicitly_wait(5)  # seconds
            self.findDate(browser, endTrip)

            browser.find_element(By.ID, f"calendarDaysTable{endTrip}").click()


        # handle passengers number
        passengers_input = browser.find_element(By.ID, self.config.get("passengersSelector"))
        browser.execute_script("arguments[0].click();", passengers_input)
        time.sleep(2)
        currentAdults = 1
        while currentAdults < query.adults:
            browser.find_element(By.ID, self.config.get("adults")).click()
            currentAdults += 1

        # submit form
        browser.find_element(By.ID, self.config.get("submit")).click()

        return ""

    def findDate(self, browser, date):

        max_attempts = 25
        print(f"Looking for: calendarDaysTable{date}")
        for attempt in range(1, max_attempts + 1):
            try:
                browser.find_element(By.ID, f"calendarDaysTable{date}")
                return True
            except NoSuchElementException:
                if attempt == max_attempts:
                    raise ValueError(f"Date not found after {max_attempts} attempts")
                browser.find_element(By.ID, self.config.get("dateForward")).click()

        return False
