"""
Compass Education API client.

Handles authentication and calendar event fetching without browser automation.
Uses HTTP requests with proper cookie handling for session management.
"""

import requests
import json
import re
from datetime import datetime
from typing import Optional, Dict, List, Any


class CompassClient:
    """
    Python client for Compass Education API.

    Handles authentication and calendar event fetching without browser automation.
    """

    def __init__(self, base_url: str, username: str, password: str):
        """
        Initialize Compass client.

        Args:
            base_url: Base URL of Compass instance (e.g., "https://compass.example.com")
            username: Compass username
            password: Compass password
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.user_id: Optional[int] = None
        self.school_config_key: Optional[str] = None
        self._authenticated = False

    def login(self) -> bool:
        """
        Authenticate with Compass by submitting login form.

        Returns:
            True if successful, raises exception otherwise
        """
        login_url = f"{self.base_url}/login.aspx?sessionstate=disabled"

        # Prepare credentials
        data = {
            'username': self.username,
            'password': self.password
        }

        try:
            # POST login form
            response = self.session.post(
                login_url,
                data=data,
                allow_redirects=True,
                timeout=10
            )
            response.raise_for_status()

            # Verify login was successful
            # Compass redirects to home page or returns auth cookie
            if 'Set-Cookie' not in response.headers and response.status_code != 200:
                raise Exception("Login failed: Invalid credentials or server error")

            # Try to extract userId and schoolConfigKey from the response
            # These may be in JavaScript or HTML meta tags
            self._extract_session_metadata(response.text)

            self._authenticated = True
            return True

        except requests.RequestException as e:
            raise Exception(f"Login request failed: {e}")

    def _extract_session_metadata(self, html_content: str) -> None:
        """
        Extract userId and schoolConfigKey from HTML response.

        These are usually embedded in JavaScript or window object.
        We'll look for them in the initial page load response.
        """
        # Look for patterns like: window.Compass.organisationUserId = 12345
        # or data attributes containing session info

        # Try to find userId in JavaScript
        user_id_match = re.search(r'organisationUserId["\']?\s*[:=]\s*(\d+)', html_content)
        if user_id_match:
            self.user_id = int(user_id_match.group(1))

        # Try to find schoolConfigKey
        key_match = re.search(r'schoolConfigKey["\']?\s*[:=]\s*["\']([^"\']+)["\']', html_content)
        if key_match:
            self.school_config_key = key_match.group(1)

        # If extraction failed, we can fetch these on first API call

    def _ensure_session_metadata(self) -> None:
        """
        Fetch session metadata if not already extracted.

        Makes a request to the home page or an API endpoint to get
        userId and schoolConfigKey if they weren't available after login.
        """
        if self.user_id is None:
            # Fallback: fetch home page and parse again
            response = self.session.get(f"{self.base_url}/home.aspx", timeout=10)
            self._extract_session_metadata(response.text)

        if self.user_id is None:
            raise Exception("Failed to extract userId from Compass session")

    def get_calendar_events(
        self,
        start_date: str,  # YYYY-MM-DD
        end_date: str,    # YYYY-MM-DD
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetch calendar events from Compass for a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Maximum number of events to return (default 100)

        Returns:
            List of calendar event dictionaries
        """
        if not self._authenticated:
            raise Exception("Not authenticated. Call login() first.")

        # Ensure we have the userId
        self._ensure_session_metadata()

        # Build the API request
        api_url = (
            f"{self.base_url}/Services/Calendar.svc/GetCalendarEventsByUser"
            "?sessionstate=readonly&ExcludeNonRelevantPd=true"
        )

        payload = {
            'userId': self.user_id,
            'homePage': True,
            'activityId': None,
            'locationId': None,
            'staffIds': None,
            'startDate': start_date,
            'endDate': end_date,
            'page': 1,
            'start': 0,
            'limit': limit
        }

        try:
            response = self.session.post(
                api_url,
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                timeout=10
            )
            response.raise_for_status()

            # Parse response - Compass wraps result in .d property
            data = response.json()

            # Extract actual events from response
            if isinstance(data, dict) and 'd' in data:
                events = data['d']
            else:
                events = data

            return events if isinstance(events, list) else []

        except requests.RequestException as e:
            raise Exception(f"Failed to fetch calendar events: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response from Compass: {e}")

    def close(self) -> None:
        """Close the session."""
        self.session.close()
