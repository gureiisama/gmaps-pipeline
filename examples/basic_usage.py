import os
from pathlib import Path
from time import time_ns
from gmaps_pipeline.io.writers import write_json
from gmaps_pipeline.core.main_pipeline import run_pipeline


def main():
    # Accepts one or more locations
    LOCATIONS = {
        "San Francisco": [37.7749, - 122.4194],
        "Los Angeles": [34.0522, -118.2437]
    }

    FILTERS = {
        "min_user_reviews": 20,
        "max_user_reviews": 100,
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

    # Save and Log file path
    file_path = str(Path(os.getcwd()) / f"basic_usage_output_{time_ns()}.json")
    write_json(result, path=file_path)
    print(f"Output saved to: {file_path}")


if __name__ == "__main__":
    main()
