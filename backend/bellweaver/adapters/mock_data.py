"""
Mock data collection for development and testing.

This module provides functionality to collect real data from Compass
and save it as mock data for use in development and testing.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Tuple

from dotenv import load_dotenv

from compass import CompassClient


def collect_compass_data(
    days: int = 30,
    limit: int = 100,
    output_dir: Path | None = None,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Collect all data from Compass and save as mock data.

    This collects:
    - User details (for the authenticated user)
    - Calendar events for the specified date range

    Args:
        days: Number of days ahead to fetch events for (default: 30)
        limit: Maximum number of events to fetch (default: 100)
        output_dir: Directory to save mock data to (default: backend/data/mock)

    Returns:
        Tuple of (user_details, events)

    Raises:
        ValueError: If required environment variables are not set
        Exception: If authentication or data collection fails
    """
    # Load environment variables
    load_dotenv()

    base_url = os.getenv("COMPASS_BASE_URL")
    username = os.getenv("COMPASS_USERNAME")
    password = os.getenv("COMPASS_PASSWORD")

    if not all([base_url, username, password]):
        raise ValueError(
            "COMPASS_BASE_URL, COMPASS_USERNAME, and COMPASS_PASSWORD "
            "must be set in .env file"
        )

    # Ensure base_url has https://
    if not base_url.startswith("http"):
        base_url = f"https://{base_url}"

    # Set output directory
    if output_dir is None:
        # Default to backend/data/mock
        output_dir = Path(__file__).parent.parent.parent / "data" / "mock"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Connect to Compass
    client = CompassClient(base_url, username, password)

    try:
        # Authenticate
        client.login()

        # Fetch user details
        user_details = client.get_user_details()

        # Save user details
        user_file = output_dir / "compass_user.json"
        with open(user_file, "w") as f:
            json.dump(user_details, f, indent=2, default=str)

        # Fetch events
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

        events = client.get_calendar_events(start_date, end_date, limit=limit)

        # Save events
        events_file = output_dir / "compass_events.json"
        with open(events_file, "w") as f:
            json.dump(events, f, indent=2, default=str)

        return user_details, events

    finally:
        client.close()
