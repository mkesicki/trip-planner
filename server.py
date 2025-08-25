import os
import json
import datetime
import time
import sys
import webbrowser
import requests
import msal
import concurrent.futures
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from country_list import countries_for_language
from model.Parser import Parser
from model.data_classes import TripRequest, TransportDetails, AccommodationDetails, SearchQuery
from dataclasses import replace

import logging
from utils import setup_logging

setup_logging()

# --- Flask App ---
countries = dict(countries_for_language('en'))
client_id = os.environ.get("ONE_NOTE_CLIENT_ID")
client_secret = os.environ.get("ONE_NOTE_CLIENT_SECRET")
authority = "https://login.microsoftonline.com/common"
redirect_uri = os.environ.get("ONE_NOTE_REDIRECT_URI")
scopes = ["https://graph.microsoft.com/Notes.Read", "https://graph.microsoft.com/Notes.ReadWrite"]

app = Flask(__name__)
app.secret_key = os.urandom(24)
app_client = msal.ConfidentialClientApplication(
    client_id=client_id,
    client_credential=client_secret,
    authority=authority
)

# --- Helper Functions ---
def parse_request(args: dict) -> TripRequest:
    """Parses the request arguments and returns a TripRequest object."""

    transport_start_type = args.get('transportStart')
    transport_end_type = args.get('transportEnd')

    transport_start = TransportDetails(
        transport_type=transport_start_type,
        pickup_place=args.get('pickupPlace') if transport_start_type == 'cars' else None
    )

    transport_end = TransportDetails(
        transport_type=transport_end_type,
        return_place=args.get('returnPlace') if transport_end_type == 'cars' else None
    )

    if args.get('roundtrip') == "on":
        transport_end.return_place = transport_start.pickup_place

    places_list = args.get('places[]', [])
    nights_list = args.get('nights[]', [])
    trip_countries_list = args.get("countries[]", [])

    accommodations = [
        AccommodationDetails(
            place=place,
            nights=int(nights_list[i]),
            country=trip_countries_list[i]
        ) for i, place in enumerate(places_list)
    ]

    return TripRequest(
        from_country=args.get('fromCountry'),
        to_country=accommodations[-1].country if accommodations else None,
        from_city=args.get('fromCity'),
        start_date=args.get('start'),
        end_date=args.get('end'),
        back_time=args.get('backTime'),
        adults=int(args.get('adults')),
        round_trip=args.get('roundtrip') == 'on',
        transport_only=args.get('transport_only') == 'on',
        hotels_only=args.get('hotels_only') == 'on',
        cars_between_places=args.get('cars_between_places') == 'on',
        trains_between_places=args.get('trains_between_places') == 'on',
        transport_start=transport_start,
        transport_end=transport_end,
        places=accommodations
    )

def load_config(from_country: str) -> dict:
    """Loads and merges the configuration files."""
    base_path = Path(os.getcwd())
    config_path = base_path / "static" / "configs"

    with (config_path / "config.json").open('r') as f:
        config_main = json.load(f)

    local_config_path = config_path / f"config-{from_country.lower()}.json"
    config_local = {}
    if local_config_path.is_file():
        with local_config_path.open('r') as f:
            config_local = json.load(f)

    return {
        "cars": config_main.get("cars", []) + config_local.get("cars", []),
        "flights": config_main.get("flights", []) + config_local.get("flights", []),
        "trains": config_main.get("trains", []) + config_local.get("trains", []),
        "hotels": config_main.get("hotels", []) + config_local.get("hotels", [])
    }

def validate_places(places, total_trip_days):
    """Validates the places and nights."""
    total_nights = 0
    for i, place in enumerate(places):
        nights = place.nights
        total_nights += nights

        if nights < 0:
            raise ValueError(f"Nights cannot be negative for {place.place}")

        if nights == 0 and i != 0 and i != len(places) - 1:
            raise ValueError(f"Only the first and last place can have 0 nights, not {place.place}")

    if total_nights > total_trip_days:
        raise ValueError("Total nights exceed trip duration")

def _execute_search(parser: Parser) -> str:
    """Wrapper to execute the search method of a Parser instance and return the URL."""
    try:
        return parser.search()
    except Exception as e:
        logging.error(f"A search task for {parser.query.params.get('company', 'Unknown')} generated an exception: {e}")
        return None

def run_searches_in_parallel(parsers_to_run: list) -> list:
    """
    Runs a list of parser searches in parallel and returns the URLs in the order they were submitted.
    """
    urls = []
    if not parsers_to_run:
        logging.info("No searches to perform.")
        return urls

    logging.info(f"--- Starting {len(parsers_to_run)} searches in parallel ---")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit all tasks and get a list of future objects, which maintains order
        futures = [executor.submit(_execute_search, parser) for parser in parsers_to_run]

        # Iterate through the futures in their original order and retrieve the results
        for future in futures:
            result_url = future.result()  # This will block until the specific future is complete
            if result_url:
                urls.append(result_url)

    logging.info("--- All parallel searches completed ---")
    return urls

def _get_transport_parsers_for_type(query_template: SearchQuery, config: dict, transport_type: str) -> list[Parser]:
    """Helper function to get a list of Parser objects for a single transport search."""
    parsers = []
    settings = config.get(transport_type, [])
    message = (
        f"Preparing {transport_type} search from {query_template.from_city} "
        f"in {countries.get(query_template.from_country)} to {query_template.to_city} in {countries.get(query_template.to_country)}. "
        f"Between {query_template.start_date} and {query_template.end_date}"
    )
    logging.info(message)

    logging.info(f"Found {len(settings)} providers for {transport_type}")
    for params in settings:
        query = replace(query_template, params=params)
        parsers.append(Parser(query))
    return parsers

def get_main_transport_parsers(trip: TripRequest, config: dict) -> list[Parser]:
    """Gathers main transport Parser objects."""
    logging.info("--- Preparing main transport search ---")

    if not trip.places:
        logging.warning("No places to visit provided. Cannot search for main transport.")
        return []

    all_parsers = []

    # Main transport is a car for a round trip.
    if trip.transport_start.transport_type == 'cars' and trip.round_trip:
        logging.info("Main transport is a roundtrip car rental.")
        car_query = SearchQuery(
            from_city=trip.from_city, from_country=trip.from_country, to_city=trip.from_city, to_country=trip.from_country,
            start_date=datetime.datetime.strptime(trip.start_date, "%Y-%m-%dT%H:%M"),
            end_date=datetime.datetime.strptime(trip.end_date, "%Y-%m-%dT%H:%M"),
            adults=trip.adults, round_trip=True, params={},
            pickup_place=trip.transport_start.pickup_place, return_place=trip.transport_start.pickup_place
        )
        all_parsers.extend(_get_transport_parsers_for_type(car_query, config, "cars"))
        return all_parsers

    # Main transport is a one-way car, or another transport type.
    if trip.transport_start.transport_type == 'cars':
        logging.info("Main transport is a one-way car rental.")
        outbound_query = SearchQuery(
            from_city=trip.from_city, from_country=trip.from_country, to_city=trip.places[-1].place, to_country=trip.places[-1].country,
            start_date=datetime.datetime.strptime(trip.start_date, "%Y-%m-%dT%H:%M"),
            end_date=datetime.datetime.strptime(trip.end_date, "%Y-%m-%dT%H:%M"),
            adults=trip.adults, round_trip=False, params={},
            pickup_place=trip.transport_start.pickup_place, return_place=trip.transport_end.return_place
        )
        all_parsers.extend(_get_transport_parsers_for_type(outbound_query, config, trip.transport_start.transport_type))
    else:
        logging.info(f"Main transport is {trip.transport_start.transport_type}.")
        outbound_query = SearchQuery(
            from_city=trip.from_city, from_country=trip.from_country, to_city=trip.places[0].place, to_country=trip.places[0].country,
            start_date=datetime.datetime.strptime(trip.start_date, "%Y-%m-%dT%H:%M"),
            end_date=datetime.datetime.strptime(trip.end_date, "%Y-%m-%dT%H:%M"),
            adults=trip.adults, round_trip=trip.round_trip, params={},
            pickup_place=trip.transport_start.pickup_place, return_place=trip.transport_end.return_place
        )
        all_parsers.extend(_get_transport_parsers_for_type(outbound_query, config, trip.transport_start.transport_type))

    # Return Trip Handling
    if not trip.round_trip:
        logging.info("Preparing return trip search")
        new_end_date = f"{trip.end_date[:10]}T{trip.back_time}"
        return_query = SearchQuery(
            from_city=trip.places[-1].place, from_country=trip.places[-1].country, to_city=trip.from_city, to_country=trip.from_country,
            start_date=datetime.datetime.strptime(trip.end_date, "%Y-%m-%dT%H:%M"),
            end_date=datetime.datetime.strptime(new_end_date, "%Y-%m-%dT%H:%M"),
            adults=trip.adults, round_trip=False, params={},
            pickup_place=trip.transport_end.return_place, return_place=trip.transport_start.pickup_place
        )
        all_parsers.extend(_get_transport_parsers_for_type(return_query, config, trip.transport_end.transport_type))

    return all_parsers

def get_local_transport_parsers(trip: TripRequest, config: dict) -> list[Parser]:
    """Gathers parsers for transport between places."""
    logging.info("--- Preparing local transport searches ---")
    all_parsers = []
    # Search for cars between places
    if trip.cars_between_places and trip.transport_start.transport_type != 'cars':
        logging.info("--- Preparing car searches between places ---")
        car_query = SearchQuery(
            from_city=trip.places[0].place, from_country=trip.places[0].country, to_city=trip.places[-1].place, to_country=trip.places[-1].country,
            start_date=datetime.datetime.strptime(trip.start_date, "%Y-%m-%dT%H:%M"),
            end_date=datetime.datetime.strptime(trip.end_date, "%Y-%m-%dT%H:%M"),
            adults=trip.adults, round_trip=False, params={}, pickup_place=None, return_place=None
        )
        all_parsers.extend(_get_transport_parsers_for_type(car_query, config, "cars"))

    # Search for trains between places
    if trip.trains_between_places:
        logging.info("--- Preparing train searches between places ---")
        current_date = datetime.datetime.strptime(trip.start_date, "%Y-%m-%dT%H:%M")
        for i in range(len(trip.places) - 1):
            if trip.places[i].nights > 0:
                current_date += datetime.timedelta(days=trip.places[i].nights)

            train_query = SearchQuery(
                from_city=trip.places[i].place, from_country=trip.places[i].country, to_city=trip.places[i+1].place, to_country=trip.places[i+1].country,
                start_date=current_date, end_date=current_date, adults=trip.adults, round_trip=False,
                params={}, pickup_place=None, return_place=None
            )
            all_parsers.extend(_get_transport_parsers_for_type(train_query, config, "trains"))
    return all_parsers

def get_hotel_parsers(trip: TripRequest, config: dict) -> list[Parser]:
    """Gathers all hotel-related Parser objects to be run."""
    logging.info("--- Preparing hotel searches ---")
    parsers = []
    settings = config.get("hotels", [])
    hotel_checkin = datetime.datetime.strptime(trip.start_date, "%Y-%m-%dT%H:%M")

    for place_details in trip.places:
        if place_details.nights > 0:
            hotel_checkout = hotel_checkin + datetime.timedelta(days=place_details.nights)
            logging.info(f"Preparing hotel search for {place_details.place} from {hotel_checkin} to {hotel_checkout}")

            for params in settings:
                query = SearchQuery(
                    from_city="", from_country=trip.from_country, to_city=place_details.place,
                    to_country=countries.get(place_details.country), start_date=hotel_checkin, end_date=hotel_checkout,
                    adults=trip.adults, round_trip=trip.round_trip, params=params
                )
                parsers.append(Parser(query))

            hotel_checkin = hotel_checkout
    return parsers

import threading

def send_attractions_webhook(trip_request: TripRequest):
    """Sends a webhook request to N8N to search for attractions."""
    logging.info("--- Sending attractions webhook ---")
    n8n_webhook_url = os.environ.get("N8N_WEBHOOK_URL")
    n8n_token = os.environ.get("N8N_TOKEN")

    if not n8n_webhook_url or not n8n_token:
        logging.warning("N8N_WEBHOOK_URL or N8N_TOKEN not set. Cannot send attractions webhook.")
        return

    headers = {
        'Content-Type': 'application/json',
        'Authorization': n8n_token
    }
    
    places_data = [
        {"city": place.place, "country": countries.get(place.country)} for place in trip_request.places
    ]

    try:
        requests.post(n8n_webhook_url, headers=headers, json=places_data, timeout=10)
        logging.info("Successfully sent attractions webhook.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send attractions webhook: {e}")

# --- Routes ---
@app.route("/login")
def login():
    auth_url = app_client.get_authorization_request_url(scopes=scopes, redirect_uri=redirect_uri)
    webbrowser.open(auth_url)
    return "Authentication started. Check your browser."

@app.route("/callback")
def callback():
    auth_code = request.args.get("code")
    result = app_client.acquire_token_by_authorization_code(
        code=auth_code,
        scopes=scopes,
        redirect_uri=redirect_uri
    )

    with open("/tmp/onenote.txt", "w+", encoding="utf-8") as f:
        f.write(result["access_token"])
    return "Authentication successful! You can close this window."

@app.route("/")
def start():
    """Renders the main single-page application."""
    n8n_enabled = os.environ.get("N8N_ENABLED", "false").lower() == "true"
    n8n_webhook_url = os.environ.get("N8N_WEBHOOK_URL") if n8n_enabled else None
    n8n_token = os.environ.get("N8N_TOKEN", "")
    return render_template('index.html', countries=countries, n8n_enabled=n8n_enabled, n8n_webhook_url=n8n_webhook_url, n8n_token=n8n_token)

@app.route("/api/search", methods=['POST'])
def api_search():
    """API endpoint to run searches for a specific step."""
    try:
        data = request.json
        step = data.get('step')
        trip_request = parse_request(data)
        config = load_config(trip_request.from_country)

        if data.get('search_attractions') == 'on' and (step == 'main_transport' or (step == 'hotels' and data.get('hotels_only') == 'on')):
            webhook_thread = threading.Thread(target=send_attractions_webhook, args=(trip_request,))
            webhook_thread.start()

        parsers = []
        if step == 'main_transport':
            parsers = get_main_transport_parsers(trip_request, config)
        elif step == 'hotels':
            parsers = get_hotel_parsers(trip_request, config)
        elif step == 'local_transport':
            parsers = get_local_transport_parsers(trip_request, config)
        else:
            return jsonify({"error": "Invalid step provided"}), 400

        urls = run_searches_in_parallel(parsers)
        return jsonify({"urls": urls})

    except (KeyError, ValueError) as e:
        logging.error(f"An error occurred parsing the request: {e}")
        return jsonify({"error": f"An error occurred: {e}"}), 400
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)