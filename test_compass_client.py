#!/usr/bin/env python3
"""
Test script for Compass API client implementation.

This script demonstrates how to use the CompassClient and CompassMockClient,
and generates sample data that can inform database schemas.
"""

import json
from datetime import datetime, timedelta
from src.adapters.compass_mock import CompassMockClient
from src.adapters.compass import CompassClient


def test_mock_client():
    """Test the mock Compass client."""
    print("\n" + "="*60)
    print("Testing CompassMockClient")
    print("="*60)

    # Initialize mock client
    client = CompassMockClient(
        base_url="https://mock.compass.example.com",
        username="test_user",
        password="test_password"
    )

    # Login
    print("\n1. Testing login...")
    if client.login():
        print("✓ Login successful")

    # Fetch events
    print("\n2. Testing event fetching...")
    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

    events = client.get_calendar_events(start_date, end_date, limit=100)
    print(f"✓ Retrieved {len(events)} events")

    # Display sample data
    print("\n3. Sample Events Structure:")
    print("-" * 60)
    if events:
        for i, event in enumerate(events[:3], 1):  # Show first 3 events
            print(f"\nEvent {i}:")
            print(json.dumps(event, indent=2))

    # Analyze event structure
    print("\n4. Event Data Analysis:")
    print("-" * 60)
    if events:
        first_event = events[0]
        print(f"Event fields present: {list(first_event.keys())}")
        print(f"\nData types:")
        for key, value in first_event.items():
            print(f"  {key}: {type(value).__name__}")

    client.close()
    return events


def test_real_client_with_credentials():
    """
    Test the real Compass client with provided credentials.

    Returns instructions for the user to provide credentials.
    """
    print("\n" + "="*60)
    print("Testing CompassClient (Real API)")
    print("="*60)

    print("\nTo test with real Compass credentials:")
    print("-" * 60)
    print("""
You can test the real Compass client by running:

    python -c "
from src.adapters.compass import CompassClient
import json
from datetime import datetime, timedelta

# Create client with your credentials
client = CompassClient(
    base_url='https://your-compass-instance.edu.au',
    username='your_username',
    password='your_password'
)

# Login
print('Logging in...')
client.login()
print('✓ Login successful')

# Fetch events
start_date = datetime.now().strftime('%Y-%m-%d')
end_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')

print(f'Fetching events from {start_date} to {end_date}...')
events = client.get_calendar_events(start_date, end_date)
print(f'✓ Retrieved {len(events)} events')

# Display first event
if events:
    print('\nFirst event:')
    print(json.dumps(events[0], indent=2))

client.close()
    "
    """)


def analyze_schema_requirements(events):
    """Analyze sample events to determine database schema requirements."""
    print("\n" + "="*60)
    print("Database Schema Requirements")
    print("="*60)

    if not events:
        print("No events to analyze")
        return

    # Collect all unique fields
    all_fields = set()
    for event in events:
        all_fields.update(event.keys())

    print("\n1. RawEvent Table Fields:")
    print("-" * 60)
    print("Fields found in events:")
    for field in sorted(all_fields):
        print(f"  • {field}")

    print("\n2. Suggested Schema:")
    print("-" * 60)
    print("""
CREATE TABLE raw_events (
    id TEXT PRIMARY KEY,
    compass_id TEXT NOT NULL,
    long_title TEXT NOT NULL,
    long_title_without_time TEXT,
    start_datetime TIMESTAMP NOT NULL,
    finish_datetime TIMESTAMP,
    all_day BOOLEAN,
    subject_title TEXT,
    subject_long_name TEXT,
    locations JSON,  -- Array of location objects
    managers JSON,   -- Array of manager objects
    roll_marked BOOLEAN,
    description TEXT,
    raw_data JSON,   -- Store entire event for reference
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE filtered_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_event_id TEXT FOREIGN KEY,
    user_config_id INTEGER FOREIGN KEY,
    is_relevant BOOLEAN,
    reasoning TEXT,
    action_needed TEXT,
    filtered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_name TEXT NOT NULL,
    school TEXT,
    year_level TEXT,
    class TEXT,
    interests JSON,
    filter_rules TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL UNIQUE,  -- 'compass', 'classdojo', etc.
    username TEXT NOT NULL,
    password_encrypted TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
    """)

    print("\n3. Event Type Distribution:")
    print("-" * 60)
    event_types = {}
    for event in events:
        event_type = event.get('subjectTitle', 'Unknown')
        event_types[event_type] = event_types.get(event_type, 0) + 1

    for event_type, count in sorted(event_types.items()):
        print(f"  {event_type}: {count}")

    print("\n4. Sample Queries:")
    print("-" * 60)
    print("""
-- Get all relevant events for a child in the next 7 days
SELECT re.*
FROM raw_events re
JOIN filtered_events fe ON re.id = fe.raw_event_id
WHERE fe.user_config_id = ?
  AND fe.is_relevant = true
  AND re.start_datetime <= datetime('now', '+7 days')
  AND re.start_datetime >= datetime('now')
ORDER BY re.start_datetime;

-- Get events requiring action
SELECT re.*, fe.action_needed
FROM raw_events re
JOIN filtered_events fe ON re.id = fe.raw_event_id
WHERE fe.user_config_id = ?
  AND fe.action_needed IS NOT NULL
ORDER BY re.start_datetime;
    """)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Bellbird Compass API Client - Test Suite")
    print("="*60)

    # Test mock client
    mock_events = test_mock_client()

    # Analyze schema requirements
    analyze_schema_requirements(mock_events)

    # Test real client
    test_real_client_with_credentials()

    print("\n" + "="*60)
    print("Test Complete")
    print("="*60)
    print("\nNext steps:")
    print("1. Review the database schema suggested above")
    print("2. Implement src/db/models.py with SQLAlchemy models")
    print("3. Test with real Compass credentials when ready")
    print("="*60 + "\n")
