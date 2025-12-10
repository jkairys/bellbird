"""Data models for Bellweaver.

Compass-specific models (CompassEvent, CompassUser, etc.) are now
provided by the compass_client package. Import them from there:

    from compass_client import CompassEvent, CompassUser
"""

# Re-export compass_client models for backward compatibility
from compass_client import (
    CalendarEventLocation,
    CalendarEventManager,
    CompassEvent,
    CompassUser,
)

__all__ = [
    "CalendarEventLocation",
    "CalendarEventManager",
    "CompassEvent",
    "CompassUser",
]
