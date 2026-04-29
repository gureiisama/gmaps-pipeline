import os
from pathlib import Path


def getAPI(API_NAME): return os.getenv(API_NAME)
def default_locations_path(): return Path(os.getcwd()) / "location_list.xlsx"


MAPS_API_KEY = getAPI('MAPS_API_KEY')
LOCIQ_API_KEY = getAPI('LOCIQ_API_KEY')
SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
DETAILS_URL = "https://places.googleapis.com/v1/places/{}"
LOCIQ_URL = "https://us1.locationiq.com/v1/reverse"


SEARCH_HEADERS = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": MAPS_API_KEY,
    "X-Goog-FieldMask": (
        "places.id,"
        "places.displayName,"
        "places.rating,"
        "places.userRatingCount,"
        "places.businessStatus,"
        "places.formattedAddress,"
        "places.googleMapsUri,"
        "places.types"
    )
}

DETAILS_HEADERS = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": MAPS_API_KEY,
    "X-Goog-FieldMask": (
        "id,"
        "websiteUri,"
        "nationalPhoneNumber,"
        "rating,"
        "userRatingCount"
    )
}

DEFAULT_FILTERS = {
    "min_user_reviews": 20,
    "max_user_reviews": 200,
    "min_rating": 4.0,
    "is_operational": True
}

DEFAULT_LOCATIONS = {
    "San Francisco": [37.7749, - 122.4194],
    "Los Angeles": [34.0522, -118.2437]
}


def generate_lociq_headers(latitude, longitude):
    return {
        'key': LOCIQ_API_KEY,
        'lat': latitude,
        'lon': longitude,
        'format': 'json',
        'addressdetails': 1,  # Includes city, zip, etc. as separate fields
        'normalizecity': 1   # Simplifies city names
    }


ALLOWED_OUTPUT = ["excel", "json", "sql"]
