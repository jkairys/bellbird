"""Unit tests for create_client factory function."""

import os
from unittest.mock import patch

import pytest

from compass_client import create_client, CompassClient, CompassMockClient


class TestCreateClientFactory:
    """Tests for create_client() factory function."""

    def test_create_real_client_explicit(self):
        """Test creating real client with explicit mode parameter."""
        client = create_client(
            base_url="https://example.compass.education",
            username="user",
            password="pass",
            mode="real",
        )

        assert isinstance(client, CompassClient)
        assert not isinstance(client, CompassMockClient)
        assert client.base_url == "https://example.compass.education"

    def test_create_mock_client_explicit(self):
        """Test creating mock client with explicit mode parameter."""
        client = create_client(
            base_url="https://example.compass.education",
            username="user",
            password="pass",
            mode="mock",
        )

        assert isinstance(client, CompassMockClient)
        assert client.base_url == "https://example.compass.education"

    def test_create_client_mode_case_insensitive(self):
        """Test that mode parameter is case-insensitive."""
        # Test uppercase
        client1 = create_client(
            base_url="https://example.compass.education",
            username="user",
            password="pass",
            mode="REAL",
        )
        assert isinstance(client1, CompassClient)

        # Test mixed case
        client2 = create_client(
            base_url="https://example.compass.education",
            username="user",
            password="pass",
            mode="Mock",
        )
        assert isinstance(client2, CompassMockClient)

    def test_create_client_invalid_mode(self):
        """Test that invalid mode raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            create_client(
                base_url="https://example.compass.education",
                username="user",
                password="pass",
                mode="invalid",
            )

        assert "must be 'real' or 'mock'" in str(exc_info.value).lower()

    @patch.dict(os.environ, {"COMPASS_MODE": "mock"})
    def test_create_client_from_env_variable(self):
        """Test that mode can be set via COMPASS_MODE environment variable."""
        client = create_client(
            base_url="https://example.compass.education",
            username="user",
            password="pass",
        )

        assert isinstance(client, CompassMockClient)

    @patch.dict(os.environ, {"COMPASS_MODE": "REAL"})
    def test_create_client_env_variable_case_insensitive(self):
        """Test that COMPASS_MODE env variable is case-insensitive."""
        client = create_client(
            base_url="https://example.compass.education",
            username="user",
            password="pass",
        )

        assert isinstance(client, CompassClient)

    @patch.dict(os.environ, {}, clear=True)
    def test_create_client_defaults_to_real(self):
        """Test that factory defaults to real client when no mode specified."""
        # Clear COMPASS_MODE if it exists
        os.environ.pop("COMPASS_MODE", None)

        client = create_client(
            base_url="https://example.compass.education",
            username="user",
            password="pass",
        )

        assert isinstance(client, CompassClient)
        assert not isinstance(client, CompassMockClient)

    @patch.dict(os.environ, {"COMPASS_MODE": "mock"})
    def test_create_client_explicit_mode_overrides_env(self):
        """Test that explicit mode parameter overrides environment variable."""
        # Env says mock, but we explicitly request real
        client = create_client(
            base_url="https://example.compass.education",
            username="user",
            password="pass",
            mode="real",
        )

        assert isinstance(client, CompassClient)
        assert not isinstance(client, CompassMockClient)

    def test_create_client_passes_credentials(self):
        """Test that factory passes credentials to client."""
        client = create_client(
            base_url="https://example.compass.education",
            username="testuser",
            password="testpass",
            mode="real",
        )

        assert client.base_url == "https://example.compass.education"
        assert client.username == "testuser"
        assert client.password == "testpass"

    def test_create_mock_client_with_custom_mock_dir(self, tmp_path):
        """Test creating mock client with custom mock data directory."""
        mock_dir = tmp_path / "custom_mock"
        mock_dir.mkdir()

        client = create_client(
            base_url="https://example.compass.education",
            username="user",
            password="pass",
            mode="mock",
            mock_data_dir=str(mock_dir),
        )

        assert isinstance(client, CompassMockClient)
        assert client.mock_data_dir == str(mock_dir)

    def test_create_real_client_ignores_mock_data_dir(self):
        """Test that mock_data_dir is ignored when creating real client."""
        # Should not raise error even though mock_data_dir is provided
        client = create_client(
            base_url="https://example.compass.education",
            username="user",
            password="pass",
            mode="real",
            mock_data_dir="/some/path",
        )

        assert isinstance(client, CompassClient)
        assert not isinstance(client, CompassMockClient)


class TestCreateClientEdgeCases:
    """Tests for edge cases in create_client()."""

    def test_create_client_with_empty_credentials(self):
        """Test creating client with empty credentials."""
        client = create_client(
            base_url="https://example.compass.education",
            username="",
            password="",
            mode="mock",
        )

        # Should create successfully (mock mode doesn't validate credentials)
        assert isinstance(client, CompassMockClient)

    def test_create_client_with_trailing_slash_in_url(self):
        """Test that factory handles trailing slash in base_url."""
        client = create_client(
            base_url="https://example.compass.education/",
            username="user",
            password="pass",
            mode="real",
        )

        # Client should strip trailing slash
        assert client.base_url == "https://example.compass.education"

    @patch.dict(os.environ, {"COMPASS_MODE": "invalid"})
    def test_create_client_invalid_env_variable(self):
        """Test that invalid COMPASS_MODE env variable raises error."""
        with pytest.raises(ValueError) as exc_info:
            create_client(
                base_url="https://example.compass.education",
                username="user",
                password="pass",
            )

        assert "must be 'real' or 'mock'" in str(exc_info.value).lower()

    @patch.dict(os.environ, {"COMPASS_MODE": ""})
    def test_create_client_empty_env_variable(self):
        """Test that empty COMPASS_MODE env variable defaults to real."""
        client = create_client(
            base_url="https://example.compass.education",
            username="user",
            password="pass",
        )

        # Empty env var should default to real
        assert isinstance(client, CompassClient)


class TestCreateClientInterfaceConsistency:
    """Tests that both client types have consistent interfaces."""

    def test_both_clients_have_login_method(self):
        """Test that both real and mock clients have login method."""
        real_client = create_client(
            base_url="https://example.compass.education",
            username="user",
            password="pass",
            mode="real",
        )

        mock_client = create_client(
            base_url="https://example.compass.education",
            username="user",
            password="pass",
            mode="mock",
        )

        assert hasattr(real_client, "login")
        assert callable(real_client.login)
        assert hasattr(mock_client, "login")
        assert callable(mock_client.login)

    def test_both_clients_have_get_user_details_method(self):
        """Test that both clients have get_user_details method."""
        real_client = create_client(
            base_url="https://example.compass.education",
            username="user",
            password="pass",
            mode="real",
        )

        mock_client = create_client(
            base_url="https://example.compass.education",
            username="user",
            password="pass",
            mode="mock",
        )

        assert hasattr(real_client, "get_user_details")
        assert callable(real_client.get_user_details)
        assert hasattr(mock_client, "get_user_details")
        assert callable(mock_client.get_user_details)

    def test_both_clients_have_get_calendar_events_method(self):
        """Test that both clients have get_calendar_events method."""
        real_client = create_client(
            base_url="https://example.compass.education",
            username="user",
            password="pass",
            mode="real",
        )

        mock_client = create_client(
            base_url="https://example.compass.education",
            username="user",
            password="pass",
            mode="mock",
        )

        assert hasattr(real_client, "get_calendar_events")
        assert callable(real_client.get_calendar_events)
        assert hasattr(mock_client, "get_calendar_events")
        assert callable(mock_client.get_calendar_events)
