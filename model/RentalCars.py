import logging
import datetime
from .data_classes import SearchQuery
from playwright.sync_api import sync_playwright

class RentalCars:

    def parse(self, query: SearchQuery):
        # --- Step 1: Construct the URL ---
        time_params = self.parseDate(query.start_date, "pu")
        time_params += self.parseDate(query.end_date, "do")

        pickup_location = self.getLocation(f"{query.from_city} {query.pickup_place or ''}", query.from_country)

        if query.round_trip:
            dropoff_location = pickup_location
        else:
            dropoff_location = self.getLocation(f"{query.to_city} {query.return_place or ''}", query.to_country)

        base_url = "https://www.rentalcars.com/search-results"
        query_params = {
            "cor": "es",
            "driversAge": "30",
            "pickUpLocationName": pickup_location,
            "dropOffLocationName": dropoff_location,
        }
        url = f"{base_url}?{'&'.join([f'{k}={v}' for k, v in query_params.items()])}{time_params}"

        logging.info(f"Opening URL with Playwright and interacting with the page: {url}")

        p = sync_playwright().start()
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        try:
            page.goto(url)
            logging.info("Page loaded.")

            # --- Handle the cookie banner ---
            try:
                cookie_button_selector = "#onetrust-accept-btn-handler"
                logging.info("Waiting for cookie consent button...")
                page.wait_for_selector(cookie_button_selector, timeout=10000)
                page.locator(cookie_button_selector).click()
                logging.info("Cookie banner accepted.")
            except Exception as e:
                logging.warning(f"Could not find or click cookie button: {e}")

            # --- Automation Sequence ---

            # 1. Fill the input field
            input_selector = ".SearchBoxFieldAutocomplete_input"
            pickup_city = query.from_city

            logging.info(f"Waiting for input field with class: {input_selector}")
            page.wait_for_selector(input_selector, timeout=10000)

            logging.info(f"Filling input field with: '{pickup_city}'")
            page.locator(input_selector).first.fill(pickup_city)

            # 2. Select the location type
            if query.pickup_place == "train_station":
                location_type_label = "Ciudad"
            else:
                location_type_label = "Aeropuerto"

            try:
                logging.info(f"Selecting location type: '{location_type_label}'")
                location_type_selector = f"span.SM_148f3cbb:has-text('{location_type_label}')"
                page.locator(location_type_selector).click()
                logging.info("Location type selected successfully.")
            except Exception as e:
                logging.error(f"Could not select the location type '{location_type_label}': {e}")

            # 3. Click the submit button
            try:
                submit_button_selector = 'button[type="submit"]'
                logging.info("Clicking the search button...")
                page.locator(submit_button_selector).click()
                logging.info("Search button clicked.")
            except Exception as e:
                logging.error(f"Could not click the search button: {e}")


            logging.info("Automation complete. The browser will remain open.")

        except Exception as e:
            logging.error(f"An error occurred during Playwright operation: {e}")
            logging.info("The browser will remain open for inspection despite the error.")

        return ""

    def getLocation(self, city: str, country: str):
        return f"{city.strip()},{country}"

    def parseDate(self, date: datetime.datetime, prefix: str) -> str:
        return f"&{prefix}Day={date.day}&{prefix}Hour={date.hour}&{prefix}Minute={date.minute}&{prefix}Month={date.month}&{prefix}Year={date.year}"