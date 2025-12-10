"""Unit tests for CompassClient - basic functionality only.

Note: Real API integration tests are in tests/integration/test_compass_integration.py
"""

import pytest

from compass_client import CompassClient


class TestCompassClientInit:
    """Tests for CompassClient initialization."""

    def test_init_basic(self):
        """Test basic initialization."""
        client = CompassClient("https://example.compass.education", "user", "pass")
        assert client.base_url == "https://example.compass.education"
        assert client.username == "user"
        assert client.password == "pass"
        assert client.session is not None
        assert client.user_id is None
        assert client.school_config_key is None
        assert client._authenticated is False

    def test_init_strips_trailing_slash(self):
        """Test that trailing slash is removed from base_url."""
        client = CompassClient("https://example.compass.education/", "user", "pass")
        assert client.base_url == "https://example.compass.education"

    def test_init_sets_headers(self):
        """Test that session headers are set correctly."""
        client = CompassClient("https://example.compass.education", "user", "pass")
        assert "User-Agent" in client.session.headers
        assert "Mozilla" in client.session.headers["User-Agent"]
        assert client.session.headers["Accept-Language"] == "en-AU,en;q=0.9"

    def test_multiple_clients_independent(self):
        """Test that multiple client instances are independent."""
        client1 = CompassClient("https://school1.compass.education", "user1", "pass1")
        client2 = CompassClient("https://school2.compass.education", "user2", "pass2")

        assert client1.base_url != client2.base_url
        assert client1.username != client2.username
        assert client1.session is not client2.session


class TestCompassClientHelpers:
    """Tests for CompassClient helper methods."""

    def test_extract_form_fields(self):
        """Test _extract_form_fields method extracts ASP.NET form fields."""
        html = """
        <form>
            <input name="__VIEWSTATE" value="test_viewstate" />
            <input name="__VIEWSTATEGENERATOR" value="test_generator" />
            <input name="__EVENTVALIDATION" value="test_validation" />
            <input name="username" value="" />
            <input name="password" value="" />
        </form>
        """

        client = CompassClient("https://example.compass.education", "user", "pass")
        result = client._extract_form_fields(html)

        assert "__VIEWSTATE" in result
        assert result["__VIEWSTATE"] == "test_viewstate"
        assert "__VIEWSTATEGENERATOR" in result
        assert result["__VIEWSTATEGENERATOR"] == "test_generator"
        assert "__EVENTVALIDATION" in result
        assert result["__EVENTVALIDATION"] == "test_validation"

    def test_extract_form_fields_no_form(self):
        """Test _extract_form_fields with no form returns empty dict."""
        html = "<div>No form here</div>"

        client = CompassClient("https://example.compass.education", "user", "pass")
        result = client._extract_form_fields(html)

        assert result == {}

    def test_extract_form_fields_with_checkboxes(self):
        """Test _extract_form_fields handles checkbox inputs."""
        html = """
        <form>
            <input type="checkbox" name="rememberMe" value="on" />
            <input type="text" name="username" value="test" />
        </form>
        """

        client = CompassClient("https://example.compass.education", "user", "pass")
        result = client._extract_form_fields(html)

        assert "rememberMe" in result
        assert "username" in result


class TestCompassClientAuthenticationState:
    """Tests for authentication state management."""

    def test_initial_state_not_authenticated(self):
        """Test that client starts in unauthenticated state."""
        client = CompassClient("https://example.compass.education", "user", "pass")
        assert client._authenticated is False
        assert client.user_id is None

    def test_requires_authentication_get_user_details(self):
        """Test that get_user_details requires authentication."""
        client = CompassClient("https://example.compass.education", "user", "pass")
        client._authenticated = False

        from compass_client.exceptions import CompassClientError

        with pytest.raises(CompassClientError) as exc_info:
            client.get_user_details()

        assert "not authenticated" in str(exc_info.value).lower()

    def test_requires_authentication_get_calendar_events(self):
        """Test that get_calendar_events requires authentication."""
        client = CompassClient("https://example.compass.education", "user", "pass")
        client._authenticated = False

        from compass_client.exceptions import CompassClientError

        with pytest.raises(CompassClientError) as exc_info:
            client.get_calendar_events("2025-01-01", "2025-12-31", 100)

        assert "not authenticated" in str(exc_info.value).lower()
