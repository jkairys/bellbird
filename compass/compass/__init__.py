"""
Compass Education API Client Package.

A Python client for interacting with the Compass Education platform API.
Provides authentication, data fetching, parsing, and validation.
"""

from compass.client import CompassClient
from compass.mock_client import CompassMockClient
from compass.models import (
    CompassEvent,
    CompassUser,
    CalendarEventLocation,
    CalendarEventManager,
)
from compass.parser import CompassParser, CompassParseError

__version__ = "0.1.0"

__all__ = [
    "CompassClient",
    "CompassMockClient",
    "CompassEvent",
    "CompassUser",
    "CalendarEventLocation",
    "CalendarEventManager",
    "CompassParser",
    "CompassParseError",
]
