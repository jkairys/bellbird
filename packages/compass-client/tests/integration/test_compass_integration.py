"""Integration tests for CompassClient against real Compass API.

These tests require valid Compass credentials in environment variables or .env file:
- COMPASS_BASE_URL
- COMPASS_USERNAME
- COMPASS_PASSWORD

Run with: pytest -v -m integration

Skip with: pytest -v -m "not integration"
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from dotenv import load_dotenv

from compass_client import CompassClient, CompassParser, CompassEvent, CompassUser
from compass_client.exceptions import CompassAuthenticationError, CompassClientError


# Load .env file from project root
env_path = Path(__file__).parent.parent.parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Skip all tests in this module if credentials not available
pytestmark = pytest.mark.skipif(
    not all([
        os.getenv("COMPASS_BASE_URL"),
        os.getenv("COMPASS_USERNAME"),
        os.getenv("COMPASS_PASSWORD"),
    ]),
    reason="Compass credentials not available in environment or .env file"
)


@pytest.fixture(scope="module")
def compass_credentials():
    """Get Compass credentials from environment."""
    base_url = os.getenv("COMPASS_BASE_URL")

    # Ensure base_url has a scheme (add https:// if missing)
    if base_url and not base_url.startswith(("http://", "https://")):
        base_url = f"https://{base_url}"

    return {
        "base_url": base_url,
        "username": os.getenv("COMPASS_USERNAME"),
        "password": os.getenv("COMPASS_PASSWORD"),
    }


@pytest.fixture(scope="module")
def authenticated_client(compass_credentials):
    """Create and authenticate a CompassClient.

    This fixture is module-scoped to reuse authentication across tests.
    """
    client = CompassClient(
        compass_credentials["base_url"],
        compass_credentials["username"],
        compass_credentials["password"],
    )

    # Authenticate
    success = client.login()
    assert success is True
    assert client._authenticated is True

    return client


@pytest.mark.integration
class TestCompassClientAuthentication:
    """Integration tests for Compass authentication."""

    def test_login_success(self, compass_credentials):
        """Test successful login with valid credentials."""
        client = CompassClient(
            compass_credentials["base_url"],
            compass_credentials["username"],
            compass_credentials["password"],
        )

        result = client.login()

        assert result is True
        assert client._authenticated is True

    def test_login_invalid_credentials(self, compass_credentials):
        """Test login failure with invalid credentials."""
        client = CompassClient(
            compass_credentials["base_url"],
            "invalid_username",
            "invalid_password",
        )

        with pytest.raises(CompassAuthenticationError) as exc_info:
            client.login()

        assert "login failed" in str(exc_info.value).lower() or "incorrect" in str(exc_info.value).lower()


@pytest.mark.integration
class TestCompassClientUserDetails:
    """Integration tests for fetching user details."""

    def test_get_user_details_success(self, authenticated_client):
        """Test fetching user details from real API."""
        user_data = authenticated_client.get_user_details()

        # Verify structure of real API response
        assert isinstance(user_data, dict)
        assert "userId" in user_data
        assert "userFirstName" in user_data
        assert "userLastName" in user_data
        assert isinstance(user_data["userId"], int)

        # Verify client state updated
        assert authenticated_client.user_id == user_data["userId"]

    def test_parse_user_details(self, authenticated_client):
        """Test that user details can be parsed into CompassUser model."""
        user_data = authenticated_client.get_user_details()

        # Parse into Pydantic model
        user = CompassParser.parse(CompassUser, user_data)

        assert isinstance(user, CompassUser)
        assert user.user_id > 0
        assert len(user.user_first_name) > 0
        assert len(user.user_last_name) > 0

    def test_get_user_details_requires_authentication(self, compass_credentials):
        """Test that get_user_details fails when not authenticated."""
        client = CompassClient(
            compass_credentials["base_url"],
            compass_credentials["username"],
            compass_credentials["password"],
        )
        # Don't call login()

        with pytest.raises(CompassClientError) as exc_info:
            client.get_user_details()

        assert "not authenticated" in str(exc_info.value).lower()


@pytest.mark.integration
class TestCompassClientCalendarEvents:
    """Integration tests for fetching calendar events."""

    def test_get_calendar_events_success(self, authenticated_client):
        """Test fetching calendar events from real API."""
        # Get events for next 30 days
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        events_data = authenticated_client.get_calendar_events(
            start_date=start_date,
            end_date=end_date,
            limit=10
        )

        # Verify structure of real API response
        assert isinstance(events_data, list)

        # If there are events, verify structure
        if len(events_data) > 0:
            first_event = events_data[0]
            assert isinstance(first_event, dict)
            assert "title" in first_event
            assert "start" in first_event
            assert "finish" in first_event

    def test_parse_calendar_events(self, authenticated_client):
        """Test that calendar events can be parsed into CompassEvent models."""
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        events_data = authenticated_client.get_calendar_events(
            start_date=start_date,
            end_date=end_date,
            limit=5
        )

        # Parse into Pydantic models (use safe mode to handle any schema variations)
        events, errors = CompassParser.parse_safe(CompassEvent, events_data)

        # Should successfully parse at least some events
        assert isinstance(events, list)

        if len(events_data) > 0:
            # If API returned events, we should parse at least some
            assert len(events) > 0

            # Verify first event structure
            first_event = events[0]
            assert isinstance(first_event, CompassEvent)
            assert len(first_event.title) > 0
            assert isinstance(first_event.start, datetime)
            assert isinstance(first_event.finish, datetime)

    def test_get_calendar_events_empty_range(self, authenticated_client):
        """Test fetching events for a date range with no events."""
        # Get events from far future (unlikely to have events)
        start_date = "2099-01-01"
        end_date = "2099-01-31"

        events_data = authenticated_client.get_calendar_events(
            start_date=start_date,
            end_date=end_date,
            limit=100
        )

        # Should return empty list, not error
        assert isinstance(events_data, list)
        assert len(events_data) == 0

    def test_get_calendar_events_with_limit_parameter(self, authenticated_client):
        """Test that limit parameter is accepted (note: API may not actually enforce it)."""
        start_date = "2025-01-01"
        end_date = "2025-12-31"
        limit = 3

        # Note: The Compass API accepts the limit parameter but may not enforce it
        # This test verifies the client can send the parameter without error
        events_data = authenticated_client.get_calendar_events(
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )

        # Should return list (API may return more than limit)
        assert isinstance(events_data, list)

    def test_get_calendar_events_requires_authentication(self, compass_credentials):
        """Test that get_calendar_events fails when not authenticated."""
        client = CompassClient(
            compass_credentials["base_url"],
            compass_credentials["username"],
            compass_credentials["password"],
        )
        # Don't call login()

        with pytest.raises(CompassClientError) as exc_info:
            client.get_calendar_events("2025-01-01", "2025-12-31", 100)

        assert "not authenticated" in str(exc_info.value).lower()


@pytest.mark.integration
class TestCompassClientEndToEnd:
    """End-to-end integration tests."""

    def test_full_workflow(self, compass_credentials):
        """Test complete workflow: login, get user, get events, parse."""
        # 1. Create client
        client = CompassClient(
            compass_credentials["base_url"],
            compass_credentials["username"],
            compass_credentials["password"],
        )

        # 2. Authenticate
        assert client.login() is True

        # 3. Get and parse user details
        user_data = client.get_user_details()
        user = CompassParser.parse(CompassUser, user_data)
        assert user.user_id > 0

        # 4. Get and parse calendar events
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        events_data = client.get_calendar_events(start_date, end_date, 10)
        events, errors = CompassParser.parse_safe(CompassEvent, events_data)

        # Should complete without errors
        assert isinstance(events, list)
        assert isinstance(errors, list)

    def test_session_reuse(self, authenticated_client):
        """Test that the same session can be used for multiple requests."""
        # Make multiple requests with same client
        user_data_1 = authenticated_client.get_user_details()
        user_data_2 = authenticated_client.get_user_details()

        # Should get same user both times
        assert user_data_1["userId"] == user_data_2["userId"]

        # Get events
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        events_1 = authenticated_client.get_calendar_events(start_date, end_date, 5)
        events_2 = authenticated_client.get_calendar_events(start_date, end_date, 5)

        # Should work consistently
        assert isinstance(events_1, list)
        assert isinstance(events_2, list)
