"""CLI command for refreshing mock data from real Compass API."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from compass_client.client import CompassClient

# Load environment variables from .env
load_dotenv()

# Path to mock data directory
MOCK_DATA_DIR = Path(__file__).parent.parent / "data" / "mock"


def fetch_real_data(
    username: str, password: str, base_url: str, days: int = 30, limit: int = 100
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Fetch user details and events from real Compass API.

    Args:
        username: Compass API username
        password: Compass API password
        base_url: Base URL for Compass instance
        days: Number of days to fetch events for (default: 30)
        limit: Maximum number of events to fetch (default: 100)

    Returns:
        Tuple of (user_data_dict, events_list_of_dicts)

    Raises:
        Exception: If authentication fails or API call fails
    """
    client = CompassClient(username=username, password=password, base_url=base_url)

    # Authenticate
    client.login()

    # Fetch user details
    user_response = client.get_user_details()
    user_data = user_response

    # Fetch events
    from datetime import timedelta

    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

    events_response = client.get_calendar_events(
        start_date=start_date, end_date=end_date, limit=limit
    )
    events_data = events_response

    return user_data, events_data


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
    username: str = None, password: str = None, base_url: str = None, skip_sanitize: bool = False
) -> None:
    """Refresh mock data by fetching fresh samples from real Compass API.

    Requires valid Compass credentials via environment variables or parameters.
    Sanitizes data to remove PII before storing in repository.
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

    try:
        # Fetch real data
        print("\nFetching data from Compass API...")
        user_data, events_data = fetch_real_data(username, password, base_url)
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
