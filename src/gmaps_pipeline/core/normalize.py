import re
import pandas
from pathlib import Path
from gmaps_pipeline.utility.search.lookup import deep_query


def remodel_lociq(lociq_obj: dict) -> dict:
    output = {}
    output.setdefault("coords", {
        "lat": lociq_obj.get("lat", 0),
        "lng": lociq_obj.get("lon", 0)
    })
    output.setdefault("display_name", lociq_obj.get("display_name", ""))
    return output


def remodel_raw_details(place_list: list) -> list:
    processed = []
    for place in place_list:
        processed.append(case_correction(place))
    return processed


def parse_excel(filepath: str | Path) -> dict:

    file = Path(filepath)
    if not file.is_file():
        raise FileNotFoundError(f"file does not exist: {file}")

    df = pandas.read_excel(file)

    # Column names
    area_name = 'City / District / Province'
    lat = 'Latitude'
    lng = 'Longitude'

    data_set = df[[area_name, lat, lng]]
    total_discrepancy = sum(list(data_set.isnull().sum()))

    if total_discrepancy:
        raise ValueError(
            f"The data frame must contain no discrepancy. Total found: {total_discrepancy}")

    records = data_set.to_dict(orient="records")

    locations = {}
    for record in records:
        locations.setdefault(
            record.get(area_name),
            [record.get('Latitude'), record.get(lng)]
        )

    return locations


def build_base_schema(search_details: list[dict]) -> list[dict]:
    """
    Normalize raw search results into a consistent base schema.

    This function extracts and formats fields from the search API output
    without applying any enrichment logic.

    Parameters
    ----------
    search_details : list[dict]
        Raw place data from the search API.

    Returns
    -------
    list[dict]
        List of normalized place records.
    """

    output = []

    for detail in search_details:
        place_id = detail.get("id")

        record = {
            "id": place_id,
            "name": (detail.get("display_name") or {}).get("text", ""),
            "address": detail.get("formatted_address", ""),
            "tags": ",".join(detail.get("types", [])),
            "rating": detail.get("rating", 0.0),
            "rating_count": detail.get("user_rating_count", 0),
            "business_status": detail.get("business_status", "NON-OPERATIONAL"),
            "phone": "none",
            "website": "none",
            "google_maps": detail.get("google_maps_uri", "none"),
            "is_qualified": detail.get("is_qualified", False)
        }

        output.append(record)

    return output


def apply_enrichment(
    base_records: list[dict],
    enriched_details: list[dict]
) -> list[dict]:
    """
    Merge enriched place details into base schema records.

    Parameters
    ----------
    base_records : list[dict]
        Normalized records from `build_base_schema`.
    enriched_details : list[dict]
        Enriched place data.

    Returns
    -------
    list[dict]
        Updated records containing enrichment data.
        Only records with matching enrichment are returned.
    """

    enriched_details = enriched_details or []

    enriched_index = {
        item.get("id"): item
        for item in enriched_details
        if isinstance(item, dict) and item.get("id")
    }

    output = []

    for record in base_records:
        place_id = record.get("id")
        enriched = enriched_index.get(place_id)

        if enriched:
            record["rating"] = enriched.get("rating", record["rating"])
            record["rating_count"] = enriched.get(
                "rating_count", record["rating_count"]
            )
            record["phone"] = enriched.get(
                "phone", "none"
            )
            record["website"] = enriched.get("website", "none")

        output.append(record)

    return output


def to_snake_case(s):
    """
    Convert a CamelCase or camelCase string to snake_case.

    Parameters
    ----------
    s : str
        The input string to convert.

    Returns
    -------
    str
        The string converted to snake_case.

    Examples
    --------
    >>> to_snake_case("displayName")
    'display_name'
    >>> to_snake_case("BusinessName")
    'business_name'
    """
    s = re.sub(r'(?<!^)(?=[A-Z])', '_', s)
    return s.lower()


def case_correction(d):
    """
    Return a new dictionary with all keys converted to snake_case.

    Parameters
    ----------
    d : dict
        A dictionary whose keys should be converted.

    Returns
    -------
    dict
        A new dictionary with snake_case keys and the same values.

    Examples
    --------
    >>> case_correction({"displayName": "Business name"})
    {'display_name': 'Business name'}
    """
    return {to_snake_case(k): v for k, v in d.items()}
