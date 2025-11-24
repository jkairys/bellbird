"""
Test that fixtures load correctly and have expected structure.
"""

import pytest
from tests.fixtures import load_compass_sample_events, get_fixtures_dir


def test_load_compass_sample_events():
    """Test that sample events load and have correct structure."""
    events = load_compass_sample_events()

    # Verify we have events
    assert isinstance(events, list)
    assert len(events) > 0

    # Verify first event has required fields
    first_event = events[0]
    assert '__type' in first_event
    assert 'activityId' in first_event
    assert 'longTitle' in first_event
    assert 'longTitleWithoutTime' in first_event
    assert 'start' in first_event
    assert 'finish' in first_event
    assert 'allDay' in first_event
    assert 'description' in first_event
    assert 'locations' in first_event
    assert 'managers' in first_event


def test_compass_sample_events_variety():
    """Test that sample events include variety for testing."""
    events = load_compass_sample_events()

    # Should have both all-day and timed events
    all_day_events = [e for e in events if e['allDay']]
    timed_events = [e for e in events if not e['allDay']]

    assert len(all_day_events) > 0, "Should have all-day events"
    assert len(timed_events) > 0, "Should have timed events"

    # Should have events with descriptions
    events_with_descriptions = [e for e in events if e.get('description')]
    assert len(events_with_descriptions) > 0, "Should have events with descriptions"

    # Should have events with locations
    events_with_locations = [e for e in events if e.get('locations')]
    assert len(events_with_locations) > 0, "Should have events with locations"


def test_fixtures_dir():
    """Test that fixtures directory path is accessible."""
    fixtures_dir = get_fixtures_dir()
    assert fixtures_dir.exists()
    assert fixtures_dir.is_dir()
    assert (fixtures_dir / 'compass_sample_response.json').exists()
