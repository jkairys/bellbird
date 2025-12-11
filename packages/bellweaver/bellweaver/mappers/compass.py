"""Mapper for transforming Compass-specific models to platform-agnostic Event model.

This module handles the transformation of CompassEvent objects (from the Compass API)
into normalized Event objects that can be used consistently across the application.
"""

from bellweaver.models.event import Event
from compass_client import CompassEvent


def compass_event_to_event(compass_event: CompassEvent) -> Event:
    """
    Transform a CompassEvent into a normalized Event.

    This mapper extracts the essential calendar information from the Compass-specific
    model and creates a clean, platform-agnostic Event representation.

    Args:
        compass_event: Compass-specific event model

    Returns:
        Normalized Event model

    Example:
        >>> compass_event = CompassEvent(...)
        >>> event = compass_event_to_event(compass_event)
        >>> print(event.title, event.start, event.end)
    """
    # Extract location - Compass has both 'location' string and 'locations' array
    # Prefer the simple 'location' string if available
    location = compass_event.location

    # If no simple location but we have locations array, use first location name
    if not location and compass_event.locations and len(compass_event.locations) > 0:
        location = compass_event.locations[0].location_name

    # Extract attendees from managers if available
    attendees: list = []
    if compass_event.managers:
        # For now, we don't have manager names in the model, just IDs
        # We can enhance this later when we have user lookup capabilities
        pass

    # Map event status - Compass uses runningStatus as an integer
    # We'll convert to a simple string for now
    status_map = {
        0: "EventScheduled",
        1: "EventCancelled",
        2: "EventPostponed",
        # Add more mappings as we discover them
    }
    status = status_map.get(compass_event.running_status, None)

    return Event(
        title=compass_event.title,
        start=compass_event.start,
        end=compass_event.finish,
        description=compass_event.description,
        location=location,
        all_day=compass_event.all_day,
        organizer=None,  # Not available in Compass model currently
        attendees=attendees,
        status=status,
    )
