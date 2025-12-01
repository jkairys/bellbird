"""
SQLAlchemy ORM models for Bellweaver database.

Models:
- Credential: Encrypted API credentials storage
- Batch: Adapter method invocation tracking
- ApiPayload: Raw API response storage with batch tracking
- Event: Normalized calendar event storage
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
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
    """

    __tablename__ = "api_payloads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    adapter_id = Column(String(50), nullable=False, index=True)
    method_name = Column(String(100), nullable=False, index=True)
    batch_id = Column(String(36), ForeignKey("batches.id"), nullable=False, index=True)
    payload = Column(SQLiteJSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

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
