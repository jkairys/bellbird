"""Tests for the compass process command."""

import json
from datetime import datetime, timezone

import pytest
from typer.testing import CliRunner

from bellweaver.cli.main import app
from bellweaver.db.database import SessionLocal, init_db
from bellweaver.db.models import ApiPayload, Batch, Event


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


@pytest.fixture
def db_session():
    """Create a database session for testing."""
    init_db()
    session = SessionLocal()

    # Clean up all data before each test
    session.query(Event).delete()
    session.query(ApiPayload).delete()
    session.query(Batch).delete()
    session.commit()

    yield session

    # Clean up after test
    session.query(Event).delete()
    session.query(ApiPayload).delete()
    session.query(Batch).delete()
    session.commit()
    session.close()


@pytest.fixture
def sample_compass_event_payload():
    """Sample Compass event payload."""
    return {
        "__type": "CalendarTransport:http://jdlf.com.au/ns/data/calendar",
        "activityId": 123,
        "activityType": 1,
        "allDay": False,
        "attendanceMode": 0,
        "attendeeUserId": 456,
        "backgroundColor": "#FF0000",
        "calendarId": 789,
        "description": "Test event description",
        "finish": "2025-12-03T15:00:00",
        "guid": "test-guid-123",
        "instanceId": "test-instance-123",
        "isRecurring": False,
        "lessonPlanConfigured": False,
        "longTitle": "Test Event - 14:00 to 15:00",
        "longTitleWithoutTime": "Test Event",
        "managerId": 999,
        "repeatForever": False,
        "repeatFrequency": 0,
        "rollMarked": False,
        "runningStatus": 0,
        "start": "2025-12-03T14:00:00",
        "targetStudentId": 456,
        "teachingDaysOnly": False,
        "title": "Test Event",
    }


@pytest.fixture
def batch_with_events(db_session, sample_compass_event_payload):
    """Create a batch with event payloads."""
    # Create batch
    batch = Batch(
        adapter_id="compass",
        method_name="get_calendar_events",
        parameters={"start_date": "2025-12-01", "end_date": "2025-12-31"},
    )
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)

    # Create payloads
    payload1 = ApiPayload(
        adapter_id="compass",
        method_name="get_calendar_events",
        batch_id=batch.id,
        payload=sample_compass_event_payload,
    )
    db_session.add(payload1)

    # Create second payload with different data
    payload2_data = sample_compass_event_payload.copy()
    payload2_data["title"] = "Second Test Event"
    payload2_data["guid"] = "test-guid-456"
    payload2 = ApiPayload(
        adapter_id="compass",
        method_name="get_calendar_events",
        batch_id=batch.id,
        payload=payload2_data,
    )
    db_session.add(payload2)

    db_session.commit()

    return batch


class TestProcessCommand:
    """Tests for the compass process command."""

    def test_process_command_exists(self, runner):
        """Test that the process command exists."""
        result = runner.invoke(app, ["compass", "--help"])
        assert result.exit_code == 0
        assert "process" in result.stdout

    def test_process_command_no_batches(self, runner, db_session):
        """Test process command when no batches exist."""
        # Ensure no batches exist (fixture already cleaned, but be explicit)
        db_session.query(Batch).delete()
        db_session.commit()

        result = runner.invoke(app, ["compass", "process"])
        assert result.exit_code == 1
        # Error message goes to stdout (typer.secho prints to stdout)
        assert "No batches found" in result.stdout or "No batches found" in result.stderr

    def test_process_command_creates_events(self, runner, db_session, batch_with_events):
        """Test that process command creates Event records."""
        # Verify no events exist before processing
        event_count_before = db_session.query(Event).count()
        assert event_count_before == 0

        # Run process command
        result = runner.invoke(app, ["compass", "process"])
        assert result.exit_code == 0
        assert "Success" in result.stdout

        # Verify events were created
        db_session.expire_all()
        event_count_after = db_session.query(Event).count()
        assert event_count_after == 2

        # Verify event data
        event = db_session.query(Event).first()
        assert event.title in ["Test Event", "Second Test Event"]
        assert event.description == "Test event description"
        assert event.all_day is False

    def test_process_command_updates_existing_events(
        self, runner, db_session, batch_with_events
    ):
        """Test that reprocessing updates existing events."""
        # First processing
        result = runner.invoke(app, ["compass", "process"])
        assert result.exit_code == 0

        # Get initial event data
        db_session.expire_all()
        initial_events = db_session.query(Event).order_by(Event.title).all()
        initial_count = len(initial_events)
        initial_updated_at = initial_events[0].updated_at
        initial_title = initial_events[0].title

        # Modify the event title in database to simulate a change
        first_event = db_session.query(Event).order_by(Event.title).first()
        first_event.title = "Old Title"
        db_session.commit()

        # Second processing (should update, not create new)
        result = runner.invoke(app, ["compass", "process"])
        assert result.exit_code == 0
        assert "Events updated: 2" in result.stdout

        # Verify count unchanged but data updated
        db_session.expire_all()
        final_events = db_session.query(Event).order_by(Event.title).all()
        assert len(final_events) == initial_count

        # Find the event that was modified - it should be back to original title
        restored_events = [e for e in final_events if e.title in ["Test Event", "Second Test Event"]]
        assert len(restored_events) == 2  # Both should be restored
        assert any(e.updated_at > initial_updated_at for e in restored_events)

    def test_process_command_finds_latest_batch(self, runner, db_session):
        """Test that process command uses the latest batch."""
        # Create older batch
        old_batch = Batch(
            adapter_id="compass",
            method_name="get_calendar_events",
            parameters={"start_date": "2025-01-01"},
        )
        db_session.add(old_batch)
        db_session.commit()
        db_session.refresh(old_batch)

        old_payload = ApiPayload(
            adapter_id="compass",
            method_name="get_calendar_events",
            batch_id=old_batch.id,
            payload={
                "__type": "CalendarTransport:http://jdlf.com.au/ns/data/calendar",
                "activityId": 1,
                "activityType": 1,
                "allDay": False,
                "attendanceMode": 0,
                "attendeeUserId": 1,
                "backgroundColor": "#000000",
                "calendarId": 1,
                "description": "Old event",
                "finish": "2025-01-02T15:00:00",
                "guid": "old-guid",
                "instanceId": "old-instance",
                "isRecurring": False,
                "lessonPlanConfigured": False,
                "longTitle": "Old Event",
                "longTitleWithoutTime": "Old Event",
                "managerId": 1,
                "repeatForever": False,
                "repeatFrequency": 0,
                "rollMarked": False,
                "runningStatus": 0,
                "start": "2025-01-02T14:00:00",
                "targetStudentId": 1,
                "teachingDaysOnly": False,
                "title": "Old Event",
            },
        )
        db_session.add(old_payload)
        db_session.commit()

        # Create newer batch
        new_batch = Batch(
            adapter_id="compass",
            method_name="get_calendar_events",
            parameters={"start_date": "2025-12-01"},
        )
        db_session.add(new_batch)
        db_session.commit()
        db_session.refresh(new_batch)

        new_payload = ApiPayload(
            adapter_id="compass",
            method_name="get_calendar_events",
            batch_id=new_batch.id,
            payload={
                "__type": "CalendarTransport:http://jdlf.com.au/ns/data/calendar",
                "activityId": 2,
                "activityType": 1,
                "allDay": False,
                "attendanceMode": 0,
                "attendeeUserId": 2,
                "backgroundColor": "#FFFFFF",
                "calendarId": 2,
                "description": "New event",
                "finish": "2025-12-03T15:00:00",
                "guid": "new-guid",
                "instanceId": "new-instance",
                "isRecurring": False,
                "lessonPlanConfigured": False,
                "longTitle": "New Event",
                "longTitleWithoutTime": "New Event",
                "managerId": 2,
                "repeatForever": False,
                "repeatFrequency": 0,
                "rollMarked": False,
                "runningStatus": 0,
                "start": "2025-12-03T14:00:00",
                "targetStudentId": 2,
                "teachingDaysOnly": False,
                "title": "New Event",
            },
        )
        db_session.add(new_payload)
        db_session.commit()

        # Process command should use newer batch
        result = runner.invoke(app, ["compass", "process"])
        assert result.exit_code == 0
        assert new_batch.id in result.stdout

        # Verify only new event was processed
        db_session.expire_all()
        events = db_session.query(Event).all()
        assert len(events) == 1
        assert events[0].title == "New Event"

    def test_process_command_handles_invalid_payload(
        self, runner, db_session, batch_with_events
    ):
        """Test that process command handles invalid payloads gracefully."""
        # Add an invalid payload to the batch
        invalid_payload = ApiPayload(
            adapter_id="compass",
            method_name="get_calendar_events",
            batch_id=batch_with_events.id,
            payload={"invalid": "data", "missing": "required_fields"},
        )
        db_session.add(invalid_payload)
        db_session.commit()

        # Process should succeed but report error
        result = runner.invoke(app, ["compass", "process"])
        assert result.exit_code == 0
        assert "Processing errors: 1" in result.stdout

        # Verify valid events were still processed
        db_session.expire_all()
        events = db_session.query(Event).all()
        assert len(events) == 2  # Only the valid ones

    def test_process_command_output_format(self, runner, batch_with_events):
        """Test that process command outputs expected summary."""
        result = runner.invoke(app, ["compass", "process"])
        assert result.exit_code == 0
        assert "Processing calendar events from latest batch" in result.stdout
        assert "Finding latest batch" in result.stdout
        assert "Retrieving API payloads" in result.stdout
        assert "Processing events" in result.stdout
        assert "Summary:" in result.stdout
        assert "Batch ID:" in result.stdout
        assert "Total payloads: 2" in result.stdout
        assert "Events created: 2" in result.stdout
        assert "Events updated: 0" in result.stdout
        assert "Processing errors: 0" in result.stdout
