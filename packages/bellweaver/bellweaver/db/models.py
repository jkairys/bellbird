"""
SQLAlchemy ORM models for Bellweaver database.

Models:
- Credential: Encrypted API credentials storage
- Batch: Adapter method invocation tracking
- ApiPayload: Raw API response storage with batch tracking
- Event: Normalized calendar event storage
- Child: Child profile management
- Organisation: School/daycare/sports team management
- ChildOrganisation: Many-to-many child-organisation association
- CommunicationChannel: Communication channel configuration
"""

import uuid
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import relationship

from bellweaver.db.database import Base


class Credential(Base):
    """
    Encrypted credential storage.

    Stores encrypted credentials for external API services.
    """

    __tablename__ = "credentials"

    source = Column(String(50), primary_key=True, nullable=False)
    username = Column(String(255), nullable=False)
    password_encrypted = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Credential(source='{self.source}', username='{self.username}')>"


class Batch(Base):
    """
    Adapter method invocation tracking.

    Stores metadata about each adapter method call, including parameters.
    Acts as a foreign key for related ApiPayload records.
    """

    __tablename__ = "batches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    adapter_id = Column(String(50), nullable=False, index=True)
    method_name = Column(String(100), nullable=False, index=True)
    parameters = Column(SQLiteJSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationship to ApiPayload records
    payloads = relationship("ApiPayload", back_populates="batch", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return (
            f"<Batch(id='{self.id}', adapter='{self.adapter_id}', "
            f"method='{self.method_name}')>"
        )


class ApiPayload(Base):
    """
    Raw API payload storage.

    Stores raw API responses as JSON blobs to handle schema changes gracefully.
    Records are grouped by batch_id for related API calls.

    Uses a unique constraint on (adapter_id, method_name, external_id) to prevent
    duplicate storage of the same event across multiple syncs.
    """

    __tablename__ = "api_payloads"
    __table_args__ = (
        UniqueConstraint('adapter_id', 'method_name', 'external_id', name='uix_api_payload_external'),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    adapter_id = Column(String(50), nullable=False, index=True)
    method_name = Column(String(100), nullable=False, index=True)
    batch_id = Column(String(36), ForeignKey("batches.id"), nullable=False, index=True)
    external_id = Column(String(255), nullable=False, index=True)  # Unique identifier from source system
    payload = Column(SQLiteJSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship to Batch
    batch = relationship("Batch", back_populates="payloads")

    def __repr__(self) -> str:
        return (
            f"<ApiPayload(id='{self.id}', adapter='{self.adapter_id}', "
            f"method='{self.method_name}', batch='{self.batch_id}')>"
        )

    def get_payload(self) -> Dict[str, Any]:
        """
        Get the stored payload as a dictionary.

        Returns:
            Parsed JSON payload
        """
        return self.payload if isinstance(self.payload, dict) else {}

    @staticmethod
    def generate_external_id(payload: Dict[str, Any], adapter_id: str = "compass") -> str:
        """
        Generate a unique external ID from a payload.

        For Compass events, uses the 'instanceId' field if available,
        otherwise falls back to a hash of key identifying fields.

        Args:
            payload: Raw API payload dictionary
            adapter_id: Adapter identifier (defaults to "compass")

        Returns:
            Unique external identifier string
        """
        if adapter_id == "compass":
            # Compass events have instanceId which is unique per event instance
            instance_id = payload.get("instanceId")
            if instance_id:
                return str(instance_id)

            # Fallback: create hash from identifying fields
            activity_id = payload.get("activityId", "")
            start = payload.get("start", "")
            guid = payload.get("guid", "")

            hash_input = f"{activity_id}:{start}:{guid}"
            return hashlib.sha256(hash_input.encode()).hexdigest()[:32]

        # Generic fallback for other adapters
        payload_str = str(sorted(payload.items()))
        return hashlib.sha256(payload_str.encode()).hexdigest()[:32]


class Event(Base):
    """
    Normalized calendar event storage.

    Platform-agnostic representation of calendar events from any source.
    Maintains lineage to original ApiPayload for traceability.
    """

    __tablename__ = "events"

    id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False
    )

    # Foreign key to original API payload for lineage tracking
    api_payload_id = Column(
        String(36), ForeignKey("api_payloads.id"), nullable=False, index=True
    )

    # Core event fields
    title = Column(String(500), nullable=False)
    start = Column(DateTime, nullable=False, index=True)
    end = Column(DateTime, nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(500), nullable=True)
    all_day = Column(Boolean, default=False, nullable=False)

    # Additional fields
    organizer = Column(String(255), nullable=True)
    attendees = Column(SQLiteJSON, nullable=True)  # Stored as JSON array
    status = Column(String(50), nullable=True)

    # Metadata
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship to ApiPayload
    api_payload = relationship("ApiPayload")

    def __repr__(self) -> str:
        return f"<Event(id='{self.id}', title='{self.title}', start='{self.start}')>"


class Child(Base):
    """
    Child profile.

    Stores information about a child in the family, including name, date of birth,
    gender, and interests. Associated with organisations through ChildOrganisation.
    """

    __tablename__ = "children"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    name = Column(String(200), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(50), nullable=True)
    interests = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Many-to-many relationship with Organisation via ChildOrganisation
    organisations = relationship(
        "Organisation",
        secondary="child_organisations",
        back_populates="children",
    )

    def __repr__(self) -> str:
        return f"<Child(id='{self.id}', name='{self.name}', dob='{self.date_of_birth}')>"


class Organisation(Base):
    """
    Organisation (school, daycare, kindergarten, sports team, etc.).

    Stores information about an organisation, including name, type, address, and
    contact information. Associated with children through ChildOrganisation and
    has communication channels.
    """

    __tablename__ = "organisations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    name = Column(String(200), nullable=False, unique=True)
    type = Column(String(50), nullable=False, index=True)
    address = Column(String(500), nullable=True)
    contact_info = Column(SQLiteJSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Many-to-many relationship with Child via ChildOrganisation
    children = relationship(
        "Child",
        secondary="child_organisations",
        back_populates="organisations",
    )

    # One-to-many relationship with CommunicationChannel
    channels = relationship(
        "CommunicationChannel",
        back_populates="organisation",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Organisation(id='{self.id}', name='{self.name}', type='{self.type}')>"


class ChildOrganisation(Base):
    """
    Association table for Child-Organisation many-to-many relationship.

    Uses composite primary key (child_id, organisation_id) to prevent duplicates.
    Cascade delete on both foreign keys ensures cleanup when either entity is deleted.
    """

    __tablename__ = "child_organisations"

    child_id = Column(String(36), ForeignKey("children.id", ondelete="CASCADE"), primary_key=True)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), primary_key=True)

    def __repr__(self) -> str:
        return f"<ChildOrganisation(child_id='{self.child_id}', organisation_id='{self.organisation_id}')>"


class CommunicationChannel(Base):
    """
    Communication channel configuration.

    Stores configuration for communication channels (Compass, HubHello, ClassDojo, etc.)
    associated with an organisation. Credentials are stored separately in the Credential table.
    """

    __tablename__ = "communication_channels"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    organisation_id = Column(String(36), ForeignKey("organisations.id"), nullable=False, index=True)
    channel_type = Column(String(50), nullable=False, index=True)
    credential_source = Column(String(50), ForeignKey("credentials.source", ondelete="SET NULL"), nullable=True)
    config = Column(SQLiteJSON, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    last_sync_at = Column(DateTime, nullable=True)
    last_sync_status = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Many-to-one relationship with Organisation
    organisation = relationship("Organisation", back_populates="channels")

    # Many-to-one relationship with Credential (optional)
    credential = relationship("Credential")

    def __repr__(self) -> str:
        return (
            f"<CommunicationChannel(id='{self.id}', type='{self.channel_type}', "
            f"organisation_id='{self.organisation_id}')>"
        )
