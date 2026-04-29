import time
import logging
from pathlib import Path
from gmaps_pipeline.utility.search.lookup import deep_query
from gmaps_pipeline.qualification.segment import segment_places
from gmaps_pipeline.api.datacall import reverse_geocode, search_places, fetch_place_details
from gmaps_pipeline.utility.search.lookup import deep_query
from gmaps_pipeline.utility.http.client import rate_limited_call
from gmaps_pipeline.settings.config import DEFAULT_FILTERS, DEFAULT_LOCATIONS
from gmaps_pipeline.core.normalize import (
    remodel_lociq,
    remodel_raw_details,
    build_base_schema,
    apply_enrichment,
    parse_excel
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def run_pipeline(
    query: str = "plumber",
    page_size: int = 5,
    radius: int = 3000,
    locations: dict | Path | str = DEFAULT_LOCATIONS,
    filters: dict = DEFAULT_FILTERS,
    dry_run: bool = False,
) -> dict:
    """
    Execute the end-to-end Google Maps data pipeline.

    This pipeline performs:
    1. Input sanitization and location preparation
    2. Place search per location
    3. Filtering of results based on defined criteria
    4. (Optional) Enrichment via Place Details API
    5. Final schema normalization

    Parameters
    ----------
    query : str
        Search query (e.g., "plumber", "restaurant").
    page_size : int
        Number of results per API page.
    radius : int
        Search radius in meters.
    locations : dict | Path | str
        Location configuration source.
    filters : dict
        Criteria used to qualify places.
    dry_run : bool
        If True, skips enrichment stage.

    Returns
    -------
    dict
        Structured output containing processed data per location,
        applied filters, parameters, and metadata.
    """

    pipeline_start = time.time()

    # --- 1. Validate / Sanitize inputs ---
    config_location = _sanitize(locations)

    if not config_location:
        raise ValueError("No valid file or locations object to sanitize.")

    search_data = []
    qualified_ids = []

    # --- 2. Search per location ---
    for area_name, coords in config_location.items():
        stage_start = time.time()

        lat, lng = coords
        logger.info(f"Processing area: {area_name}")

        reverse_location = remodel_lociq(reverse_geocode(coords))

        raw_data = {
            "name": area_name,
            "coords": {"lat": lat, "lng": lng},
            "query": query,
            "reverse_location": reverse_location
        }

        search_details = rate_limited_call(
            search_places,
            coords=coords,
            query=query,
            page_size=page_size,
            radius=radius
        )

        remodeled_list = remodel_raw_details(search_details["places"])

        # --- 3. Apply Filters ---
        filtered_ids = segment_places(
            places=remodeled_list,
            filters=filters,
            reverse_geo_address=reverse_location.get("display_name", ""),
            return_key="id"
        )

        if filtered_ids:
            qualified_ids.extend(filtered_ids)

        # --- Build base schema immediately ---
        base_schema = build_base_schema(remodeled_list)
        raw_data["result"] = base_schema

        search_data.append(raw_data)

        logger.info(
            f"Search + transform took {time.time() - stage_start:.2f}s")

    # Deduplicate IDs
    qualified_ids = list(set(qualified_ids))

    # --- 4. Fetch place details ---
    enrichment_start = time.time()
    enriched_data = []

    if not dry_run and qualified_ids:
        logger.info(f"Fetching details for {len(qualified_ids)} places")

        for place_id in qualified_ids:
            try:
                enriched_data.append(fetch_place_details(place_id))
            except Exception:
                logger.warning(f"Failed to fetch details for {place_id}")

        enriched_data = remodel_raw_details(enriched_data)

    else:
        logger.info("Dry run enabled — skipping enrichment stage")

    logger.info(f"Enrichment stage took {time.time() - enrichment_start:.2f}s")

    # --- 5. Apply enrichment (only if not dry run) ---
    if not dry_run:
        for data in search_data:
            data["result"] = apply_enrichment(
                base_records=data["result"],
                enriched_details=enriched_data
            )

    # --- Final output ---
    final_output = {
        "data": search_data,
        "filters": filters,
        "radius": radius,
        "page_size": page_size,
        "meta": {
            "dry_run": dry_run,
            "total_time": round(time.time() - pipeline_start, 2),
            "creation_date": time.strftime("%Y-%m-%d")
        }
    }

    logger.info(f"Pipeline completed in {time.time() - pipeline_start:.2f}s")

    return final_output


def _sanitize(locations: dict | Path | str) -> dict | None:
    """
    An error handler that is used to validate the provided locations object/file path

    Params:
        locations (dict | Path | str): A dictionary, file or a string containing the locations object.

    Output: 
        Returns a sanitized locations object (dict) or raises an exception
    """

    if isinstance(locations, Path) or isinstance(locations, str):
        file = Path(locations)
        if not file.is_file():
            raise FileNotFoundError(f"File does not exist: {file}")
        elif not ".xlsx" in file.suffix:
            raise TypeError(
                f'Current supported helper_file is only in ".xlsm" format. Received: "{file.suffix}"')
        return parse_excel(file)

    elif isinstance(locations, dict):
        has_empty_coords = set([
            not coords for coords in deep_query(locations, "*", "*")
        ])

        invalid_dtype = [str(type(coords)) for coords in deep_query(
            locations, "*", "*") if not isinstance(coords, float)]

        if not isinstance(locations, dict):
            raise ValueError(f"The location object is not of type {dict}")

        if invalid_dtype:
            raise ValueError(
                f"Invalid coordinates found: ({",".join(invalid_dtype)})")

        if True in has_empty_coords or not has_empty_coords:
            raise ValueError(
                'The locations object contain an empty coordinates.')

        return locations
    else:
        raise ValueError("locations object/filepath is invalid.")
