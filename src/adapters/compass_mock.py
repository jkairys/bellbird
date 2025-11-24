"""
Mock Compass client for testing without real credentials.

Returns realistic calendar events from collected mock data for development and testing.
"""

import json
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path


class CompassMockClient:
    """
    Mock Compass client for testing without real credentials.

    Returns calendar events from data/mock/compass_events_sanitized.json
    collected by scripts/collect_mock_data.py. Falls back to hardcoded
    synthetic events if the file doesn't exist.
    """

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.user_id = 12345
        self._authenticated = False
        self._events = self._load_mock_events()

    def _load_mock_events(self) -> List[Dict[str, Any]]:
        """
        Load mock events from data/mock/compass_events_sanitized.json.

        Falls back to hardcoded synthetic events if file doesn't exist.
        """
        mock_file = Path(__file__).parent.parent.parent / 'data' / 'mock' / 'compass_events_sanitized.json'

        if mock_file.exists():
            try:
                with open(mock_file, 'r') as f:
                    events = json.load(f)
                return events
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load mock data from {mock_file}: {e}")
                print("Falling back to hardcoded synthetic events")

        # Fallback: hardcoded synthetic events
        return self._get_fallback_events()

    def _get_fallback_events(self) -> List[Dict[str, Any]]:
        """
        Return hardcoded synthetic events as fallback.

        Used when data/mock/compass_events_sanitized.json doesn't exist.
        """
        return [
            {
                'activityId': 1,
                'longTitle': 'Year 3 Excursion to Taronga Zoo',
                'longTitleWithoutTime': 'Year 3 Excursion to Taronga Zoo',
                'start': '2025-11-29T09:00:00Z',
                'finish': '2025-11-29T12:00:00Z',
                'allDay': False,
                'locations': [{'locationName': 'Taronga Zoo'}],
                'managers': [{'managerUserId': 1001}],
                'description': 'Permission slip required. Cost: $25'
            },
            {
                'activityId': 2,
                'longTitle': 'Year 3 Music Performance',
                'longTitleWithoutTime': 'Year 3 Music Performance',
                'start': '2025-12-04T18:00:00Z',
                'finish': '2025-12-04T19:00:00Z',
                'allDay': False,
                'locations': [{'locationName': 'School Hall'}],
                'managers': [{'managerUserId': 1002}],
                'description': 'Evening performance. Tickets available online.'
            },
            {
                'activityId': 3,
                'longTitle': 'Free Dress Day - Community Fund',
                'longTitleWithoutTime': 'Free Dress Day',
                'start': '2025-11-27T00:00:00Z',
                'finish': '2025-11-27T23:59:59Z',
                'allDay': True,
                'locations': [{'locationName': 'School'}],
                'managers': [{'managerUserId': 1003}],
                'description': 'Wear your favorite outfit. Gold coin donation.'
            },
        ]

    def login(self) -> bool:
        """Mock login - always succeeds."""
        self._authenticated = True
        return True

    def get_calendar_events(
        self,
        start_date: str,
        end_date: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Return calendar events from mock data or fallback synthetic events.

        Filters events by date range and applies limit.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Maximum number of events to return (default 100)

        Returns:
            List of calendar event dictionaries
        """
        if not self._authenticated:
            raise Exception("Not authenticated")

        # Parse date range
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        # Filter events by date range
        filtered = []
        for event in self._events:
            try:
                # Handle different date formats
                event_start_str = event.get('start', '')
                if not event_start_str:
                    continue

                # Parse ISO format date (with or without timezone)
                if 'T' in event_start_str:
                    event_start = datetime.fromisoformat(event_start_str.replace('Z', '+00:00'))
                else:
                    event_start = datetime.strptime(event_start_str, '%Y-%m-%d')

                # Compare dates (ignore time for range comparison)
                event_date = event_start.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
                if start <= event_date <= end:
                    filtered.append(event)
            except (ValueError, AttributeError):
                # Skip events with invalid date formats
                continue

        # Apply limit
        return filtered[:limit]

    def close(self) -> None:
        """Mock close."""
        pass
