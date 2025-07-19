import os
import json
import datetime
import time
import sys
import webbrowser
import requests
import msal
from pathlib import Path
from flask import Flask, render_template, request
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

    places_list = args.getlist('places[]')
    nights_list = args.getlist('nights[]')
    trip_countries_list = args.getlist("countries[]")

    accommodations = [
        AccommodationDetails(
            place=place,
            nights=int(nights_list[i]),
            country=trip_countries_list[i]
        ) for i, place in enumerate(places_list)
    ]

    return TripRequest(
        from_country=args.get('fromCountry'),
        to_country=args.get('toCountry'),
        from_city=args.get('fromCity'),
        start_date=args.get('start'),
        end_date=args.get('end'),
        back_time=args.get('backTime'),
        adults=int(args.get('adults')),
        round_trip=args.get('roundtrip') == 'on',
        hotels_only=args.get('hotelsOnly') == 'on',
        transport_only=args.get('transportOnly') == 'on',
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

def handle_search(trip: TripRequest):
    """Handles the search logic for the given trip."""
    config = load_config(trip.from_country)

    # Handle start trip transport
    if not trip.hotels_only:
        handle_transport_search(trip, config)

    # Handle hotel search
    if not trip.transport_only:
        handle_hotel_search(trip, config)

def _search_transport(query_template: SearchQuery, config: dict, transport_type: str):
    """Helper function to perform a single transport search."""
    settings = config.get(transport_type, [])
    message = (
        f"Searching {transport_type} from {query_template.from_city} "
        f"in {countries.get(query_template.from_country)} to {query_template.to_city} in {countries.get(query_template.to_country)}. "
        f"Between {query_template.start_date} and {query_template.end_date}"
    )
    logging.info(message)

    logging.info(f"Found {len(settings)} providers for {transport_type}")
    for params in settings:
        query = replace(query_template, params=params)
        transport = Parser(query)
        transport.search()

def handle_transport_search(trip: TripRequest, config: dict):
    """Handles the transport search logic."""
    logging.info("--- Starting transport search ---")
    # Search for the outbound trip
    outbound_query = SearchQuery(
        from_city=trip.from_city,
        from_country=trip.from_country,
        to_city=trip.places[0].place,
        to_country=trip.to_country,
        start_date=datetime.datetime.strptime(trip.start_date, "%Y-%m-%dT%H:%M"),
        end_date=datetime.datetime.strptime(trip.end_date, "%Y-%m-%dT%H:%M"),
        adults=trip.adults,
        round_trip=trip.round_trip,
        params={},
        pickup_place=trip.transport_start.pickup_place,
        return_place=trip.transport_end.return_place
    )
    _search_transport(
        outbound_query,
        config,
        trip.transport_start.transport_type
    )

    # Search for the return trip if it's not a round trip
    if not trip.round_trip:
        logging.info("Handling return trip")
        new_end_date = f"{trip.end_date[:10]}T{trip.back_time}"
        return_query = SearchQuery(
            from_city=trip.places[-1].place,
            from_country=trip.to_country,
            to_city=trip.from_city,
            to_country=trip.from_country,
            start_date=datetime.datetime.strptime(trip.end_date, "%Y-%m-%dT%H:%M"),
            end_date=datetime.datetime.strptime(new_end_date, "%Y-%m-%dT%H:%M"),
            adults=trip.adults,
            round_trip=False,
            params={},
            pickup_place=trip.transport_end.return_place,
            return_place=trip.transport_start.pickup_place
        )
        _search_transport(
            return_query,
            config,
            trip.transport_end.transport_type
        )
    logging.info("--- Finished transport search ---")

def handle_hotel_search(trip: TripRequest, config: dict):
    """Handles the hotel search logic."""
    logging.info("Searching for hotels!")
    settings = config.get("hotels", [])
    hotel_checkin = datetime.datetime.strptime(trip.start_date, "%Y-%m-%dT%H:%M")

    for place_details in trip.places:
        hotel_checkout = hotel_checkin + datetime.timedelta(days=place_details.nights)

        for params in settings:
            query = SearchQuery(
                from_city="",
                from_country=trip.from_country,
                to_city=place_details.place,
                to_country=countries.get(place_details.country),
                start_date=hotel_checkin,
                end_date=hotel_checkout,
                adults=trip.adults,
                round_trip=trip.round_trip,
                params=params
            )
            hotels = Parser(query)
            hotels.search()

        hotel_checkin = hotel_checkout
        time.sleep(3)

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
    return render_template('index.html', countries=countries)

@app.route("/planner", methods=['GET'])
def planner():
    try:
        trip_request = parse_request(request.args)
        handle_search(trip_request)
        return render_template('planner.html', countries=countries, request=request)
    except (KeyError, ValueError) as e:
        logging.error(f"An error occurred parsing the request: {e}")
        return f"An error occurred: {e}", 400
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return "An unexpected error occurred. Please try again later.", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)