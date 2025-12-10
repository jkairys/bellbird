"""
Compass Client - Python client library for Compass Education API.

This package provides:
- CompassClient: Real HTTP client for Compass Education API
- CompassMockClient: Mock client using sample data for testing
- create_client: Factory function to create the appropriate client
- CompassEvent, CompassUser: Pydantic models for API data
- CompassParser: Generic parser for raw API responses

Example:
    >>> from compass_client import create_client, CompassEvent, CompassParser
    >>>
    >>> # Create client (mode determined by COMPASS_MODE env var)
    >>> client = create_client(base_url, username, password)
    >>> client.login()
    >>>
    >>> # Fetch and parse events
    >>> raw_events = client.get_calendar_events("2025-01-01", "2025-01-31")
    >>> events = CompassParser.parse(CompassEvent, raw_events)
    >>>
    >>> client.close()
"""

from .client import CompassClient
from .exceptions import (
    CompassAuthenticationError,
    CompassClientError,
    CompassParseError,
)
from .factory import create_client
from .mock_client import CompassMockClient
from .models import (
    CalendarEventLocation,
    CalendarEventManager,
    CompassEvent,
    CompassUser,
)
from .parser import CompassParser

__all__ = [
    # Clients
    "CompassClient",
    "CompassMockClient",
    "create_client",
    # Models
    "CompassEvent",
    "CompassUser",
    "CalendarEventLocation",
    "CalendarEventManager",
    # Parser
    "CompassParser",
    # Exceptions
    "CompassClientError",
    "CompassAuthenticationError",
    "CompassParseError",
]

__version__ = "0.1.0"
