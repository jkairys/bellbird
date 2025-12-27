"""CLI command for refreshing mock data from real Compass API."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from .browser_fetcher import fetch_with_browser

# Load environment variables from .env
load_dotenv()

# Path to mock data directory
MOCK_DATA_DIR = Path(__file__).parent.parent / "data" / "mock"


def fetch_real_data(
    username: Optional[str] = None,
    password: Optional[str] = None,
    base_url: Optional[str] = None,
    days: int = 30,
    limit: int = 100,
    headless: bool = True,
) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Fetch user details and events from real Compass API using browser automation.

    Uses Playwright to handle Cloudflare protection and fetch data.

    Args:
        username: Compass API username
        password: Compass API password
        base_url: Base URL for Compass instance
        days: Number of days to fetch events for (default: 30)
        limit: Maximum number of events to fetch (default: 100)
        headless: Whether to run browser in headless mode (default: True)

    Returns:
        Tuple of (user_data_dict, events_list_of_dicts)

    Raises:
        Exception: If authentication fails or API call fails
    """
    # Ensure credentials are not None
    if username is None or password is None or base_url is None:
        raise ValueError(
            "Requires non-None username, password, and base_url."
            " Ensure these are provided as arguments or set in environment variables."
        )

    return fetch_with_browser(
        base_url=base_url,
        username=username,
        password=password,
        days=days,
        limit=limit,
        headless=headless,
    )


def sanitize_user_data(user_data: dict[str, Any]) -> dict[str, Any]:
    """Remove PII (Personally Identifiable Information) from user data.

    Args:
        user_data: Raw user data from Compass API

    Returns:
        Sanitized user data dict with PII removed
    """
    sanitized = user_data.copy()

    # Remove/redact sensitive fields
    pii_fields = [
        "email",
        "phone",
        "mobilePhone",
        "address",
        "suburb",
        "postcode",
        "state",
        "country",
    ]

    for field in pii_fields:
        if field in sanitized:
            # Keep field structure but redact value
            sanitized[field] = "[REDACTED]"

    # Keep essential fields for testing: id, firstName, lastName
    return sanitized


def sanitize_event_data(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove PII from event data.

    Args:
        events: List of raw event dicts from Compass API

    Returns:
        List of sanitized event dicts
    """
    sanitized_events = []

    for event in events:
        sanitized = event.copy()

        # Remove/redact sensitive fields
        pii_fields = [
            "createdBy",
            "modifiedBy",
            "location",
            "description",
            "notes",
        ]

        for field in pii_fields:
            if field in sanitized:
                sanitized[field] = "[REDACTED]"

        sanitized_events.append(sanitized)

    return sanitized_events


def write_mock_data(user_data: dict[str, Any], events_data: list[dict[str, Any]]) -> None:
    """Write sanitized mock data to JSON files.

    Args:
        user_data: Sanitized user data dict
        events_data: List of sanitized event dicts
    """
    # Ensure directory exists
    MOCK_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Write user data
    user_file = MOCK_DATA_DIR / "compass_user.json"
    with open(user_file, "w") as f:
        json.dump(user_data, f, indent=2)
    print(f"✓ Wrote user data to {user_file}")

    # Write events data
    events_file = MOCK_DATA_DIR / "compass_events.json"
    with open(events_file, "w") as f:
        json.dump(events_data, f, indent=2)
    print(f"✓ Wrote events data to {events_file}")


def update_schema_version() -> None:
    """Update schema_version.json with current timestamp and package version."""
    schema_file = MOCK_DATA_DIR / "schema_version.json"

    schema_data = {
        "last_updated": datetime.now().isoformat(),
        "compass_api_version": "1.0.0",  # Hardcode for now
        "mock_data_version": "1.0.0",
    }

    with open(schema_file, "w") as f:
        json.dump(schema_data, f, indent=2)
    print(f"✓ Updated schema version in {schema_file}")


def refresh_mock_data(
    username: Optional[str] = None,
    password: Optional[str] = None,
    base_url: Optional[str] = None,
    skip_sanitize: bool = False,
    headless: bool = True,
) -> None:
    """Refresh mock data by fetching fresh samples from real Compass API.

    Uses Playwright browser automation to handle Cloudflare protection.
    Requires valid Compass credentials via environment variables or parameters.
    Sanitizes data to remove PII before storing in repository.

    Args:
        username: Compass username (or set COMPASS_USERNAME env var)
        password: Compass password (or set COMPASS_PASSWORD env var)
        base_url: Compass base URL (or set COMPASS_BASE_URL env var)
        skip_sanitize: Skip PII sanitization (not recommended)
        headless: Run browser in headless mode (default True)
    """
    # Get credentials from environment if not provided
    if not username:
        username = os.getenv("COMPASS_USERNAME")
        if not username:
            username = input("Compass username: ")

    if not password:
        password = os.getenv("COMPASS_PASSWORD")
        if not password:
            import getpass

            password = getpass.getpass("Compass password: ")

    if not base_url:
        base_url = os.getenv("COMPASS_BASE_URL")
        if not base_url:
            base_url = input("Compass base URL: ")

    print("Refreshing mock data from Compass API...")
    print(f"Base URL: {base_url}")
    print(f"Username: {username}")
    print(f"Headless mode: {headless}")

    try:
        # Fetch real data using browser automation
        print("\nFetching data from Compass API (using browser)...")
        user_data, events_data = fetch_real_data(
            username, password, base_url, headless=headless
        )
        print(f"✓ Fetched user data: {len(str(user_data))} bytes")
        print(f"✓ Fetched {len(events_data)} events")

        # Sanitize if not skipped
        if not skip_sanitize:
            print("\nSanitizing data (removing PII)...")
            user_data = sanitize_user_data(user_data)
            events_data = sanitize_event_data(events_data)
            print("✓ Data sanitized")
        else:
            print("⚠️  Skipping sanitization - PII will be included in mock data")

        # Write to files
        print("\nWriting mock data files...")
        write_mock_data(user_data, events_data)

        # Update schema version
        print("\nUpdating schema version...")
        update_schema_version()
        print("\n✅ Mock data refresh completed successfully!")
        print(f"Mock data location: {MOCK_DATA_DIR}")
        print("Next steps: Commit the updated mock data files to your repository")

    except Exception as e:
        print(f"\n❌ Error refreshing mock data: {e}")
        raise
