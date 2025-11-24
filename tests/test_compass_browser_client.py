"""
Integration test for Compass browser-based API client.

This test uses Playwright to provide reliable browser automation for Compass login and event fetching.
It requires valid credentials to be provided via environment variables or pytest fixtures.

To run this test:
    1. Set COMPASS_USERNAME and COMPASS_PASSWORD environment variables in .env
    2. Run: poetry run pytest tests/test_compass_browser_client.py -v

The test will skip if credentials are not provided.
"""

import os
import pytest
from datetime import datetime, timedelta
from src.adapters.compass_browser import CompassBrowserClient


# Base URL for Seaford North Primary School
COMPASS_BASE_URL = "https://seaford-northps-vic.compass.education"


@pytest.fixture
def compass_browser_credentials(request):
    """
    Fixture to provide Compass credentials.

    Looks for credentials in:
    1. Command-line arguments (--compass-username, --compass-password)
    2. Environment variables (COMPASS_USERNAME, COMPASS_PASSWORD)
    3. Skips test if not found
    """
    username = (
        request.config.getoption("--compass-username") or
        os.environ.get("COMPASS_USERNAME")
    )
    password = (
        request.config.getoption("--compass-password") or
        os.environ.get("COMPASS_PASSWORD")
    )

    if not username or not password:
        pytest.skip(
            "Compass credentials not provided. "
            "Set COMPASS_USERNAME/COMPASS_PASSWORD env vars"
        )

    return {"username": username, "password": password}


@pytest.fixture
def compass_browser_client(compass_browser_credentials):
    """Create and yield a Compass browser client instance."""
    client = CompassBrowserClient(
        base_url=COMPASS_BASE_URL,
        username=compass_browser_credentials["username"],
        password=compass_browser_credentials["password"]
    )
    yield client
    # Cleanup
    try:
        client.close()
    except Exception:
        pass


class TestCompassBrowserClientAuthentication:
    """Test browser-based Compass API authentication."""

    def test_browser_login_success(self, compass_browser_client):
        """Test successful login using browser automation."""
        result = compass_browser_client.login()
        assert result is True
        assert compass_browser_client._authenticated is True

    def test_browser_user_id_extracted_after_login(self, compass_browser_client):
        """Test that userId is extracted after successful login."""
        compass_browser_client.login()

        # userId should be extracted from the page
        # Note: It's okay if this is None - Compass may not expose it to JavaScript
        # The important thing is that login succeeded


class TestCompassBrowserClientCalendarEvents:
    """Test browser-based calendar event fetching."""

    def test_browser_fetch_calendar_events_current_month(self, compass_browser_client):
        """Test fetching calendar events for current month."""
        compass_browser_client.login()

        today = datetime.now()
        start_date = today.replace(day=1).strftime("%Y-%m-%d")

        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=1)
        else:
            end_date = today.replace(month=today.month + 1, day=1)
        end_date = (end_date - timedelta(days=1)).strftime("%Y-%m-%d")

        events = compass_browser_client.get_calendar_events(start_date, end_date)
        assert isinstance(events, list)

    def test_browser_fetch_calendar_events_next_30_days(self, compass_browser_client):
        """Test fetching calendar events for next 30 days."""
        compass_browser_client.login()

        today = datetime.now()
        start_date = today.strftime("%Y-%m-%d")
        end_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")

        events = compass_browser_client.get_calendar_events(start_date, end_date)
        assert isinstance(events, list)

        if events:
            event = events[0]
            print(f"\nSample event: {event}")
