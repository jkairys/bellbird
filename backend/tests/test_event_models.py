"""Tests for platform-agnostic Event models."""

from datetime import datetime, timezone

import pytest

from bellweaver.models.event import Event


class TestEventModel:
    """Test suite for Event Pydantic model."""

    def test_event_minimal_required_fields(self):
        """Test creating an Event with only required fields."""
        event = Event(
            title="Test Event",
            start=datetime(2025, 1, 15, 9, 0),
            end=datetime(2025, 1, 15, 10, 0),
        )

        assert event.title == "Test Event"
        assert event.start == datetime(2025, 1, 15, 9, 0)
        assert event.end == datetime(2025, 1, 15, 10, 0)
        assert event.description is None
        assert event.location is None
        assert event.all_day is False
        assert event.organizer is None
        assert event.attendees == []
        assert event.status is None
        assert isinstance(event.created_at, datetime)
        assert isinstance(event.updated_at, datetime)

    def test_event_all_fields(self):
        """Test creating an Event with all fields populated."""
        event = Event(
            title="School Assembly",
            start=datetime(2025, 1, 15, 9, 0),
            end=datetime(2025, 1, 15, 10, 0),
            description="Whole school assembly in the gym",
            location="Main Gymnasium",
            all_day=False,
            organizer="Principal Smith",
            attendees=["Year 1", "Year 2", "Year 3"],
            status="EventScheduled",
        )

        assert event.title == "School Assembly"
        assert event.start == datetime(2025, 1, 15, 9, 0)
        assert event.end == datetime(2025, 1, 15, 10, 0)
        assert event.description == "Whole school assembly in the gym"
        assert event.location == "Main Gymnasium"
        assert event.all_day is False
        assert event.organizer == "Principal Smith"
        assert event.attendees == ["Year 1", "Year 2", "Year 3"]
        assert event.status == "EventScheduled"

    def test_event_all_day_flag(self):
        """Test all_day flag behavior."""
        event = Event(
            title="Staff Development Day",
            start=datetime(2025, 1, 15, 0, 0),
            end=datetime(2025, 1, 15, 23, 59),
            all_day=True,
        )

        assert event.all_day is True

    def test_event_with_empty_attendees(self):
        """Test event with explicitly empty attendees list."""
        event = Event(
            title="Test Event",
            start=datetime(2025, 1, 15, 9, 0),
            end=datetime(2025, 1, 15, 10, 0),
            attendees=[],
        )

        assert event.attendees == []

    def test_event_status_values(self):
        """Test various event status values."""
        statuses = ["EventScheduled", "EventCancelled", "EventPostponed"]

        for status in statuses:
            event = Event(
                title="Test Event",
                start=datetime(2025, 1, 15, 9, 0),
                end=datetime(2025, 1, 15, 10, 0),
                status=status,
            )
            assert event.status == status

    def test_event_timestamps_auto_generated(self):
        """Test that created_at and updated_at are auto-generated."""
        event = Event(
            title="Test Event",
            start=datetime(2025, 1, 15, 9, 0),
            end=datetime(2025, 1, 15, 10, 0),
        )

        # Should be set to current time
        assert event.created_at is not None
        assert event.updated_at is not None
        assert isinstance(event.created_at, datetime)
        assert isinstance(event.updated_at, datetime)

        # Should be very recent (within last minute)
        now = datetime.now(timezone.utc)
        time_diff = (now - event.created_at).total_seconds()
        assert time_diff < 60

    def test_event_serialization(self):
        """Test that Event can be serialized to dict."""
        event = Event(
            title="Test Event",
            start=datetime(2025, 1, 15, 9, 0),
            end=datetime(2025, 1, 15, 10, 0),
            description="Test description",
            location="Test location",
        )

        event_dict = event.model_dump()

        assert event_dict["title"] == "Test Event"
        assert event_dict["start"] == datetime(2025, 1, 15, 9, 0)
        assert event_dict["end"] == datetime(2025, 1, 15, 10, 0)
        assert event_dict["description"] == "Test description"
        assert event_dict["location"] == "Test location"

    def test_event_json_serialization(self):
        """Test that Event can be serialized to JSON."""
        event = Event(
            title="Test Event",
            start=datetime(2025, 1, 15, 9, 0),
            end=datetime(2025, 1, 15, 10, 0),
        )

        json_str = event.model_dump_json()

        assert isinstance(json_str, str)
        assert "Test Event" in json_str
        assert "2025-01-15" in json_str
