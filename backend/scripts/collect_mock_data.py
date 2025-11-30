#!/usr/bin/env python3
"""
Collect real Compass data for use as mock data in development.

This script:
1. Authenticates with Compass using credentials from .env
2. Fetches user details for the authenticated user
3. Fetches calendar events for the next 30 days
4. Saves the raw responses to data/mock/compass_*.json
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.adapters.compass import CompassClient


def main():
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    base_url = os.getenv('COMPASS_BASE_URL')
    username = os.getenv('COMPASS_USERNAME')
    password = os.getenv('COMPASS_PASSWORD')

    if not all([base_url, username, password]):
        print("Error: COMPASS_BASE_URL, COMPASS_USERNAME, and COMPASS_PASSWORD must be set in .env")
        sys.exit(1)

    # Ensure base_url has https://
    if not base_url.startswith('http'):
        base_url = f'https://{base_url}'

    # Create output directory
    output_dir = Path(__file__).parent.parent / 'data' / 'mock'
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Connecting to Compass at {base_url}...")
    client = CompassClient(base_url, username, password)

    try:
        # Authenticate
        print("Authenticating...")
        client.login()
        print("✓ Authenticated successfully")

        # Fetch user details
        print("Fetching user details...")
        user_details = client.get_user_details()
        print(f"✓ Fetched user details for {user_details.get('userFullName', 'unknown')}")

        # Save user details
        user_details_file = output_dir / 'compass_user_details.json'
        with open(user_details_file, 'w') as f:
            json.dump(user_details, f, indent=2, default=str)
        print(f"✓ Saved user details to {user_details_file}")

        # Fetch events for next 30 days
        start_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

        print(f"Fetching events from {start_date} to {end_date}...")
        events = client.get_calendar_events(start_date, end_date, limit=100)
        print(f"✓ Fetched {len(events)} events")

        # Save events
        events_file = output_dir / 'compass_events.json'
        with open(events_file, 'w') as f:
            json.dump(events, f, indent=2, default=str)
        print(f"✓ Saved events to {events_file}")

        print("\nSuccess! Mock data collected.")
        print(f"  User: {user_details.get('userFullName', 'unknown')}")
        print(f"  Total events: {len(events)}")
        print(f"  Date range: {start_date} to {end_date}")
        print(f"  Output files:")
        print(f"    - {user_details_file}")
        print(f"    - {events_file}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        client.close()


if __name__ == '__main__':
    main()
