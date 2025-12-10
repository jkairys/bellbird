"""
Pydantic models for family management.

This module defines validation models for children, organisations,
communication channels, and their associations.
"""

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class OrganisationType(str, Enum):
    """Valid organisation types."""

    SCHOOL = "school"
    DAYCARE = "daycare"
    KINDERGARTEN = "kindergarten"
    SPORTS_TEAM = "sports_team"
    OTHER = "other"


class ChannelType(str, Enum):
    """Valid communication channel types."""

    COMPASS = "compass"
    HUBHELLO = "hubhello"
    CLASSDOJO = "classdojo"
    XPLORE = "xplore"
    OTHER = "other"


class SyncStatus(str, Enum):
    """Valid sync status values."""

    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


# Base models for shared fields
class ChildBase(BaseModel):
    """Base model for child fields."""

    name: str = Field(..., min_length=1, max_length=200)
    date_of_birth: date
    gender: Optional[str] = Field(None, max_length=50)
    interests: Optional[str] = None

    @field_validator('date_of_birth')
    @classmethod
    def validate_date_not_future(cls, v: date) -> date:
        """Validate that date_of_birth is not in the future."""
        if v > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return v


class OrganisationBase(BaseModel):
    """Base model for organisation fields."""

    name: str = Field(..., min_length=1, max_length=200)
    type: OrganisationType
    address: Optional[str] = Field(None, max_length=500)
    contact_info: Optional[dict] = None


class ChannelBase(BaseModel):
    """Base model for communication channel fields."""

    channel_type: ChannelType
    config: Optional[dict] = None
    is_active: bool = True


# Create models (for POST requests)
class ChildCreate(ChildBase):
    """Model for creating a new child."""
    pass


class OrganisationCreate(OrganisationBase):
    """Model for creating a new organisation."""
    pass


class ChannelCreate(ChannelBase):
    """Model for creating a new communication channel."""

    credentials: Optional[dict] = Field(
        None,
        description="Optional credentials (username, password) for authenticated channels"
    )


# Update models (for PUT requests)
class ChildUpdate(ChildBase):
    """Model for updating a child."""
    pass


class OrganisationUpdate(OrganisationBase):
    """Model for updating an organisation."""
    pass


class ChannelUpdate(ChannelBase):
    """Model for updating a communication channel."""

    credentials: Optional[dict] = Field(
        None,
        description="Optional credentials (username, password) for authenticated channels"
    )


# Response models (for API responses)
class Child(ChildBase):
    """Model for child API response."""

    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Organisation(OrganisationBase):
    """Model for organisation API response."""

    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommunicationChannel(ChannelBase):
    """Model for communication channel API response."""

    id: str
    organisation_id: str
    credential_source: Optional[str] = None
    last_sync_at: Optional[datetime] = None
    last_sync_status: Optional[SyncStatus] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Detail models (with nested relationships)
class ChildDetail(Child):
    """Model for child with organisations."""

    organisations: List[Organisation] = []


class OrganisationDetail(Organisation):
    """Model for organisation with children and channels."""

    children: List[Child] = []
    channels: List[CommunicationChannel] = []


# Association models
class ChildOrganisationCreate(BaseModel):
    """Model for creating child-organisation association."""

    organisation_id: str = Field(..., min_length=36, max_length=36)
