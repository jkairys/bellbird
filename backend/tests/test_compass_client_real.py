"""
Integration test for real Compass API client.

This test uses the real CompassClient to interact with a live Compass instance.
It requires valid credentials to be provided via environment variables or pytest fixtures.

To run this test:
    1. Set COMPASS_USERNAME and COMPASS_PASSWORD environment variables, OR
    2. Pass credentials via command-line:
       pytest tests/test_compass_client_real.py --compass-username=X --compass-password=Y

The test will skip if credentials are not provided.
"""

import os
from datetime import datetime, timedelta

import pytest
from src.adapters.compass import CompassClient

# Base URL for Seaford North Primary School
COMPASS_BASE_URL = "https://seaford-northps-vic.compass.education"


@pytest.fixture(scope="session")
def compass_credentials(request):
    """
    Fixture to provide Compass credentials.

    Looks for credentials in:
    1. Command-line arguments (--compass-username, --compass-password)
    2. Environment variables (COMPASS_USERNAME, COMPASS_PASSWORD)
    3. Skips test if not found
    """
    username = request.config.getoption("--compass-username") or os.environ.get("COMPASS_USERNAME")
    password = request.config.getoption("--compass-password") or os.environ.get("COMPASS_PASSWORD")

    if not username or not password:
        pytest.skip(
            "Compass credentials not provided. "
            "Set COMPASS_USERNAME/COMPASS_PASSWORD env vars or use "
            "--compass-username and --compass-password flags"
        )

    return {"username": username, "password": password}


@pytest.fixture(scope="session")
def compass_client(compass_credentials):
    """Create and yield a Compass client instance."""
    client = CompassClient(
        base_url=COMPASS_BASE_URL,
        username=compass_credentials["username"],
        password=compass_credentials["password"],
    )
    client.login()
    if not client._authenticated:
        pytest.skip("Failed to authenticate with provided Compass credentials.")
    yield client
    # Cleanup
    try:
        client.close()
    except Exception:
        pass


class TestCompassClientRealAuthentication:
    """Test real Compass API authentication."""

    def test_login_success(self, compass_client):
        """Test successful login to Compass."""
        # Should not raise an exception
        result = compass_client.login()
        assert result is True
        assert compass_client._authenticated is True

    def test_user_id_extracted_after_login(self, compass_client):
        """Test that userId is extracted after successful login."""
        compass_client.login()

        # userId should be extracted from the login response
        assert compass_client.user_id is not None
        assert isinstance(compass_client.user_id, int)
        assert compass_client.user_id > 0

    def test_session_established(self, compass_client):
        """Test that session cookies are established after login."""
        compass_client.login()

        # Session should have cookies from the login response
        assert len(compass_client.session.cookies) > 0


class TestCompassClientRealCalendarEvents:
    """Test real Compass API calendar event fetching."""

    def test_fetch_calendar_events_current_month(self, compass_client):
        """Test fetching calendar events for current month."""
        compass_client.login()

        # Get events for current month
        today = datetime.now()
        start_date = today.replace(day=1).strftime("%Y-%m-%d")

        # Last day of current month
        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=1)
        else:
            end_date = today.replace(month=today.month + 1, day=1)
        end_date = (end_date - timedelta(days=1)).strftime("%Y-%m-%d")

        events = compass_client.get_calendar_events(start_date, end_date)

        # Should return a list (may be empty if no events)
        assert isinstance(events, list)

        # If there are events, they should have expected properties
        if events:
            first_event = events[0]
            assert isinstance(first_event, dict)

    def test_fetch_calendar_events_next_30_days(self, compass_client):
        """Test fetching calendar events for next 30 days."""
        compass_client.login()

        today = datetime.now()
        start_date = today.strftime("%Y-%m-%d")
        end_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")

        events = compass_client.get_calendar_events(start_date, end_date)

        # Should return a list
        assert isinstance(events, list)

        # Inspect event structure if events exist
        if events:
            event = events[0]
            # Events should be dictionaries
            assert isinstance(event, dict)
            print(f"\nSample event structure: {event}")

    def test_fetch_calendar_events_empty_range(self, compass_client):
        """Test fetching events from a date range far in the past."""
        compass_client.login()

        # Query for a date range in the past
        start_date = "2020-01-01"
        end_date = "2020-01-31"

        events = compass_client.get_calendar_events(start_date, end_date)

        # Should return a list (likely empty)
        assert isinstance(events, list)

    def test_fetch_calendar_events_single_day(self, compass_client):
        """Test fetching events for a single day."""
        compass_client.login()

        today = datetime.now()
        date_str = today.strftime("%Y-%m-%d")

        events = compass_client.get_calendar_events(date_str, date_str)

        # Should return a list
        assert isinstance(events, list)

    def test_calendar_events_has_expected_fields(self, compass_client):
        """Test that calendar events have expected Compass fields."""
        compass_client.login()

        today = datetime.now()
        start_date = today.strftime("%Y-%m-%d")
        end_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")

        events = compass_client.get_calendar_events(start_date, end_date, limit=10)

        # If events are returned, check their structure
        if events:
            event = events[0]
            # Compass events typically have these fields
            # (exact fields may vary, this is informational)
            print(f"\nEvent keys present: {list(event.keys())}")
            print(f"Full event: {event}")


class TestCompassClientRealEdgeCases:
    """Test edge cases and error handling."""

    def test_fetch_events_without_login_fails(self):
        """Test that fetching events without login raises error."""
        client = CompassClient(base_url=COMPASS_BASE_URL, username="dummy", password="dummy")

        with pytest.raises(Exception, match="Not authenticated"):
            client.get_calendar_events("2025-01-01", "2025-01-31")

        client.close()

    def test_client_initialization(self):
        """Test CompassClient initialization."""
        client = CompassClient(
            base_url=COMPASS_BASE_URL, username="test_user", password="test_pass"
        )

        assert client.base_url == COMPASS_BASE_URL
        assert client.username == "test_user"
        assert client.password == "test_pass"
        assert client._authenticated is False
        assert client.user_id is None

        client.close()

    def test_base_url_trailing_slash_handling(self):
        """Test that base URL handles trailing slashes correctly."""
        base_url_with_slash = COMPASS_BASE_URL + "/"
        client = CompassClient(base_url=base_url_with_slash, username="test", password="test")

        # Should remove trailing slash
        assert client.base_url == COMPASS_BASE_URL

        client.close()


class TestCompassClientRealDateRanges:
    """Test various date range scenarios."""

    # def test_fetch_events_reverse_date_range(self, compass_client):
    #     """Test fetching with end_date before start_date (should handle gracefully)."""
    #     compass_client.login()

    #     # Reverse date range
    #     start_date = "2025-12-31"
    #     end_date = "2025-01-01"

    #     # Should either return empty list or handle gracefully
    #     events = compass_client.get_calendar_events(start_date, end_date)
    #     assert isinstance(events, list)

    def test_fetch_events_large_date_range(self, compass_client):
        """Test fetching events over a large date range."""
        compass_client.login()

        # 1 year range
        start_date = "2025-01-01"
        end_date = "2025-12-31"

        events = compass_client.get_calendar_events(start_date, end_date, limit=200)
        assert isinstance(events, list)

    # def test_fetch_events_with_limit(self, compass_client):
    #     """Test that limit parameter works."""
    #     compass_client.login()

    #     today = datetime.now()
    #     start_date = today.strftime("%Y-%m-%d")
    #     end_date = (today + timedelta(days=90)).strftime("%Y-%m-%d")

    #     events = compass_client.get_calendar_events(start_date, end_date, limit=10)

    #     # Should not exceed limit
    #     assert len(events) <= 10
