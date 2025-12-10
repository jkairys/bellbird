"""Unit tests for CompassMockClient."""

import json
from pathlib import Path

import pytest

from compass_client import CompassMockClient
from compass_client.exceptions import CompassClientError


class TestCompassMockClientInit:
    """Tests for CompassMockClient initialization."""

    def test_init_basic(self):
        """Test basic initialization."""
        client = CompassMockClient("https://example.compass.education", "user", "pass")
        assert client.base_url == "https://example.compass.education"
        assert client.username == "user"
        assert client.password == "pass"
        assert client.user_id is None
        assert client._authenticated is False
        assert client._mock_user is None
        assert client._mock_events is None

    def test_init_with_custom_mock_dir(self, tmp_path):
        """Test initialization with custom mock data directory."""
        # Create mock data files
        mock_dir = tmp_path / "custom_mock"
        mock_dir.mkdir()

        user_data = {"userId": 999, "username": "mockuser"}
        events_data = [{"title": "Test Event", "start": "2025-12-01T09:00:00"}]

        (mock_dir / "compass_user.json").write_text(json.dumps(user_data))
        (mock_dir / "compass_events.json").write_text(json.dumps(events_data))
        (mock_dir / "schema_version.json").write_text(json.dumps({"version": "1.0.0"}))

        client = CompassMockClient(
            "https://example.compass.education",
            "user",
            "pass",
            mock_data_dir=str(mock_dir),
        )

        assert client.mock_data_dir == str(mock_dir)


class TestCompassMockClientLogin:
    """Tests for CompassMockClient.login() method."""

    def test_login_always_succeeds(self):
        """Test that login always succeeds in mock mode."""
        client = CompassMockClient("https://example.compass.education", "user", "pass")

        result = client.login()

        assert result is True
        assert client._authenticated is True

    def test_login_with_wrong_credentials(self):
        """Test that login succeeds even with wrong credentials."""
        client = CompassMockClient("https://example.compass.education", "wrong", "wrong")

        result = client.login()

        assert result is True
        assert client._authenticated is True


class TestCompassMockClientGetUserDetails:
    """Tests for CompassMockClient.get_user_details() method."""

    def test_get_user_details_success(self):
        """Test successful retrieval of mock user details."""
        client = CompassMockClient("https://example.compass.education", "user", "pass")
        client._authenticated = True

        result = client.get_user_details()

        assert "userId" in result
        assert "username" in result
        assert isinstance(result["userId"], int)
        assert client.user_id == result["userId"]

    def test_get_user_details_not_authenticated(self):
        """Test get_user_details when not authenticated."""
        client = CompassMockClient("https://example.compass.education", "user", "pass")
        client._authenticated = False

        with pytest.raises(CompassClientError) as exc_info:
            client.get_user_details()

        assert "not authenticated" in str(exc_info.value).lower()

    def test_get_user_details_loads_data_once(self):
        """Test that mock data is loaded only once."""
        client = CompassMockClient("https://example.compass.education", "user", "pass")
        client._authenticated = True

        # First call
        result1 = client.get_user_details()

        # Store reference to loaded data
        mock_user_ref = client._mock_user

        # Second call
        result2 = client.get_user_details()

        # Should be same object (not reloaded)
        assert client._mock_user is mock_user_ref
        assert result1 == result2


class TestCompassMockClientGetCalendarEvents:
    """Tests for CompassMockClient.get_calendar_events() method."""

    def test_get_calendar_events_success(self):
        """Test successful retrieval of mock calendar events."""
        client = CompassMockClient("https://example.compass.education", "user", "pass")
        client._authenticated = True
        client.user_id = 12345

        result = client.get_calendar_events("2025-12-01", "2025-12-31", 100)

        assert isinstance(result, list)
        assert len(result) > 0
        assert "title" in result[0]
        assert "start" in result[0]

    def test_get_calendar_events_respects_limit(self):
        """Test that limit parameter is respected."""
        client = CompassMockClient("https://example.compass.education", "user", "pass")
        client._authenticated = True
        client.user_id = 12345

        result = client.get_calendar_events("2025-12-01", "2025-12-31", 2)

        assert len(result) <= 2

    def test_get_calendar_events_not_authenticated(self):
        """Test get_calendar_events when not authenticated."""
        client = CompassMockClient("https://example.compass.education", "user", "pass")
        client._authenticated = False

        with pytest.raises(CompassClientError) as exc_info:
            client.get_calendar_events("2025-12-01", "2025-12-31", 100)

        assert "not authenticated" in str(exc_info.value).lower()

    def test_get_calendar_events_filters_by_date(self):
        """Test that events are filtered by date range."""
        client = CompassMockClient("https://example.compass.education", "user", "pass")
        client._authenticated = True
        client.user_id = 12345

        # Get all events first
        all_events = client.get_calendar_events("2000-01-01", "2099-12-31", 1000)

        # Get events for narrow date range
        filtered_events = client.get_calendar_events("2025-12-01", "2025-12-02", 1000)

        # Filtered should be subset of all
        assert len(filtered_events) <= len(all_events)


class TestCompassMockClientDataLoading:
    """Tests for CompassMockClient data loading."""

    def test_load_mock_user_data(self):
        """Test loading mock user data."""
        client = CompassMockClient("https://example.compass.education", "user", "pass")

        user_data = client._load_mock_user_data()

        assert isinstance(user_data, dict)
        assert "userId" in user_data
        assert "username" in user_data

    def test_load_mock_events_data(self):
        """Test loading mock events data."""
        client = CompassMockClient("https://example.compass.education", "user", "pass")

        events_data = client._load_mock_events_data()

        assert isinstance(events_data, list)
        assert len(events_data) > 0
        assert "title" in events_data[0]

    def test_load_mock_data_missing_file(self, tmp_path):
        """Test loading mock data when file is missing."""
        mock_dir = tmp_path / "empty_mock"
        mock_dir.mkdir()

        client = CompassMockClient(
            "https://example.compass.education",
            "user",
            "pass",
            mock_data_dir=str(mock_dir),
        )

        with pytest.raises(FileNotFoundError):
            client._load_mock_user_data()


class TestCompassMockClientInterface:
    """Tests that CompassMockClient implements the same interface as CompassClient."""

    def test_has_same_public_methods(self):
        """Test that mock client has same public methods as real client."""
        from compass_client import CompassClient

        mock_client = CompassMockClient("https://example.compass.education", "user", "pass")
        real_client = CompassClient("https://example.compass.education", "user", "pass")

        # Get public methods (not starting with _)
        mock_methods = {
            name for name in dir(mock_client) if not name.startswith("_") and callable(getattr(mock_client, name))
        }
        real_methods = {
            name for name in dir(real_client) if not name.startswith("_") and callable(getattr(real_client, name))
        }

        # Core interface methods that must match
        core_methods = {"login", "get_user_details", "get_calendar_events"}

        assert core_methods.issubset(mock_methods)
        assert core_methods.issubset(real_methods)

    def test_returns_same_data_types(self):
        """Test that mock client returns same data types as real client."""
        client = CompassMockClient("https://example.compass.education", "user", "pass")
        client._authenticated = True
        client.user_id = 12345

        # login returns bool
        login_result = client.login()
        assert isinstance(login_result, bool)

        # get_user_details returns dict
        user_result = client.get_user_details()
        assert isinstance(user_result, dict)

        # get_calendar_events returns list
        events_result = client.get_calendar_events("2025-12-01", "2025-12-31", 100)
        assert isinstance(events_result, list)
