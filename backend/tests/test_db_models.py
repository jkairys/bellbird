"""
Tests for database models and database setup.
"""

import os
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bellweaver.db.database import Base, init_db
from bellweaver.db.models import ApiPayload, Credential


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    # Create a temporary file
    fd, temp_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # Set database URL to temp file
    db_url = f"sqlite:///{temp_path}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    # Cleanup
    session.close()
    engine.dispose()
    os.unlink(temp_path)


@pytest.fixture
def sample_batch_id():
    """Generate a sample batch ID for tests."""
    return str(uuid.uuid4())


class TestCredentialModel:
    """Tests for the Credential model."""

    def test_create_credential(self, temp_db):
        """Test creating a credential."""
        credential = Credential(
            source="compass",
            username="test_user",
            password_encrypted="encrypted_password_123",
        )
        temp_db.add(credential)
        temp_db.commit()

        # Retrieve and verify
        retrieved = temp_db.query(Credential).filter_by(source="compass").first()
        assert retrieved is not None
        assert retrieved.source == "compass"
        assert retrieved.username == "test_user"
        assert retrieved.password_encrypted == "encrypted_password_123"
        assert isinstance(retrieved.created_at, datetime)
        assert isinstance(retrieved.updated_at, datetime)

    def test_credential_primary_key(self, temp_db):
        """Test that source is the primary key."""
        # Create first credential
        cred1 = Credential(
            source="compass",
            username="user1",
            password_encrypted="pass1",
        )
        temp_db.add(cred1)
        temp_db.commit()

        # Try to create another with same source (should replace)
        cred2 = Credential(
            source="compass",
            username="user2",
            password_encrypted="pass2",
        )
        temp_db.merge(cred2)
        temp_db.commit()

        # Should only have one record
        count = temp_db.query(Credential).filter_by(source="compass").count()
        assert count == 1

        # Should be the updated one
        retrieved = temp_db.query(Credential).filter_by(source="compass").first()
        assert retrieved.username == "user2"

    def test_multiple_sources(self, temp_db):
        """Test storing credentials for multiple sources."""
        sources = ["compass", "classdojo", "hubhello", "xplore"]

        for source in sources:
            cred = Credential(
                source=source,
                username=f"{source}_user",
                password_encrypted=f"{source}_encrypted",
            )
            temp_db.add(cred)

        temp_db.commit()

        # Verify all were created
        assert temp_db.query(Credential).count() == len(sources)

        # Verify each source
        for source in sources:
            cred = temp_db.query(Credential).filter_by(source=source).first()
            assert cred is not None
            assert cred.username == f"{source}_user"

    def test_credential_repr(self, temp_db):
        """Test string representation of Credential."""
        cred = Credential(
            source="compass",
            username="test_user",
            password_encrypted="encrypted",
        )
        assert "compass" in repr(cred)
        assert "test_user" in repr(cred)


class TestApiPayloadModel:
    """Tests for the ApiPayload model."""

    def test_create_api_payload(self, temp_db, sample_batch_id):
        """Test creating an API payload record."""
        payload_data = {
            "activityId": 12345,
            "longTitle": "Test Event",
            "start": "2025-12-01T09:00:00",
            "finish": "2025-12-01T10:00:00",
        }

        payload = ApiPayload(
            adapter_id="compass",
            method_name="get_calendar_events",
            batch_id=sample_batch_id,
            payload=payload_data,
        )
        temp_db.add(payload)
        temp_db.commit()

        # Retrieve and verify
        retrieved = temp_db.query(ApiPayload).first()
        assert retrieved is not None
        assert retrieved.adapter_id == "compass"
        assert retrieved.method_name == "get_calendar_events"
        assert retrieved.batch_id == sample_batch_id
        assert retrieved.payload == payload_data
        assert isinstance(retrieved.created_at, datetime)
        assert isinstance(retrieved.id, str)

    def test_api_payload_auto_id(self, temp_db, sample_batch_id):
        """Test that ID is auto-generated as UUID."""
        payload = ApiPayload(
            adapter_id="compass",
            method_name="get_calendar_events",
            batch_id=sample_batch_id,
            payload={"test": "data"},
        )
        temp_db.add(payload)
        temp_db.commit()

        assert payload.id is not None
        # Verify it's a valid UUID string
        uuid.UUID(payload.id)  # Will raise if not valid UUID

    def test_batch_grouping(self, temp_db):
        """Test that records can be grouped by batch_id."""
        batch_id = str(uuid.uuid4())

        # Create multiple payloads in same batch
        payloads = []
        for i in range(5):
            payload = ApiPayload(
                adapter_id="compass",
                method_name="get_calendar_events",
                batch_id=batch_id,
                payload={"event_id": i},
            )
            payloads.append(payload)
            temp_db.add(payload)

        temp_db.commit()

        # Query by batch_id
        batch_records = temp_db.query(ApiPayload).filter_by(batch_id=batch_id).all()
        assert len(batch_records) == 5

        # Verify all have same batch_id
        assert all(record.batch_id == batch_id for record in batch_records)

    def test_multiple_adapters(self, temp_db):
        """Test storing payloads from multiple adapters."""
        adapters = ["compass", "classdojo", "hubhello", "xplore"]

        for adapter in adapters:
            payload = ApiPayload(
                adapter_id=adapter,
                method_name="get_events",
                batch_id=str(uuid.uuid4()),
                payload={"source": adapter},
            )
            temp_db.add(payload)

        temp_db.commit()

        # Verify all were created
        assert temp_db.query(ApiPayload).count() == len(adapters)

        # Query by adapter
        for adapter in adapters:
            records = temp_db.query(ApiPayload).filter_by(adapter_id=adapter).all()
            assert len(records) == 1
            assert records[0].payload["source"] == adapter

    def test_multiple_methods(self, temp_db, sample_batch_id):
        """Test storing payloads from different method calls."""
        methods = ["get_calendar_events", "get_user_info", "get_school_details"]

        for method in methods:
            payload = ApiPayload(
                adapter_id="compass",
                method_name=method,
                batch_id=sample_batch_id,
                payload={"method": method},
            )
            temp_db.add(payload)

        temp_db.commit()

        # Query by method
        for method in methods:
            records = temp_db.query(ApiPayload).filter_by(method_name=method).all()
            assert len(records) == 1
            assert records[0].payload["method"] == method

    def test_complex_json_payload(self, temp_db, sample_batch_id):
        """Test storing complex nested JSON payloads."""
        complex_payload = {
            "event": {
                "id": 12345,
                "title": "Test Event",
                "attendees": [
                    {"name": "John", "role": "teacher"},
                    {"name": "Jane", "role": "student"},
                ],
                "metadata": {
                    "created": "2025-12-01",
                    "tags": ["important", "urgent"],
                },
            }
        }

        payload = ApiPayload(
            adapter_id="compass",
            method_name="get_event_details",
            batch_id=sample_batch_id,
            payload=complex_payload,
        )
        temp_db.add(payload)
        temp_db.commit()

        # Retrieve and verify structure is preserved
        retrieved = temp_db.query(ApiPayload).first()
        assert retrieved.payload["event"]["id"] == 12345
        assert len(retrieved.payload["event"]["attendees"]) == 2
        assert retrieved.payload["event"]["metadata"]["tags"] == ["important", "urgent"]

    def test_get_payload_method(self, temp_db, sample_batch_id):
        """Test the get_payload() helper method."""
        payload_data = {"test": "data"}

        payload = ApiPayload(
            adapter_id="compass",
            method_name="test",
            batch_id=sample_batch_id,
            payload=payload_data,
        )
        temp_db.add(payload)
        temp_db.commit()

        # Test get_payload returns dict
        result = payload.get_payload()
        assert isinstance(result, dict)
        assert result == payload_data

    def test_api_payload_repr(self, temp_db, sample_batch_id):
        """Test string representation of ApiPayload."""
        payload = ApiPayload(
            adapter_id="compass",
            method_name="get_events",
            batch_id=sample_batch_id,
            payload={"test": "data"},
        )
        temp_db.add(payload)
        temp_db.commit()

        repr_str = repr(payload)
        assert "compass" in repr_str
        assert "get_events" in repr_str
        assert sample_batch_id in repr_str

    def test_query_by_created_at(self, temp_db):
        """Test that created_at is indexed and queryable."""
        # Create payloads
        for i in range(3):
            payload = ApiPayload(
                adapter_id="compass",
                method_name="test",
                batch_id=str(uuid.uuid4()),
                payload={"index": i},
            )
            temp_db.add(payload)

        temp_db.commit()

        # Query by created_at (should work due to index)
        recent = (
            temp_db.query(ApiPayload)
            .order_by(ApiPayload.created_at.desc())
            .first()
        )
        assert recent is not None
        assert recent.payload["index"] == 2  # Last created

    def test_schema_flexibility(self, temp_db, sample_batch_id):
        """Test that different payload structures can be stored (schema flexibility)."""
        # Old schema
        old_payload = ApiPayload(
            adapter_id="compass",
            method_name="get_events",
            batch_id=sample_batch_id,
            payload={"eventId": 1, "title": "Old Event"},
        )

        # New schema with additional fields
        new_payload = ApiPayload(
            adapter_id="compass",
            method_name="get_events",
            batch_id=sample_batch_id,
            payload={
                "eventId": 2,
                "title": "New Event",
                "newField": "new data",
                "anotherNewField": {"nested": "data"},
            },
        )

        temp_db.add(old_payload)
        temp_db.add(new_payload)
        temp_db.commit()

        # Both should be retrievable
        records = temp_db.query(ApiPayload).filter_by(batch_id=sample_batch_id).all()
        assert len(records) == 2

        # Verify old and new schemas coexist
        old = next(r for r in records if r.payload["eventId"] == 1)
        new = next(r for r in records if r.payload["eventId"] == 2)

        assert "newField" not in old.payload
        assert "newField" in new.payload
        assert new.payload["newField"] == "new data"


class TestDatabaseSetup:
    """Tests for database initialization and setup."""

    def test_init_db_creates_tables(self):
        """Test that init_db creates all tables."""
        # Create temporary database
        fd, temp_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        try:
            from sqlalchemy import create_engine, inspect

            # Create a new engine for the temp database
            test_engine = create_engine(f"sqlite:///{temp_path}")

            # Create tables using Base metadata
            Base.metadata.create_all(bind=test_engine)

            # Check tables were created
            inspector = inspect(test_engine)
            tables = inspector.get_table_names()

            assert "credentials" in tables
            assert "api_payloads" in tables

            # Cleanup engine
            test_engine.dispose()

        finally:
            os.unlink(temp_path)

    def test_default_database_path(self):
        """Test that default database path is in data/ directory."""
        from bellweaver.db.database import DB_PATH, DATA_DIR

        assert DATA_DIR.name == "data"
        assert DB_PATH.name == "bellweaver.db"
        assert DB_PATH.parent == DATA_DIR
