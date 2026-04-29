import os
import json
import argparse
from typing import Any
from gmaps_pipeline.core.main_pipeline import run_pipeline
from gmaps_pipeline.io.writers import write_json
from gmaps_pipeline.settings.config import DEFAULT_FILTERS, DEFAULT_LOCATIONS


def parse_json_or_file_path(value: str) -> Any:
    """
    Accept either:
    - a JSON string, or
    - a path to a JSON file

    Returns:
        - the parsed JSON object if `value` is valid JSON
        - the original path string if `value` points to an existing file

    Raises:
        argparse.ArgumentTypeError if neither case is true.
    """
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        if os.path.exists(value):
            return value

        raise argparse.ArgumentTypeError(
            "Expected a valid JSON string or a path to an existing JSON file."
        )


def build_filters(args: argparse.Namespace) -> dict[str, Any]:
    """
    Build the filters dictionary from CLI arguments.

    If the user provides all three of these values:
    - min_user_count
    - max_user_count
    - rating

    then they override the default filters.
    """
    if (
        args.min_user_count is not None
        and args.max_user_count is not None
        and args.rating is not None
    ):
        return {
            "min_user_reviews": int(args.min_user_count),
            "max_user_reviews": int(args.max_user_count),
            "min_rating": float(args.rating),
            "is_operational": True,
        }

    return DEFAULT_FILTERS


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the Google Maps pipeline and save the results to a file."
    )

    parser.add_argument(
        "--query",
        type=str,
        default="plumber",
        help="Search term to use in the pipeline. Default: plumber",
    )
    parser.add_argument(
        "--page_size",
        type=int,
        default=5,
        help="Number of results to request per page. Default: 5",
    )
    parser.add_argument(
        "--radius",
        type=int,
        default=3000,
        help="Search radius in meters. Default: 3000",
    )
    parser.add_argument(
        "--locations",
        type=parse_json_or_file_path,
        default=DEFAULT_LOCATIONS,
        help="JSON string or path to a JSON file containing locations.",
    )

    parser.add_argument(
        "--min_user_count",
        type=int,
        default=None,
        help="Minimum number of user reviews required.",
    )
    parser.add_argument(
        "--max_user_count",
        type=int,
        default=None,
        help="Maximum number of user reviews allowed.",
    )
    parser.add_argument(
        "--rating",
        type=float,
        default=None,
        help="Minimum rating threshold.",
    )
    parser.add_argument(
        "--filters",
        default=DEFAULT_FILTERS,
        help="Default filters used by the pipeline.",
    )

    parser.add_argument(
        "--output_format",
        type=str,
        choices=["json"],
        default="json",
        help="Output format. Default: json",
    )
    parser.add_argument(
        "--output_path",
        default=None,
        help="Path where the output file will be saved.",
    )

    parser.add_argument(
        "--dry_run",
        default=False,
        help="False by default. Skips enrichment when set to True.",
    )

    return parser


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    filters = build_filters(args)

    output_data = run_pipeline(
        query=args.query,
        page_size=args.page_size,
        radius=args.radius,
        locations=args.locations,
        filters=filters,
        dry_run=args.dry_run
    )

    if args.output_format == "json":
        path = write_json(
            data=output_data,
            path=args.output_path
        )
        print(f"Output saved to: {path}")


if __name__ == "__main__":
    main()
