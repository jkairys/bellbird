"""Platform-agnostic event models based on Schema.org Event specification.

This module provides normalized event models that can represent calendar events
from any source system (Compass, ClassDojo, HubHello, etc.).

The design follows Schema.org Event conventions for maximum interoperability.
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class Event(BaseModel):
    """
    Platform-agnostic calendar event model based on Schema.org Event.

    This model represents a normalized view of calendar events from any source.
    It strips away source-specific details while preserving the essential
    information needed for display and filtering.

    Attributes:
        title: Event name/title (maps to 'name' in Schema.org)
        start: Event start date and time (maps to 'startDate' in Schema.org)
        end: Event end date and time (maps to 'endDate' in Schema.org)
        description: Detailed description of the event (optional)
        location: Where the event takes place (optional, simple string for now)
        all_day: Whether this is an all-day event (default: False)
        organizer: Person or organization organizing the event (optional)
        attendees: List of attendee names (optional, stored as simple strings)
        status: Event status like 'EventScheduled', 'EventCancelled' (optional)
        created_at: When this event record was created in our system
        updated_at: When this event record was last updated in our system
    """

    # Core required fields
    title: str = Field(..., description="Event name/title")
    start: datetime = Field(..., description="Event start date and time")
    end: datetime = Field(..., description="Event end date and time")

    # Strongly recommended fields
    description: Optional[str] = Field(None, description="Detailed description")
    location: Optional[str] = Field(None, description="Event location")
    all_day: bool = Field(False, description="Whether this is an all-day event")

    # Additional useful fields
    organizer: Optional[str] = Field(None, description="Event organizer")
    attendees: list[str] = Field(
        default_factory=list, description="List of attendee names"
    )
    status: Optional[str] = Field(
        None, description="Event status (EventScheduled, EventCancelled, etc.)"
    )

    # Internal metadata
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this record was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this record was last updated",
    )
