"""
SQLAlchemy ORM models for Bellweaver database.

Models:
- Credential: Encrypted API credentials storage
- ApiPayload: Raw API response storage with batch tracking
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy import JSON, Column, DateTime, String, Text
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON

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
    batch_id = Column(String(36), nullable=False, index=True)
    payload = Column(SQLiteJSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

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
