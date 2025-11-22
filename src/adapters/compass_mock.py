"""
Mock Compass client for testing without real credentials.

Returns synthetic but realistic calendar events for development and testing.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta


class CompassMockClient:
    """
    Mock Compass client for testing without real credentials.
    Returns synthetic but realistic calendar events.
    """

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.user_id = 12345
        self._authenticated = False

    def login(self) -> bool:
        """Mock login - always succeeds."""
        self._authenticated = True
        return True

    def get_calendar_events(
        self,
        start_date: str,
        end_date: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Return synthetic calendar events for testing.

        Includes:
        - Excursions
        - Performances
        - Sports days
        - Assemblies
        - Free dress days
        - Permission slips
        - Mixed year levels
        """
        if not self._authenticated:
            raise Exception("Not authenticated")

        # Parse dates
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        # Generate synthetic events
        events = [
            {
                'id': '1',
                'longTitle': 'Year 3 Excursion to Taronga Zoo',
                'longTitleWithoutTime': 'Year 3 Excursion to Taronga Zoo',
                'start': (start + timedelta(days=5)).isoformat(),
                'finish': (start + timedelta(days=5, hours=3)).isoformat(),
                'allDay': False,
                'subjectTitle': 'Excursion',
                'subjectLongName': 'Excursion',
                'locations': [{'name': 'Taronga Zoo'}],
                'managers': [{'name': 'Mrs Smith'}],
                'rollMarked': False,
                'description': 'Permission slip required. Cost: $25'
            },
            {
                'id': '2',
                'longTitle': 'Year 3 Music Performance',
                'longTitleWithoutTime': 'Year 3 Music Performance',
                'start': (start + timedelta(days=10)).isoformat(),
                'finish': (start + timedelta(days=10, hours=1)).isoformat(),
                'allDay': False,
                'subjectTitle': 'Music',
                'subjectLongName': 'Music Performance',
                'locations': [{'name': 'School Hall'}],
                'managers': [{'name': 'Mr Johnson'}],
                'rollMarked': False,
                'description': 'Evening performance. Tickets available online.'
            },
            {
                'id': '3',
                'longTitle': 'Free Dress Day - Community Fund',
                'longTitleWithoutTime': 'Free Dress Day',
                'start': (start + timedelta(days=3)).isoformat(),
                'finish': (start + timedelta(days=3)).isoformat(),
                'allDay': True,
                'subjectTitle': 'Event',
                'subjectLongName': 'Free Dress Day',
                'locations': [{'name': 'School'}],
                'managers': [{'name': 'Principal'}],
                'rollMarked': False,
                'description': 'Wear your favorite outfit. Gold coin donation.'
            },
            {
                'id': '4',
                'longTitle': 'Year 2-3 Sports Carnival',
                'longTitleWithoutTime': 'Year 2-3 Sports Carnival',
                'start': (start + timedelta(days=7)).isoformat(),
                'finish': (start + timedelta(days=7, hours=4)).isoformat(),
                'allDay': False,
                'subjectTitle': 'Sports',
                'subjectLongName': 'Sports Carnival',
                'locations': [{'name': 'School Oval'}],
                'managers': [{'name': 'PE Department'}],
                'rollMarked': True,
                'description': 'House colors provided. Parents welcome to attend.'
            },
            {
                'id': '5',
                'longTitle': 'Whole School Assembly',
                'longTitleWithoutTime': 'Whole School Assembly',
                'start': (start + timedelta(days=2)).isoformat(),
                'finish': (start + timedelta(days=2, hours=1)).isoformat(),
                'allDay': False,
                'subjectTitle': 'Assembly',
                'subjectLongName': 'Whole School Assembly',
                'locations': [{'name': 'School Hall'}],
                'managers': [{'name': 'Principal'}],
                'rollMarked': True,
                'description': 'General announcements and awards.'
            },
            {
                'id': '6',
                'longTitle': 'Year 4 Excursion - Museum Visit',
                'longTitleWithoutTime': 'Year 4 Excursion - Museum Visit',
                'start': (start + timedelta(days=8)).isoformat(),
                'finish': (start + timedelta(days=8, hours=3)).isoformat(),
                'allDay': False,
                'subjectTitle': 'Excursion',
                'subjectLongName': 'Excursion',
                'locations': [{'name': 'State Museum'}],
                'managers': [{'name': 'Mrs Davis'}],
                'rollMarked': False,
                'description': 'Year 4 only. Permission slip due by Friday.'
            },
        ]

        # Filter by date range and limit
        filtered = [e for e in events if start <= datetime.fromisoformat(e['start']) <= end]
        return filtered[:limit]

    def close(self) -> None:
        """Mock close."""
        pass
