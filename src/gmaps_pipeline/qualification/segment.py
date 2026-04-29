from gmaps_pipeline.utility.search.lookup import deep_query, match_component


def segment_places(
        places: list,
        filters: dict,
        reverse_geo_address: str,
        return_key: str = "*"
) -> list | None:
    """
    Filter and return place records that match the given criteria.
    The function walks through the provided place data, extracts each raw place record, checks its rating, review count, operational status, and whether its address matches the reverse-geocoded location. Only records that satisfy all filter conditions are returned.

    Args:
        places (dict): Nested place data containing raw place records and
            reverse location metadata.
        filters (dict): Filtering rules. Expected keys include:
            - min_rating
            - min_user_reviews
            - max_user_reviews
            - is_operational

    Returns:
        list: A list of place dictionaries that meet all filter conditions.

    Raises:
        ValueError: If `filters` is not a dictionary or is empty.
        KeyError: If the function cannot extract the reverse location from
            `places`.
    """

    if not isinstance(filters, dict) or not filters:
        raise ValueError("Unable to segment data, no filters have been found.")

    if not isinstance(reverse_geo_address, str) or not reverse_geo_address:
        raise ValueError(
            "No reverse_geo_address found, unable to validate query address."
        )

    _min = filters.get('min_user_reviews')
    _max = filters.get('max_user_reviews')

    if not _min or not _max:
        raise ValueError(
            f"Unable to filter min_user_reviews:{_min} and max_user_reviews:{_max}")

    qualified_results = []

    for place in places:

        places_loc = place.get("formatted_address")
        rating_count = place.get("rating", 0)
        user_rating_count = place.get("user_rating_count", 0)
        isOperational = True if place.get(
            "business_status", "").lower() else False
        address_check = match_component(
            source_text=places_loc,
            target_text=reverse_geo_address,
            delimiter=","
        )

        if (
            rating_count >= filters.get('min_rating') and
            (user_rating_count >= _min and user_rating_count <= _max) and
            isOperational == filters.get('is_operational') and
            address_check
        ):
            place.setdefault("is_qualified", True)
            qualified_results.append(place)

    if return_key == "*":
        return qualified_results

    if qualified_results:
        if not qualified_results[0].get(return_key, None):
            raise KeyError(f'Return Key: "{return_key}" does not exist.')
        else:
            return deep_query(qualified_results, "*", return_key)
