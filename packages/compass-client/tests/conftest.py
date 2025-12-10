"""Shared pytest fixtures for compass-client tests."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def mock_data_dir():
    """Return path to mock data directory."""
    return Path(__file__).parent.parent / "data" / "mock"


@pytest.fixture
def sample_compass_event(mock_data_dir):
    """Load a single sample compass event from mock data."""
    events_file = mock_data_dir / "compass_events.json"
    with open(events_file) as f:
        events = json.load(f)
    # Return first event
    return events[0] if events else None


@pytest.fixture
def sample_compass_events(mock_data_dir):
    """Load all sample compass events from mock data."""
    events_file = mock_data_dir / "compass_events.json"
    with open(events_file) as f:
        return json.load(f)


@pytest.fixture
def sample_compass_user(mock_data_dir):
    """Load sample compass user from mock data."""
    user_file = mock_data_dir / "compass_user.json"
    with open(user_file) as f:
        return json.load(f)


@pytest.fixture
def minimal_event_data():
    """Minimal event data for testing edge cases."""
    return {
        "__type": "CalendarTransport:http://jdlf.com.au/ns/data/calendar",
        "activityId": 123,
        "activityType": 1,
        "allDay": False,
        "attendanceMode": 0,
        "attendeeUserId": 456,
        "backgroundColor": "#FF0000",
        "calendarId": 789,
        "description": "Test event",
        "finish": "2025-12-01T10:00:00",
        "guid": "test-guid",
        "instanceId": "test-instance",
        "isRecurring": False,
        "lessonPlanConfigured": False,
        "longTitle": "Test Event - 09:00",
        "longTitleWithoutTime": "Test Event",
        "managerId": 999,
        "repeatForever": False,
        "repeatFrequency": 0,
        "rollMarked": False,
        "runningStatus": 0,
        "start": "2025-12-01T09:00:00",
        "targetStudentId": 456,
        "teachingDaysOnly": False,
        "title": "Test Event",
    }
