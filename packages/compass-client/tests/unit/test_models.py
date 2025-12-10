"""Unit tests for Compass Pydantic models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from compass_client import CompassEvent, CompassUser


class TestCompassEventModel:
    """Tests for CompassEvent Pydantic model."""

    def test_create_event_from_mock_data(self, sample_compass_event):
        """Test creating event from real mock data."""
        event = CompassEvent(**sample_compass_event)

        assert event.title is not None
        assert isinstance(event.start, datetime)
        assert isinstance(event.finish, datetime)
        assert isinstance(event.all_day, bool)

    def test_create_event_with_minimal_fields(self, minimal_event_data):
        """Test creating event with minimal required fields."""
        event = CompassEvent(**minimal_event_data)

        assert event.title == "Test Event"
        assert isinstance(event.start, datetime)
        assert event.all_day is False

    def test_event_missing_required_field(self):
        """Test that creating event without required field raises error."""
        with pytest.raises(ValidationError) as exc_info:
            CompassEvent(
                # Missing many required fields
                title="Test Event",
            )

        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_event_invalid_field_type(self, minimal_event_data):
        """Test that invalid field type raises error."""
        minimal_event_data["allDay"] = "not_a_boolean"

        with pytest.raises(ValidationError):
            CompassEvent(**minimal_event_data)

    def test_event_datetime_parsing(self, minimal_event_data):
        """Test that datetime strings are parsed correctly."""
        event = CompassEvent(**minimal_event_data)

        assert isinstance(event.start, datetime)
        assert event.start.year == 2025
        assert event.start.month == 12

    def test_event_field_aliases(self, sample_compass_event):
        """Test that field aliases work correctly."""
        # Mock data uses camelCase
        assert "allDay" in sample_compass_event
        assert "activityId" in sample_compass_event

        event = CompassEvent(**sample_compass_event)

        # Model uses snake_case
        assert hasattr(event, "all_day")
        assert hasattr(event, "activity_id")

    def test_event_optional_fields(self, minimal_event_data):
        """Test that optional fields can be None."""
        event = CompassEvent(**minimal_event_data)

        # These are optional in the model
        assert event.location is None or isinstance(event.location, str)
        assert event.comment is None or isinstance(event.comment, str)

    def test_event_serialization(self, sample_compass_event):
        """Test that event can be serialized to dict."""
        event = CompassEvent(**sample_compass_event)

        event_dict = event.model_dump()

        assert isinstance(event_dict, dict)
        assert "title" in event_dict
        assert "start" in event_dict

    def test_event_json_serialization(self, sample_compass_event):
        """Test that event can be serialized to JSON."""
        event = CompassEvent(**sample_compass_event)

        event_json = event.model_dump_json()

        assert isinstance(event_json, str)
        assert len(event_json) > 0


class TestCompassUserModel:
    """Tests for CompassUser Pydantic model."""

    def test_create_user_from_mock_data(self, sample_compass_user):
        """Test creating user from real mock data."""
        user = CompassUser(**sample_compass_user)

        assert user.user_id is not None
        assert user.user_first_name is not None
        assert user.user_last_name is not None

    def test_user_missing_required_field(self):
        """Test that creating user without required field raises error."""
        with pytest.raises(ValidationError) as exc_info:
            CompassUser(
                # Missing many required fields
                user_id=12345,
            )

        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_user_invalid_field_type(self):
        """Test that invalid field type raises error."""
        with pytest.raises(ValidationError):
            CompassUser(
                user_id="not_an_int",  # Should be int
                user_first_name="Test",
            )

    def test_user_field_aliases(self, sample_compass_user):
        """Test that field aliases work correctly."""
        # Mock data uses camelCase
        assert "userId" in sample_compass_user
        assert "userFirstName" in sample_compass_user

        user = CompassUser(**sample_compass_user)

        # Model uses snake_case
        assert hasattr(user, "user_id")
        assert hasattr(user, "user_first_name")

    def test_user_optional_fields(self, sample_compass_user):
        """Test that optional fields are handled correctly."""
        user = CompassUser(**sample_compass_user)

        # These fields may or may not be present
        assert hasattr(user, "age")
        assert hasattr(user, "birthday")

    def test_user_serialization(self, sample_compass_user):
        """Test that user can be serialized to dict."""
        user = CompassUser(**sample_compass_user)

        user_dict = user.model_dump()

        assert isinstance(user_dict, dict)
        assert "user_id" in user_dict
        assert "user_first_name" in user_dict

    def test_user_json_serialization(self, sample_compass_user):
        """Test that user can be serialized to JSON."""
        user = CompassUser(**sample_compass_user)

        user_json = user.model_dump_json()

        assert isinstance(user_json, str)
        assert str(user.user_id) in user_json


class TestModelsIntegration:
    """Integration tests for models working together."""

    def test_event_with_locations(self, sample_compass_event):
        """Test creating event with location data."""
        event = CompassEvent(**sample_compass_event)

        if event.locations:
            assert isinstance(event.locations, list)
            assert len(event.locations) > 0

    def test_event_with_managers(self, sample_compass_event):
        """Test creating event with manager data."""
        event = CompassEvent(**sample_compass_event)

        if event.managers:
            assert isinstance(event.managers, list)
            assert len(event.managers) > 0

    def test_models_are_mutable(self, minimal_event_data):
        """Test that models can be modified after creation (Pydantic v2 default)."""
        event = CompassEvent(**minimal_event_data)
        original_title = event.title

        # Pydantic v2 models are mutable by default
        event.title = "Modified Title"
        assert event.title == "Modified Title"
        assert event.title != original_title

    def test_multiple_events_from_mock_data(self, sample_compass_events):
        """Test parsing multiple events from mock data."""
        events = [CompassEvent(**event_data) for event_data in sample_compass_events[:5]]

        assert len(events) == 5
        assert all(isinstance(event, CompassEvent) for event in events)
        assert all(event.title is not None for event in events)
