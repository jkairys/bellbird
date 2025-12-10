"""Tests for Compass Pydantic models."""

import json
from pathlib import Path

import pytest

from compass_client import CompassEvent, CompassUser


@pytest.fixture
def mock_data_dir():
    """Return path to mock data directory."""
    return Path(__file__).parent.parent / "data" / "mock"


@pytest.fixture
def compass_events_data(mock_data_dir):
    """Load compass events mock data."""
    events_file = mock_data_dir / "compass_events.json"
    with open(events_file) as f:
        return json.load(f)


@pytest.fixture
def compass_user_data(mock_data_dir):
    """Load compass user mock data."""
    user_file = mock_data_dir / "compass_user.json"
    with open(user_file) as f:
        return json.load(f)


def test_compass_event_model_parses_mock_data(compass_events_data):
    """Test that CompassEvent model can parse all mock event data."""
    events = [CompassEvent(**event_data) for event_data in compass_events_data]

    assert len(events) > 0

    # Check first event has expected fields
    first_event = events[0]
    assert first_event.activity_id == 12441
    assert first_event.title == "01GEN_1A"
    assert first_event.subject_long_name == "Yr 1 Generalist"
    assert first_event.all_day is False


def test_compass_event_model_with_locations(compass_events_data):
    """Test that CompassEvent handles location data correctly."""
    # Find an event with locations
    event_with_locations = next(
        e for e in compass_events_data if e.get("locations") is not None
    )

    event = CompassEvent(**event_with_locations)

    assert event.locations is not None
    assert len(event.locations) > 0
    assert event.locations[0].location_id == 1


def test_compass_event_model_with_managers(compass_events_data):
    """Test that CompassEvent handles manager data correctly."""
    # Find an event with managers
    event_with_managers = next(
        e for e in compass_events_data if e.get("managers") is not None
    )

    event = CompassEvent(**event_with_managers)

    assert event.managers is not None
    assert len(event.managers) > 0
    assert event.managers[0].manager_import_identifier == "RD01"


def test_compass_event_all_day_event(compass_events_data):
    """Test parsing of all-day events."""
    # Find an all-day event
    all_day_event = next(e for e in compass_events_data if e.get("allDay") is True)

    event = CompassEvent(**all_day_event)

    assert event.all_day is True
    assert event.title == "Rolling Power Outages All Week!"


def test_compass_user_model_parses_mock_data(compass_user_data):
    """Test that CompassUser model can parse mock user data."""
    user = CompassUser(**compass_user_data)

    assert user.user_id == 4180
    assert user.user_first_name == "Bethany"
    assert user.user_last_name == "KAIRYS"
    assert user.user_email == "bethany.kairys@gmail.com"
    assert user.user_display_code == "KAI0002"
    assert user.user_school_url == "seaford-northps-vic.compass.education"


def test_compass_user_optional_fields(compass_user_data):
    """Test that CompassUser handles optional fields correctly."""
    user = CompassUser(**compass_user_data)

    # These should be None in the test data
    assert user.age is None
    assert user.birthday is None
    assert user.gender is None
    assert user.user_year_level is None


def test_compass_event_field_aliases(compass_events_data):
    """Test that field aliases work correctly."""
    event_data = compass_events_data[0]
    event = CompassEvent(**event_data)

    # Test that we can access fields by both the alias and the Python name
    assert event.activity_id == event_data["activityId"]
    assert event.long_title == event_data["longTitle"]
    assert event.target_student_id == event_data["targetStudentId"]


def test_compass_user_field_aliases(compass_user_data):
    """Test that field aliases work correctly for user."""
    user = CompassUser(**compass_user_data)

    # Test that we can access fields by both the alias and the Python name
    assert user.user_id == compass_user_data["userId"]
    assert user.user_email == compass_user_data["userEmail"]
    assert user.user_school_url == compass_user_data["userSchoolURL"]
