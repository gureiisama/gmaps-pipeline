import re
from gmaps_pipeline.utility.http.client import http_request
from gmaps_pipeline.settings.config import (
    SEARCH_URL,
    SEARCH_HEADERS,
    DETAILS_URL,
    DETAILS_HEADERS,
    LOCIQ_URL,
    generate_lociq_headers
)


def search_places(
        coords: list,
        query: str = 'plumber',
        page_size: int = 5,
        radius: int = 3000,
):
    """
    Perform a Google Places Text Search using location bias.

    Constructs and sends a search request based on coordinates, query,
    and radius, returning raw API results with optional request metadata.

    Args:
        coords: [latitude, longitude] pair.
        query: Search keyword or phrase.
        page_size: Maximum number of results to return.
        radius: Search radius in meters.
        storeParams: If True, include request parameters and reverse-geocoded location.

    Returns:
        dict: {
            "raw": API response,
            "params": (optional) input parameters and derived metadata
        }
    """

    _validate(coords, query, page_size, radius)

    [lat, lng] = coords

    search_payload = {
        "textQuery": query,
        "page_size": page_size,
        "locationBias": {
            "circle": {
                "center": {
                    "latitude": lat,
                    "longitude": lng
                },
                "radius": radius
            }
        }
    }

    search_response = http_request(
        method="POST",
        url=SEARCH_URL,
        headers=SEARCH_HEADERS,
        json=search_payload
    )

    return search_response


def fetch_place_details(
    place_id: str
) -> object:
    """
    Retrieve detailed information for a specific place.

    Uses the Google Places Details endpoint to fetch enriched data
    such as name, website, phone number, and other available fields.

    Args:
        place_id: Unique Google Places identifier.

    Returns:
        dict: Parsed API response containing place details.
    """

    return http_request(
        method="GET",
        url=DETAILS_URL.format(place_id),
        headers=DETAILS_HEADERS
    )


def reverse_geocode(coords: list) -> dict:
    """
    Convert geographic coordinates into a human-readable location.

    Uses the LocationIQ API to resolve latitude and longitude into
    structured address information.

    Args:
        coords: [latitude, longitude] pair.

    Returns:
        dict: Parsed API response containing address/location data.
    """

    [lat, lon] = coords

    return http_request(
        method="GET",
        url=LOCIQ_URL,
        params=generate_lociq_headers(lat, lon)
    )


def _validate(
    coords: list,
    query: str = 'plumber',
    page_size: int = 20,
    radius: int = 3000,
):
    """
    Error handler used for cleansing input arguments for search_places Function

    Params:
        coords (list): Must only contain latitude and longtitude, ex. [14.599, 120.984]                
        query (str): The text query used for Text Search API. ex. "restaurant", "plumber"        
        page_size (int): Controls how many place results are returned per page in the response.
        radius (int): Defines how far from a given location the API should prioritize results.

    Output: 
        Raises and exception or does nothing (pass)
    """

    # COORDS
    if not isinstance(coords, list):
        raise ValueError("Coordinates must be a typed of list.")

    # QUERY
    # Pattern: Start of string, one or more alpha/space chars, end of string
    pattern = r"^[a-zA-Z\s]+$"
    if not re.fullmatch(pattern, query):
        raise ValueError(
            "Query can only contain alphabet characters and spaces")

    # page_size
    if page_size < 1:
        raise ValueError("Minimum page_size must be atleast 1")

    if page_size > 20:
        _cancel(warningMsg="""
Increasing page_size beyond 20 pulls in lower quality result
while making responses heavier and slower. It also drives
up downstream costs and complicates pagination.
            """)

    # RADIUS
    if radius < 1:
        raise ValueError("Radius must be atleast 500")

    if radius > 3000:
        _cancel(
            warningMsg="Using a radius > 3000m weakens locality and reduces the result's relevance.")


def _cancel(
    warningMsg: str,
    confirmMsg: str = "Would you still like to proceed? [Y/N]: ",
    cancelMsg: str = "The operation has been successfully cancelled"
):
    """
    A helper function serving as a secondary check if the user wants
    to proceed despite the initial warning, it either proceeds or
    cancels an operation by raising an Exception.

    Params:
        warningMsg (str): Warning message
        confirmMsg (str): Confirmatory message
        cancelMsg (str): Cancellation message

    Output:
        Returns None or raises and Exception
    """
    print(warningMsg + '\n')
    ans = input(confirmMsg)
    if ans == "Y":
        return None
    else:
        raise Exception(cancelMsg)
