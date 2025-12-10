"""
Unit tests for Compass parser.

Tests the parsing layer that transforms raw API responses into validated Pydantic models.
"""

from datetime import datetime

import pytest
from compass_client import CompassParser, CompassParseError, CompassEvent, CompassUser


class TestCompassParserEvent:
    """Test parsing of calendar events."""

    @pytest.fixture
    def valid_event_raw(self):
        """Valid raw event data from Compass API."""
        return {
            "__type": "CalendarTransport:http://jdlf.com.au/ns/data/calendar",
            "activityId": 12345,
            "activityImportIdentifier": None,
            "activityType": 1,
            "allDay": False,
            "attendanceMode": 0,
            "attendeeUserId": 67890,
            "backgroundColor": "#4CAF50",
            "calendarId": 1,
            "categoryIds": None,
            "comment": None,
            "description": "Year 6 Mathematics",
            "eventSetupStatus": None,
            "finish": "2025-01-15T10:30:00",
            "guid": "abc-123-def-456",
            "inClassStatus": None,
            "instanceId": "inst-123",
            "isRecurring": False,
            "learningTaskActivityId": None,
            "learningTaskId": None,
            "lessonPlanConfigured": False,
            "location": "Room 101",
            "locations": None,
            "longTitle": "Mathematics - Year 6",
            "longTitleWithoutTime": "Mathematics",
            "managerId": 11111,
            "managers": None,
            "minutesMeetingId": None,
            "period": "1",
            "recurringFinish": None,
            "recurringStart": None,
            "repeatDays": None,
            "repeatForever": False,
            "repeatFrequency": 0,
            "repeatUntil": None,
            "rollMarked": False,
            "runningStatus": 0,
            "sessionName": None,
            "start": "2025-01-15T09:00:00",
            "subjectId": 101,
            "subjectLongName": "Mathematics",
            "targetStudentId": 67890,
            "teachingDaysOnly": True,
            "textColor": None,
            "title": "Mathematics",
            "unavailablePd": None,
        }

    @pytest.fixture
    def valid_user_raw(self):
        """Valid raw user data from Compass API."""
        return {
            "__type": "UserDetailsBlob",
            "age": 10,
            "birthday": "2014-05-15T00:00:00",
            "chroniclePinnedCount": 0,
            "contextualFormGroup": "6A",
            "dateOfDeath": None,
            "gender": "M",
            "hasEmailRestriction": False,
            "isBirthday": False,
            "userACTStudentID": None,
            "userAccessRestrictions": None,
            "userCompassPersonId": "person-uuid-123",
            "userConfirmationPhotoPath": "/photos/confirmation.jpg",
            "userDetails": None,
            "userDisplayCode": "SNP-1234",
            "userEmail": "student@example.com",
            "userFirstName": "John",
            "userFlags": [],
            "userFormGroup": "6A",
            "userFullName": "John Smith",
            "userGenderPronouns": None,
            "userHouse": "Red",
            "userId": 67890,
            "userLastName": "Smith",
            "userPhoneExtension": None,
            "userPhotoPath": "/photos/student.jpg",
            "userPreferredLastName": "Smith",
            "userPreferredName": "Johnny",
            "userReportName": "John Smith",
            "userReportPrefFirstLast": "Johnny Smith",
            "userRole": 1,
            "userRoleInSchool": None,
            "userSchoolId": "12345",
            "userSchoolURL": "https://school.compass.education",
            "userSex": "M",
            "userSquarePhotoPath": "/photos/student_square.jpg",
            "userStatus": 1,
            "userSussiID": "sussi-123",
            "userTimeLinePeriods": [],
            "userVSN": None,
            "userYearLevel": "6",
            "userYearLevelId": 6,
        }

    def test_parse_event_success(self, valid_event_raw):
        """Test successful parsing of a valid event."""
        event = CompassParser.parse(CompassEvent, valid_event_raw)

        assert isinstance(event, CompassEvent)
        assert event.activity_id == 12345
        assert event.title == "Mathematics"
        assert event.description == "Year 6 Mathematics"
        assert event.all_day is False
        assert event.location == "Room 101"
        assert isinstance(event.start, datetime)
        assert isinstance(event.finish, datetime)

    def test_parse_event_with_alias_fields(self, valid_event_raw):
        """Test that camelCase fields are correctly mapped to snake_case."""
        event = CompassParser.parse(CompassEvent, valid_event_raw)

        # Check that aliases work correctly
        assert event.activity_id == valid_event_raw["activityId"]
        assert event.attendee_user_id == valid_event_raw["attendeeUserId"]
        assert event.background_color == valid_event_raw["backgroundColor"]
        assert event.long_title == valid_event_raw["longTitle"]

    def test_parse_event_missing_required_field(self, valid_event_raw):
        """Test parsing fails when required field is missing."""
        del valid_event_raw["activityId"]

        with pytest.raises(CompassParseError) as exc_info:
            CompassParser.parse(CompassEvent, valid_event_raw)

        error = exc_info.value
        assert "validation error" in str(error).lower()
        assert error.raw_data == valid_event_raw
        assert error.validation_errors is not None

    def test_parse_event_invalid_field_type(self, valid_event_raw):
        """Test parsing fails when field has wrong type."""
        valid_event_raw["activityId"] = "not-an-integer"

        with pytest.raises(CompassParseError) as exc_info:
            CompassParser.parse(CompassEvent, valid_event_raw)

        error = exc_info.value
        assert error.raw_data == valid_event_raw
        assert error.validation_errors is not None

    def test_parse_event_invalid_datetime(self, valid_event_raw):
        """Test parsing fails with invalid datetime format."""
        valid_event_raw["start"] = "invalid-date"

        with pytest.raises(CompassParseError):
            CompassParser.parse(CompassEvent, valid_event_raw)

    def test_parse_events_success(self, valid_event_raw):
        """Test successful parsing of multiple events."""
        event2 = valid_event_raw.copy()
        event2["activityId"] = 99999
        event2["title"] = "Science"

        raw_events = [valid_event_raw, event2]
        events = CompassParser.parse(CompassEvent, raw_events)

        assert len(events) == 2
        assert all(isinstance(e, CompassEvent) for e in events)
        assert events[0].activity_id == 12345
        assert events[1].activity_id == 99999
        assert events[0].title == "Mathematics"
        assert events[1].title == "Science"

    def test_parse_events_empty_list(self):
        """Test parsing empty list returns empty list."""
        events = CompassParser.parse(CompassEvent, [])
        assert events == []

    def test_parse_events_one_invalid(self, valid_event_raw):
        """Test parsing fails when one event is invalid."""
        invalid_event = valid_event_raw.copy()
        del invalid_event["activityId"]

        raw_events = [valid_event_raw, invalid_event]

        with pytest.raises(CompassParseError) as exc_info:
            CompassParser.parse(CompassEvent, raw_events)

        error = exc_info.value
        assert "index 1" in str(error).lower()

    def test_parse_events_safe_all_valid(self, valid_event_raw):
        """Test safe parsing with all valid events."""
        event2 = valid_event_raw.copy()
        event2["activityId"] = 99999

        raw_events = [valid_event_raw, event2]
        valid_events, errors = CompassParser.parse_safe(CompassEvent, raw_events)

        assert len(valid_events) == 2
        assert len(errors) == 0
        assert all(isinstance(e, CompassEvent) for e in valid_events)

    def test_parse_events_safe_with_invalid(self, valid_event_raw):
        """Test safe parsing skips invalid events and collects errors."""
        invalid_event = valid_event_raw.copy()
        del invalid_event["activityId"]

        raw_events = [valid_event_raw, invalid_event]
        valid_events, errors = CompassParser.parse_safe(CompassEvent, raw_events)

        assert len(valid_events) == 1
        assert len(errors) == 1
        assert valid_events[0].activity_id == 12345
        assert isinstance(errors[0], CompassParseError)
        assert "index 1" in str(errors[0]).lower()

    def test_parse_events_safe_all_invalid(self, valid_event_raw):
        """Test safe parsing with all invalid events."""
        invalid_event = valid_event_raw.copy()
        del invalid_event["activityId"]

        raw_events = [invalid_event, invalid_event]
        valid_events, errors = CompassParser.parse_safe(CompassEvent, raw_events)

        assert len(valid_events) == 0
        assert len(errors) == 2
        assert all(isinstance(e, CompassParseError) for e in errors)


class TestCompassParserUser:
    """Test parsing of user details."""

    @pytest.fixture
    def valid_user_raw(self):
        """Valid raw user data from Compass API."""
        return {
            "__type": "UserDetailsBlob",
            "age": 10,
            "birthday": "2014-05-15T00:00:00",
            "chroniclePinnedCount": 0,
            "contextualFormGroup": "6A",
            "dateOfDeath": None,
            "gender": "M",
            "hasEmailRestriction": False,
            "isBirthday": False,
            "userACTStudentID": None,
            "userAccessRestrictions": None,
            "userCompassPersonId": "person-uuid-123",
            "userConfirmationPhotoPath": "/photos/confirmation.jpg",
            "userDetails": None,
            "userDisplayCode": "SNP-1234",
            "userEmail": "student@example.com",
            "userFirstName": "John",
            "userFlags": [],
            "userFormGroup": "6A",
            "userFullName": "John Smith",
            "userGenderPronouns": None,
            "userHouse": "Red",
            "userId": 67890,
            "userLastName": "Smith",
            "userPhoneExtension": None,
            "userPhotoPath": "/photos/student.jpg",
            "userPreferredLastName": "Smith",
            "userPreferredName": "Johnny",
            "userReportName": "John Smith",
            "userReportPrefFirstLast": "Johnny Smith",
            "userRole": 1,
            "userRoleInSchool": None,
            "userSchoolId": "12345",
            "userSchoolURL": "https://school.compass.education",
            "userSex": "M",
            "userSquarePhotoPath": "/photos/student_square.jpg",
            "userStatus": 1,
            "userSussiID": "sussi-123",
            "userTimeLinePeriods": [],
            "userVSN": None,
            "userYearLevel": "6",
            "userYearLevelId": 6,
        }

    def test_parse_user_success(self, valid_user_raw):
        """Test successful parsing of a valid user."""
        user = CompassParser.parse(CompassUser, valid_user_raw)

        assert isinstance(user, CompassUser)
        assert user.user_id == 67890
        assert user.user_first_name == "John"
        assert user.user_last_name == "Smith"
        assert user.user_preferred_name == "Johnny"
        assert user.user_email == "student@example.com"
        assert user.user_year_level == "6"

    def test_parse_user_with_alias_fields(self, valid_user_raw):
        """Test that camelCase fields are correctly mapped to snake_case."""
        user = CompassParser.parse(CompassUser, valid_user_raw)

        assert user.user_id == valid_user_raw["userId"]
        assert user.user_first_name == valid_user_raw["userFirstName"]
        assert user.user_compass_person_id == valid_user_raw["userCompassPersonId"]
        assert user.chronicle_pinned_count == valid_user_raw["chroniclePinnedCount"]

    def test_parse_user_missing_required_field(self, valid_user_raw):
        """Test parsing fails when required field is missing."""
        del valid_user_raw["userId"]

        with pytest.raises(CompassParseError) as exc_info:
            CompassParser.parse(CompassUser, valid_user_raw)

        error = exc_info.value
        assert "validation error" in str(error).lower()
        assert error.raw_data == valid_user_raw
        assert error.validation_errors is not None

    def test_parse_user_invalid_field_type(self, valid_user_raw):
        """Test parsing fails when field has wrong type."""
        valid_user_raw["userId"] = "not-an-integer"

        with pytest.raises(CompassParseError) as exc_info:
            CompassParser.parse(CompassUser, valid_user_raw)

        error = exc_info.value
        assert error.raw_data == valid_user_raw

    def test_parse_users_success(self, valid_user_raw):
        """Test successful parsing of multiple users."""
        user2 = valid_user_raw.copy()
        user2["userId"] = 11111
        user2["userFirstName"] = "Jane"

        raw_users = [valid_user_raw, user2]
        users = CompassParser.parse(CompassUser, raw_users)

        assert len(users) == 2
        assert all(isinstance(u, CompassUser) for u in users)
        assert users[0].user_id == 67890
        assert users[1].user_id == 11111
        assert users[0].user_first_name == "John"
        assert users[1].user_first_name == "Jane"

    def test_parse_users_empty_list(self):
        """Test parsing empty list returns empty list."""
        users = CompassParser.parse(CompassUser, [])
        assert users == []

    def test_parse_users_one_invalid(self, valid_user_raw):
        """Test parsing fails when one user is invalid."""
        invalid_user = valid_user_raw.copy()
        del invalid_user["userId"]

        raw_users = [valid_user_raw, invalid_user]

        with pytest.raises(CompassParseError) as exc_info:
            CompassParser.parse(CompassUser, raw_users)

        error = exc_info.value
        assert "index 1" in str(error).lower()


class TestCompassParseError:
    """Test CompassParseError exception."""

    def test_error_has_message(self):
        """Test error contains message."""
        error = CompassParseError("Something went wrong")
        assert str(error) == "Something went wrong"

    def test_error_has_raw_data(self):
        """Test error contains raw data."""
        raw = {"foo": "bar"}
        error = CompassParseError("Error", raw_data=raw)
        assert error.raw_data == raw

    def test_error_has_validation_errors(self):
        """Test error contains validation errors."""
        validation_errors = [{"field": "userId", "error": "required"}]
        error = CompassParseError("Error", validation_errors=validation_errors)
        assert error.validation_errors == validation_errors

    def test_error_all_fields(self):
        """Test error with all fields."""
        raw = {"invalid": "data"}
        validation_errors = [{"error": "details"}]
        error = CompassParseError("Parse failed", raw_data=raw, validation_errors=validation_errors)

        assert str(error) == "Parse failed"
        assert error.raw_data == raw
        assert error.validation_errors == validation_errors
