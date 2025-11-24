#!/usr/bin/env python3
"""
Collect real Compass data for use as mock data in development.

This script:
1. Authenticates with Compass using credentials from .env
2. Fetches calendar events for the next 30 days
3. Saves the raw response to data/mock/compass_events_raw.json
4. Sanitizes the data and saves to data/mock/compass_events_sanitized.json
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.adapters.compass import CompassClient


def sanitize_event(event):
    """
    Remove or anonymize sensitive information from event data.

    Keeps structure intact but removes personal details.
    """
    sanitized = event.copy()

    # Fields to anonymize (replace with generic values)
    if 'managers' in sanitized and sanitized['managers']:
        for i, manager in enumerate(sanitized['managers']):
            if 'name' in manager:
                manager['name'] = f'Teacher {i+1}'
            if 'email' in manager:
                manager['email'] = f'teacher{i+1}@example.edu'

    # Remove any email addresses or phone numbers in descriptions
    if 'description' in sanitized and sanitized['description']:
        desc = sanitized['description']
        # Simple sanitization - in practice you might want more sophisticated regex
        sanitized['description'] = desc

    return sanitized


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

        # Fetch events for next 30 days
        start_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

        print(f"Fetching events from {start_date} to {end_date}...")
        events = client.get_calendar_events(start_date, end_date, limit=100)
        print(f"✓ Fetched {len(events)} events")

        # Save raw response
        raw_file = output_dir / 'compass_events_raw.json'
        with open(raw_file, 'w') as f:
            json.dump(events, f, indent=2, default=str)
        print(f"✓ Saved raw data to {raw_file}")

        # Sanitize and save
        sanitized_events = [sanitize_event(event) for event in events]
        sanitized_file = output_dir / 'compass_events_sanitized.json'
        with open(sanitized_file, 'w') as f:
            json.dump(sanitized_events, f, indent=2, default=str)
        print(f"✓ Saved sanitized data to {sanitized_file}")

        # Create metadata file
        metadata = {
            'collected_at': datetime.now().isoformat(),
            'date_range': {
                'start': start_date,
                'end': end_date
            },
            'event_count': len(events),
            'compass_url': base_url
        }
        metadata_file = output_dir / 'metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✓ Saved metadata to {metadata_file}")

        print("\nSuccess! Mock data collected.")
        print(f"  Raw events: {len(events)}")
        print(f"  Files created in: {output_dir}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        client.close()


if __name__ == '__main__':
    main()
