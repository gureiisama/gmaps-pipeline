# gmaps-pipeline

A modular Python data pipeline for extracting, validating, filtering, and enriching business data from the Google Maps Places API.

---

## Overview

This project implements a structured, multi-stage data pipeline that:

* Retrieves business listings using the Google Maps Text Search API
* Normalizes raw API responses into a consistent schema
* Validates geographic relevance using reverse geocoding (LocationIQ)
* Applies rule-based filtering (rating, review count, operational status)
* Enriches qualified results using the Place Details API
* Outputs structured data in JSON format for downstream processing

The pipeline is designed to be **deterministic, observable, and extensible**, with support for future additions such as Excel export, SQL storage, and lead scoring.

---

## Features

* Multi-location data extraction
* Response normalization (Text Search + Place Details)
* Reverse geocoding validation (LocationIQ)
* Rule-based filtering system
* Deduplication using `place_id`
* Left join → all records kept, only qualified enriched
* JSON output support
* Structured logging (replaces `print`)
* Execution timing and performance visibility
* Dry-run mode (skip enrichment stage)
* Modular architecture (API, pipeline, filters, I/O, utilities)

---

## Project Structure

```
gmaps_pipeline/
├── api/                  # Google Maps API interaction (search, details)
├── core/                 # Pipeline orchestration (runner, api normalization)
├── qualification/        # Filtering rules
├── io/                   # Writers (JSON implemented)
├── settings/             # Configuration and default filters
utility/
│ └── http/             # HTTP client with retry logic and API abstraction
│ └── search/           # Location validation and traversal logic
├── cli.py                # Command-line interface
```

---

## Installation

```bash
git clone https://github.com/gureiisama/gmaps-pipeline.git
cd gmaps-pipeline

pip install -r requirements.txt
pip install -e .
```

---

## Configuration

Set required API keys as environment variables:

### Windows (PowerShell)

```bash
$env:MAPS_API_KEY="your_google_api_key"
$env:LOCIQ_API_KEY="your_locationiq_api_key"
```

### macOS/Linux

```bash
export MAPS_API_KEY=your_google_api_key
export LOCIQ_API_KEY=your_locationiq_api_key
```

---

## Usage

### Python Example

```python
from gmaps_pipeline.core.main_pipeline import run_pipeline
from gmaps_pipeline.io.writers import write_json

LOCATIONS = {
    "San Francisco": [37.7749, -122.4194],
    "Los Angeles": [34.0522, -118.2437]
}

FILTERS = {
    "min_user_reviews": 10,
    "max_user_reviews": 400,
    "min_rating": 4.0,
    "is_operational": True
}

result = run_pipeline(
    query="electrician",
    page_size=5,
    radius=3000,
    locations=LOCATIONS,
    filters=FILTERS
)

write_json(result, "output.json")
```

---

### CLI Usage

```bash
py -m gmaps_pipeline.cli \
  --query "electrician" \
  --locations "sample_location_list.xlsx" \
  --page_size 5 \
  --radius 3000 \
  --min_user_count 10 \
  --max_user_count 400 \
  --rating 4.0 \
  --output_format json \
  --output_path output.json \
  --dry_run False
```

---

## Pipeline Flow

```
Locations 
  → Text Search 
  → Normalization 
  → Location Validation 
  → Filtering 
  → Deduplication 
  → Enrichment (conditional) 
  → Output
```

---

## Example Output

Below is a simplified sample of the pipeline output.

> **This example shows one qualified and one non-qualified business for clarity.**

```json
{
  "data": [
    {
      "name": "San Francisco",
      "coords": {
        "lat": 37.7749,
        "lng": -122.4194
      },
      "query": "electrician",
      "result": [
        {
          "id": "ChIJZ5vif4J9j4ARn1Yqv1gvHZU",
          "name": "BV Electric Inc.",
          "address": "44 Gough St #210, San Francisco, CA 94103, USA",
          "tags": "electrician,service,point_of_interest,establishment",
          "rating": 4.8,
          "rating_count": 557,
          "business_status": "OPERATIONAL",
          "website": "none",
          "phone": "none",
          "is_qualified": false
        }
      ]
    },
    {
      "name": "Los Angeles",
      "coords": {
        "lat": 34.0522,
        "lng": -118.2437
      },
      "query": "electrician",
      "result": [
        {
          "id": "ChIJ7aDzth3HwoARtSHjPVpFPf0",
          "name": "Blue Moon Electrical",
          "address": "360 S Broadway #60, Los Angeles, CA 90013, USA",
          "tags": "electrician,service,point_of_interest,establishment",
          "rating": 5,
          "rating_count": 71,
          "business_status": "OPERATIONAL",
          "website": "none",
          "phone": "+14086386856",
          "is_qualified": true
        }
      ]
    }
  ],
  "filters": {
    "min_user_reviews": 10,
    "max_user_reviews": 400,
    "min_rating": 4.0,
    "is_operational": true
  },
  "meta": {
    "dry_run": false,
    "total_time": 3.57,
    "creation_date": "2026-04-29"
  }
}
```

---

## Key Concepts

* **Normalized Results**
  All API responses are standardized into a consistent schema.

* **Qualification (`is_qualified`)**
  Indicates whether a business meets filtering criteria.

* **Selective Enrichment**
  Only qualified records trigger Place Details API calls.

* **Left-Join Behavior**
  All records are preserved; enrichment is applied only when available.

* **Metadata (`meta`)**
  Includes execution context such as runtime, dry-run mode and creation date.

---

## Filtering

Filtering is rule-based and configurable.

```python
DEFAULT_FILTERS = {
    "min_user_reviews": 20,
    "max_user_reviews": 100,
    "min_rating": 4.0,
    "is_operational": True
}
```

Filters are applied after validation and normalization.

---

## Location Validation

To improve geographic accuracy, the pipeline uses reverse geocoding via LocationIQ.

### Problem

Google Maps Text Search may return results outside the intended radius when local data is sparse.

### Solution

The pipeline uses `reverse_geocode` (`api/datacall.py`) and `match_component` (`utility/search/lookup.py`) to:

1. Reverse geocode input coordinates
2. Extract location components (city, state, country)
3. Match these components against business addresses

Only matching results proceed to filtering and enrichment.

---

## Performance & Observability

* **Logging**:
  Structured logging replaces print statements for better traceability

* **Timing**:
  Measures execution time per stage and overall pipeline runtime

* **Dry Run Mode**:
  Skips enrichment API calls while preserving full dataset

```python
run_pipeline(..., dry_run=True)
```

---

## Limitations

* Enrichment uses sequential API calls → primary bottleneck
* Subject to external API latency and rate limits
* JSON output only (Excel/SQL pending)
* Rule-based filtering (no scoring model yet)
* Dependent on Google Maps and LocationIQ availability

---

## Future Improvements

* Controlled concurrency (thread pooling for enrichment)
* Excel export support
* SQL database integration
* Lead scoring / ranking model
* Retry and backoff strategies
* Async pipeline execution

---

## License

MIT License

Copyright (c) 2026 Gray Egaran

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
