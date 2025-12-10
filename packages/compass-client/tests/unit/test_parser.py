"""Unit tests for CompassParser."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from compass_client import CompassParser, CompassEvent, CompassUser
from compass_client.exceptions import CompassParseError


class TestCompassParserSingleItem:
    """Tests for parsing single items."""

    def test_parse_single_event_success(self, sample_compass_event):
        """Test parsing a single valid event."""
        result = CompassParser.parse(CompassEvent, sample_compass_event)

        assert isinstance(result, CompassEvent)
        assert result.title is not None
        assert isinstance(result.start, datetime)

    def test_parse_single_user_success(self, sample_compass_user):
        """Test parsing a single valid user."""
        result = CompassParser.parse(CompassUser, sample_compass_user)

        assert isinstance(result, CompassUser)
        assert result.user_id is not None
        assert result.user_first_name is not None

    def test_parse_single_with_alias_fields(self, sample_compass_user):
        """Test parsing with camelCase field names (aliases)."""
        # Mock data uses camelCase
        assert "userId" in sample_compass_user
        assert "userFirstName" in sample_compass_user

        result = CompassParser.parse(CompassUser, sample_compass_user)

        # Parsed model uses snake_case
        assert result.user_id is not None
        assert result.user_first_name is not None

    def test_parse_single_missing_required_field(self):
        """Test parsing with missing required field raises error."""
        raw_data = {
            # Missing many required fields
            "title": "Event"
        }

        with pytest.raises(CompassParseError) as exc_info:
            CompassParser.parse(CompassEvent, raw_data)

        assert "validation" in str(exc_info.value).lower()

    def test_parse_single_invalid_type(self, minimal_event_data):
        """Test parsing with invalid field type raises error."""
        minimal_event_data["allDay"] = "not_a_boolean"  # Should be boolean

        with pytest.raises(CompassParseError):
            CompassParser.parse(CompassEvent, minimal_event_data)


class TestCompassParserMultipleItems:
    """Tests for parsing multiple items."""

    def test_parse_multiple_events_success(self, sample_compass_events):
        """Test parsing a list of valid events."""
        # Use first 3 events from mock data
        raw_data = sample_compass_events[:3]

        result = CompassParser.parse(CompassEvent, raw_data)

        assert isinstance(result, list)
        assert len(result) == 3
        assert all(isinstance(item, CompassEvent) for item in result)

    def test_parse_empty_list(self):
        """Test parsing an empty list returns empty list."""
        raw_data = []

        result = CompassParser.parse(CompassEvent, raw_data)

        assert result == []

    def test_parse_list_with_one_invalid(self, sample_compass_event):
        """Test parsing list with one invalid item raises error by default."""
        raw_data = [
            sample_compass_event,  # Valid
            {"title": "Invalid"},  # Missing required fields
        ]

        with pytest.raises(CompassParseError) as exc_info:
            CompassParser.parse(CompassEvent, raw_data)

        error = exc_info.value
        assert error.validation_errors is not None
        assert len(error.validation_errors) > 0


class TestCompassParserSafeMode:
    """Tests for safe parsing mode."""

    def test_safe_parse_all_valid(self, sample_compass_events):
        """Test safe parsing with all valid items."""
        # Use first 3 events
        raw_data = sample_compass_events[:3]

        valid_items, errors = CompassParser.parse_safe(CompassEvent, raw_data)

        assert len(valid_items) == 3
        assert all(isinstance(item, CompassEvent) for item in valid_items)
        assert len(errors) == 0

    def test_safe_parse_with_invalid(self, sample_compass_event):
        """Test safe parsing skips invalid items and returns valid ones."""
        raw_data = [
            sample_compass_event,  # Valid
            {"title": "Invalid"},  # Missing required fields
            sample_compass_event,  # Valid
        ]

        valid_items, errors = CompassParser.parse_safe(CompassEvent, raw_data)

        # Should return only the 2 valid events
        assert len(valid_items) == 2
        assert all(isinstance(item, CompassEvent) for item in valid_items)
        assert len(errors) == 1

    def test_safe_parse_all_invalid(self):
        """Test safe parsing with all invalid items returns empty list."""
        raw_data = [
            {"start": "2025-12-01T09:00:00"},  # Missing many fields
            {"title": "Event"},  # Missing many fields
            {"invalid": "data"},  # Missing all required fields
        ]

        valid_items, errors = CompassParser.parse_safe(CompassEvent, raw_data)

        assert len(valid_items) == 0
        assert len(errors) == 3

    def test_safe_parse_single_item(self, sample_compass_event):
        """Test safe parsing with single item."""
        valid_items, errors = CompassParser.parse_safe(CompassEvent, [sample_compass_event])

        assert isinstance(valid_items, list)
        assert len(valid_items) == 1
        assert valid_items[0].title is not None
        assert len(errors) == 0


class TestCompassParserErrorHandling:
    """Tests for error handling and error objects."""

    def test_parse_error_contains_message(self):
        """Test that parse error contains a message."""
        raw_data = {"invalid": "data"}

        try:
            CompassParser.parse(CompassEvent, raw_data)
        except CompassParseError as e:
            error_msg = str(e)
            assert len(error_msg) > 0
            assert "validation" in error_msg.lower() or "failed" in error_msg.lower()

    def test_parse_error_contains_raw_data(self):
        """Test that parse error contains the raw data."""
        raw_data = {"invalid": "data"}

        try:
            CompassParser.parse(CompassEvent, raw_data)
        except CompassParseError as e:
            assert e.raw_data == raw_data

    def test_parse_error_contains_validation_errors(self):
        """Test that parse error contains validation errors."""
        raw_data = [
            {"invalid": "data"},
            {"also": "invalid"},
        ]

        try:
            CompassParser.parse(CompassEvent, raw_data)
        except CompassParseError as e:
            assert e.validation_errors is not None
            assert len(e.validation_errors) > 0

    def test_parse_error_string_representation(self):
        """Test string representation of parse error."""
        raw_data = {"invalid": "data"}

        try:
            CompassParser.parse(CompassEvent, raw_data)
        except CompassParseError as e:
            error_str = str(e)
            assert len(error_str) > 0
            assert "CompassEvent" in error_str


class TestCompassParserEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_parse_with_none_value(self):
        """Test parsing None raises appropriate error."""
        with pytest.raises(CompassParseError):
            CompassParser.parse(CompassEvent, None)

    def test_parse_with_extra_fields(self, sample_compass_event):
        """Test parsing with extra fields (should ignore extra fields)."""
        # Add some extra fields
        sample_compass_event["extraField1"] = "ignored"
        sample_compass_event["extraField2"] = 123

        # Should parse successfully, ignoring extra fields
        result = CompassParser.parse(CompassEvent, sample_compass_event)

        assert result.title is not None

    def test_parse_datetime_formats(self, minimal_event_data):
        """Test parsing datetime in various formats."""
        # ISO format without timezone
        result = CompassParser.parse(CompassEvent, minimal_event_data)

        assert isinstance(result.start, datetime)
        assert result.start.year == 2025
        assert result.start.month == 12
        assert result.start.day == 1

    def test_parse_large_list(self, sample_compass_events):
        """Test parsing a large list of events."""
        # Use all events from mock data
        valid_items, errors = CompassParser.parse_safe(CompassEvent, sample_compass_events)

        assert len(valid_items) > 0
        assert all(isinstance(event, CompassEvent) for event in valid_items)
