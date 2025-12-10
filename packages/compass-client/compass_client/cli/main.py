"""Main CLI entry point for compass-client."""

import sys
import argparse
from .refresh_mock_data import refresh_mock_data


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="compass-client",
        description="Compass API client CLI tools",
    )
    parser.add_argument(
        "--username",
        help="Compass API username (or set COMPASS_USERNAME env var)",
    )
    parser.add_argument(
        "--password",
        help="Compass API password (or set COMPASS_PASSWORD env var)",
    )
    parser.add_argument(
        "--base-url",
        help="Compass base URL (or set COMPASS_BASE_URL env var)",
    )
    parser.add_argument(
        "--skip-sanitize",
        action="store_true",
        help="Skip PII sanitization (NOT recommended)",
    )

    args = parser.parse_args()

    try:
        refresh_mock_data(
            username=args.username,
            password=args.password,
            base_url=args.base_url,
            skip_sanitize=args.skip_sanitize,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
