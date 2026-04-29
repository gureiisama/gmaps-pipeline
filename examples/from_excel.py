import os
from pathlib import Path
from time import time_ns
from gmaps_pipeline.io.writers import write_json
from gmaps_pipeline.core.main_pipeline import run_pipeline


def main():
    # Pass an excel file containing locations instead of a locations object
    LOCATIONS_FILE = "sample_location_list.xlsx"

    FILTERS = {
        "min_user_reviews": 60,
        "max_user_reviews": 240,
        "min_rating": 4.0,
        "is_operational": True
    }

    result = run_pipeline(
        query="dental clinic",
        page_size=5,
        radius=3000,
        locations=LOCATIONS_FILE,
        filters=FILTERS
    )

    # Save and Log file path
    file_path = str(Path(os.getcwd()) / f"from_excel_output_{time_ns()}.json")
    write_json(result, path=file_path)
    print(f"Output saved to: {file_path}")


if __name__ == "__main__":
    main()
