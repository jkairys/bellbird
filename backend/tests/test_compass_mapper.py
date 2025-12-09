"""Tests for Compass to Event mapper."""

from datetime import datetime

import pytest

from compass import CalendarEventLocation, CompassEvent
from bellweaver.mappers.compass import compass_event_to_event
from bellweaver.models.event import Event


class TestCompassEventMapper:
    """Test suite for compass_event_to_event mapper."""

    def test_mapper_minimal_fields(self):
        """Test mapping with minimal required fields."""
        compass_event = CompassEvent(
            activity_id=12345,
            activity_type=1,
            all_day=False,
            attendance_mode=1,
            attendee_user_id=100,
            background_color="#ffffff",
            calendar_id=1,
            description="Test event",
            finish=datetime(2025, 1, 15, 10, 0),
            guid="test-guid-123",
            instance_id="instance-123",
            is_recurring=False,
            lesson_plan_configured=False,
            long_title="10:00: Test Event",
            long_title_without_time="Test Event",
            manager_id=200,
            repeat_forever=False,
            repeat_frequency=0,
            roll_marked=False,
            running_status=0,
            start=datetime(2025, 1, 15, 9, 0),
            target_student_id=100,
            teaching_days_only=False,
            title="Test Event",
        )

        event = compass_event_to_event(compass_event)

        assert isinstance(event, Event)
        assert event.title == "Test Event"
        assert event.start == datetime(2025, 1, 15, 9, 0)
        assert event.end == datetime(2025, 1, 15, 10, 0)
        assert event.description == "Test event"
        assert event.all_day is False
        assert event.status == "EventScheduled"

    def test_mapper_with_location_string(self):
        """Test mapping when Compass event has location as string."""
        compass_event = CompassEvent(
            activity_id=12345,
            activity_type=1,
            all_day=False,
            attendance_mode=1,
            attendee_user_id=100,
            background_color="#ffffff",
            calendar_id=1,
            description="Test event",
            finish=datetime(2025, 1, 15, 10, 0),
            guid="test-guid-123",
            instance_id="instance-123",
            is_recurring=False,
            lesson_plan_configured=False,
            location="Classroom 1A",
            long_title="10:00: Test Event",
            long_title_without_time="Test Event",
            manager_id=200,
            repeat_forever=False,
            repeat_frequency=0,
            roll_marked=False,
            running_status=0,
            start=datetime(2025, 1, 15, 9, 0),
            target_student_id=100,
            teaching_days_only=False,
            title="Test Event",
        )

        event = compass_event_to_event(compass_event)

        assert event.location == "Classroom 1A"

    def test_mapper_with_locations_array(self):
        """Test mapping when Compass event has locations array."""
        compass_event = CompassEvent(
            activity_id=12345,
            activity_type=1,
            all_day=False,
            attendance_mode=1,
            attendee_user_id=100,
            background_color="#ffffff",
            calendar_id=1,
            description="Test event",
            finish=datetime(2025, 1, 15, 10, 0),
            guid="test-guid-123",
            instance_id="instance-123",
            is_recurring=False,
            lesson_plan_configured=False,
            locations=[
                CalendarEventLocation(
                    location_id=1,
                    location_name="Main Gymnasium",
                )
            ],
            long_title="10:00: Test Event",
            long_title_without_time="Test Event",
            manager_id=200,
            repeat_forever=False,
            repeat_frequency=0,
            roll_marked=False,
            running_status=0,
            start=datetime(2025, 1, 15, 9, 0),
            target_student_id=100,
            teaching_days_only=False,
            title="Test Event",
        )

        event = compass_event_to_event(compass_event)

        assert event.location == "Main Gymnasium"

    def test_mapper_location_string_takes_precedence(self):
        """Test that location string takes precedence over locations array."""
        compass_event = CompassEvent(
            activity_id=12345,
            activity_type=1,
            all_day=False,
            attendance_mode=1,
            attendee_user_id=100,
            background_color="#ffffff",
            calendar_id=1,
            description="Test event",
            finish=datetime(2025, 1, 15, 10, 0),
            guid="test-guid-123",
            instance_id="instance-123",
            is_recurring=False,
            lesson_plan_configured=False,
            location="Primary Location",
            locations=[
                CalendarEventLocation(
                    location_id=1,
                    location_name="Secondary Location",
                )
            ],
            long_title="10:00: Test Event",
            long_title_without_time="Test Event",
            manager_id=200,
            repeat_forever=False,
            repeat_frequency=0,
            roll_marked=False,
            running_status=0,
            start=datetime(2025, 1, 15, 9, 0),
            target_student_id=100,
            teaching_days_only=False,
            title="Test Event",
        )

        event = compass_event_to_event(compass_event)

        assert event.location == "Primary Location"

    def test_mapper_all_day_event(self):
        """Test mapping for all-day events."""
        compass_event = CompassEvent(
            activity_id=12345,
            activity_type=1,
            all_day=True,
            attendance_mode=1,
            attendee_user_id=100,
            background_color="#ffffff",
            calendar_id=1,
            description="Staff Development Day",
            finish=datetime(2025, 1, 15, 23, 59),
            guid="test-guid-123",
            instance_id="instance-123",
            is_recurring=False,
            lesson_plan_configured=False,
            long_title="Staff Development Day",
            long_title_without_time="Staff Development Day",
            manager_id=200,
            repeat_forever=False,
            repeat_frequency=0,
            roll_marked=False,
            running_status=0,
            start=datetime(2025, 1, 15, 0, 0),
            target_student_id=100,
            teaching_days_only=False,
            title="Staff Development Day",
        )

        event = compass_event_to_event(compass_event)

        assert event.all_day is True

    def test_mapper_status_mapping(self):
        """Test mapping of running_status to event status."""
        test_cases = [
            (0, "EventScheduled"),
            (1, "EventCancelled"),
            (2, "EventPostponed"),
            (999, None),  # Unknown status should return None
        ]

        for running_status, expected_status in test_cases:
            compass_event = CompassEvent(
                activity_id=12345,
                activity_type=1,
                all_day=False,
                attendance_mode=1,
                attendee_user_id=100,
                background_color="#ffffff",
                calendar_id=1,
                description="Test event",
                finish=datetime(2025, 1, 15, 10, 0),
                guid="test-guid-123",
                instance_id="instance-123",
                is_recurring=False,
                lesson_plan_configured=False,
                long_title="10:00: Test Event",
                long_title_without_time="Test Event",
                manager_id=200,
                repeat_forever=False,
                repeat_frequency=0,
                roll_marked=False,
                running_status=running_status,
                start=datetime(2025, 1, 15, 9, 0),
                target_student_id=100,
                teaching_days_only=False,
                title="Test Event",
            )

            event = compass_event_to_event(compass_event)

            assert event.status == expected_status

    def test_mapper_preserves_timestamps(self):
        """Test that mapper correctly handles start/finish timestamps."""
        start_time = datetime(2025, 11, 23, 22, 0)  # From fixture
        end_time = datetime(2025, 11, 24, 2, 40)  # From fixture

        compass_event = CompassEvent(
            activity_id=12441,
            activity_type=1,
            all_day=False,
            attendance_mode=1,
            attendee_user_id=4164,
            background_color="#dce6f4",
            calendar_id=-4164,
            description="",
            finish=end_time,
            guid="c4997880-4dcc-4ea4-9a0e-7cb27e9eaf6b",
            instance_id="12441231120252200",
            is_recurring=False,
            lesson_plan_configured=False,
            long_title="10:00: Year 1 Generalist",
            long_title_without_time="Year 1 Generalist",
            manager_id=4424,
            repeat_forever=False,
            repeat_frequency=0,
            roll_marked=True,
            running_status=1,
            start=start_time,
            target_student_id=4164,
            teaching_days_only=False,
            title="Year 1 Class",
        )

        event = compass_event_to_event(compass_event)

        assert event.start == start_time
        assert event.end == end_time

    def test_mapper_empty_description(self):
        """Test mapping when description is empty string."""
        compass_event = CompassEvent(
            activity_id=12345,
            activity_type=1,
            all_day=False,
            attendance_mode=1,
            attendee_user_id=100,
            background_color="#ffffff",
            calendar_id=1,
            description="",
            finish=datetime(2025, 1, 15, 10, 0),
            guid="test-guid-123",
            instance_id="instance-123",
            is_recurring=False,
            lesson_plan_configured=False,
            long_title="10:00: Test Event",
            long_title_without_time="Test Event",
            manager_id=200,
            repeat_forever=False,
            repeat_frequency=0,
            roll_marked=False,
            running_status=0,
            start=datetime(2025, 1, 15, 9, 0),
            target_student_id=100,
            teaching_days_only=False,
            title="Test Event",
        )

        event = compass_event_to_event(compass_event)

        # Empty string should be preserved (not converted to None)
        assert event.description == ""
