"""
Mock Compass client for testing without real credentials.

Returns realistic calendar events from committed mock data for development and testing.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .exceptions import CompassClientError


class CompassMockClient:
    """
    Mock Compass client for testing without real credentials.

    Returns calendar events from data/mock/compass_events.json.
    Falls back to hardcoded synthetic events if the file doesn't exist.
    """

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        mock_data_dir: Optional[str] = None,
    ):
        """
        Initialize mock client.

        Args:
            base_url: Base URL (not used, but maintains interface parity)
            username: Username (not used, but maintains interface parity)
            password: Password (not used, but maintains interface parity)
            mock_data_dir: Optional custom directory for mock data files
        """
        self.base_url = base_url
        self.username = username
        self.password = password
        self.mock_data_dir = mock_data_dir
        self.user_id = None
        self._authenticated = False
        self._mock_events: Optional[List[Dict[str, Any]]] = None
        self._mock_user: Optional[Dict[str, Any]] = None

    def _load_mock_events_data(self) -> List[Dict[str, Any]]:
        """
        Load mock events from data/mock/compass_events.json.

        Falls back to hardcoded synthetic events if file doesn't exist
        (only when using default mock_data_dir).

        Raises:
            FileNotFoundError: If custom mock_data_dir is specified but file doesn't exist
        """
        if self.mock_data_dir:
            mock_file = Path(self.mock_data_dir) / "compass_events.json"
        else:
            mock_file = Path(__file__).parent.parent / "data" / "mock" / "compass_events.json"

        if mock_file.exists():
            try:
                with open(mock_file, "r") as f:
                    events = json.load(f)
                return events
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load mock data from {mock_file}: {e}")
                if self.mock_data_dir:
                    raise
                print("Falling back to hardcoded synthetic events")

        # If custom mock_data_dir was specified, raise error instead of falling back
        if self.mock_data_dir:
            raise FileNotFoundError(f"Mock data file not found: {mock_file}")

        return self._get_fallback_events()

    def _load_mock_user_data(self) -> Dict[str, Any]:
        """
        Load mock user from data/mock/compass_user.json.

        Falls back to hardcoded synthetic user if file doesn't exist
        (only when using default mock_data_dir).

        Raises:
            FileNotFoundError: If custom mock_data_dir is specified but file doesn't exist
        """
        if self.mock_data_dir:
            mock_file = Path(self.mock_data_dir) / "compass_user.json"
        else:
            mock_file = Path(__file__).parent.parent / "data" / "mock" / "compass_user.json"

        if mock_file.exists():
            try:
                with open(mock_file, "r") as f:
                    user = json.load(f)
                return user
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load mock data from {mock_file}: {e}")
                if self.mock_data_dir:
                    raise
                print("Falling back to hardcoded synthetic user")

        # If custom mock_data_dir was specified, raise error instead of falling back
        if self.mock_data_dir:
            raise FileNotFoundError(f"Mock data file not found: {mock_file}")

        return self._get_fallback_user()

    def _get_fallback_events(self) -> List[Dict[str, Any]]:
        """
        Return hardcoded synthetic events as fallback.

        Used when data/mock/compass_events.json doesn't exist.
        """
        return [
            {
                "__type": "CalendarTransport:http://jdlf.com.au/ns/data/calendar",
                "activityId": 1,
                "activityType": 1,
                "allDay": False,
                "attendanceMode": 0,
                "attendeeUserId": 12345,
                "backgroundColor": "#4CAF50",
                "calendarId": 1,
                "description": "Permission slip required. Cost: $25",
                "finish": "2025-12-15T15:00:00+11:00",
                "guid": "fallback-guid-001",
                "instanceId": "fallback-instance-001",
                "isRecurring": False,
                "lessonPlanConfigured": False,
                "longTitle": "09:00 - Year 3 Excursion to Taronga Zoo",
                "longTitleWithoutTime": "Year 3 Excursion to Taronga Zoo",
                "managerId": 1001,
                "repeatForever": False,
                "repeatFrequency": 0,
                "rollMarked": False,
                "runningStatus": 0,
                "start": "2025-12-15T09:00:00+11:00",
                "targetStudentId": 12345,
                "teachingDaysOnly": False,
                "title": "Year 3 Excursion to Taronga Zoo",
                "locations": [
                    {
                        "__type": "CalendarEventLocation:http://jdlf.com.au/ns/data/calendar",
                        "locationId": 1,
                        "locationName": "Taronga Zoo",
                    }
                ],
                "managers": [
                    {
                        "__type": "CalendarEventManager:http://jdlf.com.au/ns/data/calendar",
                        "managerUserId": 1001,
                        "managerImportIdentifier": "teacher1@school.edu",
                    }
                ],
            },
            {
                "__type": "CalendarTransport:http://jdlf.com.au/ns/data/calendar",
                "activityId": 2,
                "activityType": 1,
                "allDay": False,
                "attendanceMode": 0,
                "attendeeUserId": 12345,
                "backgroundColor": "#2196F3",
                "calendarId": 1,
                "description": "Evening performance. Tickets available online.",
                "finish": "2025-12-20T19:00:00+11:00",
                "guid": "fallback-guid-002",
                "instanceId": "fallback-instance-002",
                "isRecurring": False,
                "lessonPlanConfigured": False,
                "longTitle": "18:00 - Year 3 Music Performance",
                "longTitleWithoutTime": "Year 3 Music Performance",
                "managerId": 1002,
                "repeatForever": False,
                "repeatFrequency": 0,
                "rollMarked": False,
                "runningStatus": 0,
                "start": "2025-12-20T18:00:00+11:00",
                "targetStudentId": 12345,
                "teachingDaysOnly": False,
                "title": "Year 3 Music Performance",
                "locations": [
                    {
                        "__type": "CalendarEventLocation:http://jdlf.com.au/ns/data/calendar",
                        "locationId": 2,
                        "locationName": "School Hall",
                    }
                ],
                "managers": [
                    {
                        "__type": "CalendarEventManager:http://jdlf.com.au/ns/data/calendar",
                        "managerUserId": 1002,
                        "managerImportIdentifier": "teacher2@school.edu",
                    }
                ],
            },
            {
                "__type": "CalendarTransport:http://jdlf.com.au/ns/data/calendar",
                "activityId": 3,
                "activityType": 1,
                "allDay": True,
                "attendanceMode": 0,
                "attendeeUserId": 12345,
                "backgroundColor": "#FF9800",
                "calendarId": 1,
                "description": "Wear your favorite outfit. Gold coin donation.",
                "finish": "2025-12-18T23:59:59+11:00",
                "guid": "fallback-guid-003",
                "instanceId": "fallback-instance-003",
                "isRecurring": False,
                "lessonPlanConfigured": False,
                "longTitle": "Free Dress Day - Community Fund",
                "longTitleWithoutTime": "Free Dress Day - Community Fund",
                "managerId": 1003,
                "repeatForever": False,
                "repeatFrequency": 0,
                "rollMarked": False,
                "runningStatus": 0,
                "start": "2025-12-18T00:00:00+11:00",
                "targetStudentId": 12345,
                "teachingDaysOnly": False,
                "title": "Free Dress Day",
                "locations": [
                    {
                        "__type": "CalendarEventLocation:http://jdlf.com.au/ns/data/calendar",
                        "locationId": 3,
                        "locationName": "School",
                    }
                ],
                "managers": [
                    {
                        "__type": "CalendarEventManager:http://jdlf.com.au/ns/data/calendar",
                        "managerUserId": 1003,
                        "managerImportIdentifier": "admin@school.edu",
                    }
                ],
            },
        ]

    def _get_fallback_user(self) -> Dict[str, Any]:
        """
        Return hardcoded synthetic user as fallback.

        Used when data/mock/compass_user.json doesn't exist.
        """
        return {
            "__type": "UserDetailsBlob",
            "userId": 12345,
            "username": "jsmith",
            "userFirstName": "Jane",
            "userLastName": "Smith",
            "userPreferredName": "Jane",
            "userFullName": "Jane Smith",
            "userEmail": "jane.smith@example.com",
            "userDisplayCode": "JSM-0001",
            "userCompassPersonId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            "userYearLevel": "8",
            "userFormGroup": "8A",
            "userHouse": "Blue House",
            "userRole": 4,
            "age": 13,
            "birthday": "2012-03-15T00:00:00+11:00",
            "gender": "Female",
            "userPhotoPath": "/images/default-avatar.png",
            "userSquarePhotoPath": "/images/default-avatar-square.png",
            "userConfirmationPhotoPath": "/images/default-avatar.png",
            "chroniclePinnedCount": 0,
            "hasEmailRestriction": False,
            "isBirthday": False,
            "userFlags": [],
            "userTimeLinePeriods": [],
            "contextualFormGroup": "8A",
            "userPreferredLastName": "Smith",
            "userReportName": "Jane Smith",
            "userReportPrefFirstLast": "Jane Smith",
            "userSchoolId": "SCH001",
            "userSchoolURL": "https://school.compass.education",
            "userStatus": 1,
            "userSussiID": "12345",
        }

    def login(self) -> bool:
        """Mock login - always succeeds and loads mock data."""
        self._authenticated = True
        self._mock_events = self._load_mock_events_data()
        self._mock_user = self._load_mock_user_data()
        self.user_id = self._mock_user.get("userId")
        return True

    def get_user_details(self, target_user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Return mock user data.

        Args:
            target_user_id: User ID (ignored in mock mode)

        Returns:
            Dictionary containing mock user details
        """
        if not self._authenticated:
            raise CompassClientError("Not authenticated. Call login() first.")

        if self._mock_user is None:
            self._mock_user = self._load_mock_user_data()
            self.user_id = self._mock_user.get("userId")

        return self._mock_user

    def get_calendar_events(
        self, start_date: str, end_date: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Return calendar events from mock data.

        Filters events by date range and applies limit.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Maximum number of events to return (default 100)

        Returns:
            List of calendar event dictionaries
        """
        if not self._authenticated:
            raise CompassClientError("Not authenticated. Call login() first.")

        if self._mock_events is None:
            self._mock_events = self._load_mock_events_data()

        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        filtered = []
        for event in self._mock_events:
            try:
                event_start_str = event.get("start", "")
                if not event_start_str:
                    continue

                if "T" in event_start_str:
                    event_start = datetime.fromisoformat(event_start_str.replace("Z", "+00:00"))
                else:
                    event_start = datetime.strptime(event_start_str, "%Y-%m-%d")

                event_date = event_start.replace(
                    hour=0, minute=0, second=0, microsecond=0, tzinfo=None
                )
                if start <= event_date <= end:
                    filtered.append(event)
            except (ValueError, AttributeError):
                continue

        return filtered[:limit]

    def close(self) -> None:
        """Mock close - no-op."""
        pass
