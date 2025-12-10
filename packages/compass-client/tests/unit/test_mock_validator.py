"""
Unit tests for mock data validation.
"""

import json
import tempfile
from pathlib import Path

import pytest

from compass_client.mock_validator import (
    MockDataValidationError,
    load_and_validate_mock_data,
    validate_mock_data_schema,
)


class TestMockValidatorMissingFiles:
    """Test validation when files are missing."""

    def test_missing_directory_raises_error(self):
        """Test that missing mock data directory raises error."""
        with pytest.raises(MockDataValidationError, match="does not exist"):
            validate_mock_data_schema(Path("/nonexistent/path"))

    def test_missing_events_file_raises_error(self):
        """Test that missing compass_events.json raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create user and version files
            (tmpdir / "compass_user.json").write_text(
                '{"userId": 1, "userFirstName": "Test", "userLastName": "User"}'
            )
            (tmpdir / "schema_version.json").write_text('{"version": "1.0", "api_version": "1.0"}')

            with pytest.raises(MockDataValidationError, match="compass_events.json"):
                validate_mock_data_schema(tmpdir)

    def test_missing_user_file_raises_error(self):
        """Test that missing compass_user.json raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create events and version files
            (tmpdir / "compass_events.json").write_text("[]")
            (tmpdir / "schema_version.json").write_text('{"version": "1.0", "api_version": "1.0"}')

            with pytest.raises(MockDataValidationError, match="compass_user.json"):
                validate_mock_data_schema(tmpdir)

    def test_missing_version_file_raises_error(self):
        """Test that missing schema_version.json raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create events and user files
            (tmpdir / "compass_events.json").write_text("[]")
            (tmpdir / "compass_user.json").write_text(
                '{"userId": 1, "userFirstName": "Test", "userLastName": "User"}'
            )

            with pytest.raises(MockDataValidationError, match="schema_version.json"):
                validate_mock_data_schema(tmpdir)


class TestMockValidatorInvalidJSON:
    """Test validation when JSON files are invalid."""

    def test_invalid_events_json_raises_error(self):
        """Test that invalid JSON in compass_events.json raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            (tmpdir / "compass_events.json").write_text("not valid json{")
            (tmpdir / "compass_user.json").write_text(
                '{"userId": 1, "userFirstName": "Test", "userLastName": "User"}'
            )
            (tmpdir / "schema_version.json").write_text('{"version": "1.0", "api_version": "1.0"}')

            with pytest.raises(MockDataValidationError, match="Invalid JSON"):
                validate_mock_data_schema(tmpdir)

    def test_invalid_user_json_raises_error(self):
        """Test that invalid JSON in compass_user.json raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            (tmpdir / "compass_events.json").write_text("[]")
            (tmpdir / "compass_user.json").write_text("not valid json{")
            (tmpdir / "schema_version.json").write_text('{"version": "1.0", "api_version": "1.0"}')

            with pytest.raises(MockDataValidationError, match="Invalid JSON"):
                validate_mock_data_schema(tmpdir)


class TestMockValidatorWrongDataTypes:
    """Test validation when data types are wrong."""

    def test_events_is_dict_not_array(self):
        """Test that compass_events.json must be an array."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            (tmpdir / "compass_events.json").write_text('{"not": "array"}')
            (tmpdir / "compass_user.json").write_text(
                '{"userId": 1, "userFirstName": "Test", "userLastName": "User"}'
            )
            (tmpdir / "schema_version.json").write_text('{"version": "1.0", "api_version": "1.0"}')

            with pytest.raises(MockDataValidationError, match="must contain a JSON array"):
                validate_mock_data_schema(tmpdir)

    def test_user_is_array_not_object(self):
        """Test that compass_user.json must be an object."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            (tmpdir / "compass_events.json").write_text("[]")
            (tmpdir / "compass_user.json").write_text("[1, 2, 3]")
            (tmpdir / "schema_version.json").write_text('{"version": "1.0", "api_version": "1.0"}')

            with pytest.raises(MockDataValidationError, match="must contain a JSON object"):
                validate_mock_data_schema(tmpdir)

    def test_version_is_array_not_object(self):
        """Test that schema_version.json must be an object."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            (tmpdir / "compass_events.json").write_text("[]")
            (tmpdir / "compass_user.json").write_text(
                '{"userId": 1, "userFirstName": "Test", "userLastName": "User"}'
            )
            (tmpdir / "schema_version.json").write_text("[1, 2, 3]")

            with pytest.raises(MockDataValidationError, match="must contain a JSON object"):
                validate_mock_data_schema(tmpdir)


class TestMockValidatorMissingRequiredFields:
    """Test validation of required fields in objects."""

    def test_user_missing_userId(self):
        """Test that compass_user.json requires userId."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            (tmpdir / "compass_events.json").write_text("[]")
            (tmpdir / "compass_user.json").write_text(
                '{"userFirstName": "Test", "userLastName": "User"}'
            )
            (tmpdir / "schema_version.json").write_text('{"version": "1.0", "api_version": "1.0"}')

            with pytest.raises(MockDataValidationError, match="missing required fields"):
                validate_mock_data_schema(tmpdir)

    def test_event_missing_start(self):
        """Test that events require start field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            event = {"finish": "2025-12-15T09:00:00", "title": "Test"}
            (tmpdir / "compass_events.json").write_text(json.dumps([event]))
            (tmpdir / "compass_user.json").write_text(
                '{"userId": 1, "userFirstName": "Test", "userLastName": "User"}'
            )
            (tmpdir / "schema_version.json").write_text('{"version": "1.0", "api_version": "1.0"}')

            with pytest.raises(MockDataValidationError, match="missing required fields"):
                validate_mock_data_schema(tmpdir)


class TestMockValidatorSuccess:
    """Test successful validation."""

    def test_valid_mock_data_passes(self):
        """Test that valid mock data passes validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            events = [
                {
                    "start": "2025-12-15T09:00:00",
                    "finish": "2025-12-15T10:00:00",
                    "title": "Test Event",
                }
            ]
            user = {"userId": 123, "userFirstName": "John", "userLastName": "Doe"}
            version = {"version": "1.0", "api_version": "1.0"}

            (tmpdir / "compass_events.json").write_text(json.dumps(events))
            (tmpdir / "compass_user.json").write_text(json.dumps(user))
            (tmpdir / "schema_version.json").write_text(json.dumps(version))

            # Should not raise
            result = validate_mock_data_schema(tmpdir)
            assert result is True

    def test_load_and_validate_returns_data(self):
        """Test that load_and_validate_mock_data returns the loaded data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            events = [
                {
                    "start": "2025-12-15T09:00:00",
                    "finish": "2025-12-15T10:00:00",
                    "title": "Test Event",
                }
            ]
            user = {"userId": 123, "userFirstName": "John", "userLastName": "Doe"}
            version = {"version": "1.0", "api_version": "1.0"}

            (tmpdir / "compass_events.json").write_text(json.dumps(events))
            (tmpdir / "compass_user.json").write_text(json.dumps(user))
            (tmpdir / "schema_version.json").write_text(json.dumps(version))

            data = load_and_validate_mock_data(tmpdir)

            assert data["events"] == events
            assert data["user"] == user
            assert data["schema_version"] == version

    def test_default_mock_data_dir(self):
        """Test that default mock data directory (from package) loads successfully."""
        # This test verifies that the committed mock data is valid
        data = load_and_validate_mock_data()
        assert "events" in data
        assert "user" in data
        assert "schema_version" in data
        assert isinstance(data["events"], list)
        assert isinstance(data["user"], dict)
        assert isinstance(data["schema_version"], dict)
