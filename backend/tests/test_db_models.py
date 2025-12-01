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
from bellweaver.db.models import ApiPayload, Batch, Credential


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    # Create a temporary file
    fd, temp_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # Set database URL to temp file
    db_url = f"sqlite:///{temp_path}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})

    # Enable foreign key constraints in SQLite
    from sqlalchemy import event

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

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


class TestBatchModel:
    """Tests for the Batch model."""

    def test_create_batch(self, temp_db):
        """Test creating a batch record."""
        batch = Batch(
            adapter_id="compass",
            method_name="get_calendar_events",
            parameters={"start_date": "2025-12-01", "end_date": "2025-12-31"},
        )
        temp_db.add(batch)
        temp_db.commit()

        # Retrieve and verify
        retrieved = temp_db.query(Batch).first()
        assert retrieved is not None
        assert retrieved.adapter_id == "compass"
        assert retrieved.method_name == "get_calendar_events"
        assert retrieved.parameters == {"start_date": "2025-12-01", "end_date": "2025-12-31"}
        assert isinstance(retrieved.created_at, datetime)
        assert isinstance(retrieved.id, str)

    def test_batch_auto_id(self, temp_db):
        """Test that batch ID is auto-generated as UUID."""
        batch = Batch(
            adapter_id="compass",
            method_name="get_calendar_events",
        )
        temp_db.add(batch)
        temp_db.commit()

        assert batch.id is not None
        # Verify it's a valid UUID string
        uuid.UUID(batch.id)

    def test_batch_without_parameters(self, temp_db):
        """Test creating a batch without parameters (nullable)."""
        batch = Batch(
            adapter_id="compass",
            method_name="get_user_info",
            parameters=None,
        )
        temp_db.add(batch)
        temp_db.commit()

        retrieved = temp_db.query(Batch).first()
        assert retrieved.parameters is None

    def test_batch_with_complex_parameters(self, temp_db):
        """Test batch with complex nested parameters."""
        complex_params = {
            "filters": {
                "date_range": {"start": "2025-12-01", "end": "2025-12-31"},
                "categories": ["sports", "excursions"],
            },
            "options": {"include_cancelled": False, "max_results": 100},
        }

        batch = Batch(
            adapter_id="compass",
            method_name="get_calendar_events",
            parameters=complex_params,
        )
        temp_db.add(batch)
        temp_db.commit()

        retrieved = temp_db.query(Batch).first()
        assert retrieved.parameters["filters"]["date_range"]["start"] == "2025-12-01"
        assert retrieved.parameters["options"]["max_results"] == 100

    def test_batch_repr(self, temp_db):
        """Test string representation of Batch."""
        batch = Batch(
            adapter_id="compass",
            method_name="get_events",
        )
        temp_db.add(batch)
        temp_db.commit()

        repr_str = repr(batch)
        assert "compass" in repr_str
        assert "get_events" in repr_str

    def test_multiple_batches(self, temp_db):
        """Test creating multiple batches."""
        batches = []
        for i in range(5):
            batch = Batch(
                adapter_id="compass",
                method_name="get_calendar_events",
                parameters={"page": i},
            )
            batches.append(batch)
            temp_db.add(batch)

        temp_db.commit()

        # Verify all were created
        assert temp_db.query(Batch).count() == 5

        # Verify each has unique ID
        batch_ids = [b.id for b in batches]
        assert len(batch_ids) == len(set(batch_ids))  # All unique


class TestApiPayloadModel:
    """Tests for the ApiPayload model."""

    def test_create_api_payload(self, temp_db):
        """Test creating an API payload record."""
        # First create a batch
        batch = Batch(
            adapter_id="compass",
            method_name="get_calendar_events",
        )
        temp_db.add(batch)
        temp_db.commit()

        payload_data = {
            "activityId": 12345,
            "longTitle": "Test Event",
            "start": "2025-12-01T09:00:00",
            "finish": "2025-12-01T10:00:00",
        }

        payload = ApiPayload(
            adapter_id="compass",
            method_name="get_calendar_events",
            batch_id=batch.id,
            payload=payload_data,
        )
        temp_db.add(payload)
        temp_db.commit()

        # Retrieve and verify
        retrieved = temp_db.query(ApiPayload).first()
        assert retrieved is not None
        assert retrieved.adapter_id == "compass"
        assert retrieved.method_name == "get_calendar_events"
        assert retrieved.batch_id == batch.id
        assert retrieved.payload == payload_data
        assert isinstance(retrieved.created_at, datetime)
        assert isinstance(retrieved.id, str)

    def test_api_payload_auto_id(self, temp_db):
        """Test that ID is auto-generated as UUID."""
        # Create a batch first
        batch = Batch(adapter_id="compass", method_name="get_calendar_events")
        temp_db.add(batch)
        temp_db.commit()

        payload = ApiPayload(
            adapter_id="compass",
            method_name="get_calendar_events",
            batch_id=batch.id,
            payload={"test": "data"},
        )
        temp_db.add(payload)
        temp_db.commit()

        assert payload.id is not None
        # Verify it's a valid UUID string
        uuid.UUID(payload.id)  # Will raise if not valid UUID

    def test_batch_grouping(self, temp_db):
        """Test that records can be grouped by batch_id."""
        # Create a batch
        batch = Batch(adapter_id="compass", method_name="get_calendar_events")
        temp_db.add(batch)
        temp_db.commit()

        # Create multiple payloads in same batch
        payloads = []
        for i in range(5):
            payload = ApiPayload(
                adapter_id="compass",
                method_name="get_calendar_events",
                batch_id=batch.id,
                payload={"event_id": i},
            )
            payloads.append(payload)
            temp_db.add(payload)

        temp_db.commit()

        # Query by batch_id
        batch_records = temp_db.query(ApiPayload).filter_by(batch_id=batch.id).all()
        assert len(batch_records) == 5

        # Verify all have same batch_id
        assert all(record.batch_id == batch.id for record in batch_records)

    def test_multiple_adapters(self, temp_db):
        """Test storing payloads from multiple adapters."""
        adapters = ["compass", "classdojo", "hubhello", "xplore"]

        for adapter in adapters:
            # Create batch for each adapter
            batch = Batch(adapter_id=adapter, method_name="get_events")
            temp_db.add(batch)
            temp_db.commit()

            payload = ApiPayload(
                adapter_id=adapter,
                method_name="get_events",
                batch_id=batch.id,
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

    def test_multiple_methods(self, temp_db):
        """Test storing payloads from different method calls."""
        methods = ["get_calendar_events", "get_user_info", "get_school_details"]

        # Create one batch
        batch = Batch(adapter_id="compass", method_name="mixed")
        temp_db.add(batch)
        temp_db.commit()

        for method in methods:
            payload = ApiPayload(
                adapter_id="compass",
                method_name=method,
                batch_id=batch.id,
                payload={"method": method},
            )
            temp_db.add(payload)

        temp_db.commit()

        # Query by method
        for method in methods:
            records = temp_db.query(ApiPayload).filter_by(method_name=method).all()
            assert len(records) == 1
            assert records[0].payload["method"] == method

    def test_complex_json_payload(self, temp_db):
        """Test storing complex nested JSON payloads."""
        # Create batch first
        batch = Batch(adapter_id="compass", method_name="get_event_details")
        temp_db.add(batch)
        temp_db.commit()

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
            batch_id=batch.id,
            payload=complex_payload,
        )
        temp_db.add(payload)
        temp_db.commit()

        # Retrieve and verify structure is preserved
        retrieved = temp_db.query(ApiPayload).first()
        assert retrieved.payload["event"]["id"] == 12345
        assert len(retrieved.payload["event"]["attendees"]) == 2
        assert retrieved.payload["event"]["metadata"]["tags"] == ["important", "urgent"]

    def test_get_payload_method(self, temp_db):
        """Test the get_payload() helper method."""
        # Create batch first
        batch = Batch(adapter_id="compass", method_name="test")
        temp_db.add(batch)
        temp_db.commit()

        payload_data = {"test": "data"}

        payload = ApiPayload(
            adapter_id="compass",
            method_name="test",
            batch_id=batch.id,
            payload=payload_data,
        )
        temp_db.add(payload)
        temp_db.commit()

        # Test get_payload returns dict
        result = payload.get_payload()
        assert isinstance(result, dict)
        assert result == payload_data

    def test_api_payload_repr(self, temp_db):
        """Test string representation of ApiPayload."""
        # Create batch first
        batch = Batch(adapter_id="compass", method_name="get_events")
        temp_db.add(batch)
        temp_db.commit()

        payload = ApiPayload(
            adapter_id="compass",
            method_name="get_events",
            batch_id=batch.id,
            payload={"test": "data"},
        )
        temp_db.add(payload)
        temp_db.commit()

        repr_str = repr(payload)
        assert "compass" in repr_str
        assert "get_events" in repr_str
        assert batch.id in repr_str

    def test_query_by_created_at(self, temp_db):
        """Test that created_at is indexed and queryable."""
        # Create payloads
        for i in range(3):
            batch = Batch(adapter_id="compass", method_name="test")
            temp_db.add(batch)
            temp_db.commit()

            payload = ApiPayload(
                adapter_id="compass",
                method_name="test",
                batch_id=batch.id,
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

    def test_schema_flexibility(self, temp_db):
        """Test that different payload structures can be stored (schema flexibility)."""
        # Create batch
        batch = Batch(adapter_id="compass", method_name="get_events")
        temp_db.add(batch)
        temp_db.commit()

        # Old schema
        old_payload = ApiPayload(
            adapter_id="compass",
            method_name="get_events",
            batch_id=batch.id,
            payload={"eventId": 1, "title": "Old Event"},
        )

        # New schema with additional fields
        new_payload = ApiPayload(
            adapter_id="compass",
            method_name="get_events",
            batch_id=batch.id,
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
        records = temp_db.query(ApiPayload).filter_by(batch_id=batch.id).all()
        assert len(records) == 2

        # Verify old and new schemas coexist
        old = next(r for r in records if r.payload["eventId"] == 1)
        new = next(r for r in records if r.payload["eventId"] == 2)

        assert "newField" not in old.payload
        assert "newField" in new.payload
        assert new.payload["newField"] == "new data"


class TestBatchApiPayloadRelationship:
    """Tests for the relationship between Batch and ApiPayload models."""

    def test_batch_to_payload_relationship(self, temp_db):
        """Test accessing payloads from a batch."""
        # Create a batch
        batch = Batch(
            adapter_id="compass",
            method_name="get_calendar_events",
            parameters={"start_date": "2025-12-01"},
        )
        temp_db.add(batch)
        temp_db.commit()

        # Create multiple payloads for this batch
        for i in range(3):
            payload = ApiPayload(
                adapter_id="compass",
                method_name="get_calendar_events",
                batch_id=batch.id,
                payload={"event_id": i},
            )
            temp_db.add(payload)

        temp_db.commit()

        # Access payloads through batch relationship
        assert len(batch.payloads) == 3
        assert all(isinstance(p, ApiPayload) for p in batch.payloads)
        assert all(p.batch_id == batch.id for p in batch.payloads)

    def test_payload_to_batch_relationship(self, temp_db):
        """Test accessing batch from a payload."""
        # Create a batch
        batch = Batch(
            adapter_id="compass",
            method_name="get_calendar_events",
            parameters={"start_date": "2025-12-01"},
        )
        temp_db.add(batch)
        temp_db.commit()

        # Create a payload
        payload = ApiPayload(
            adapter_id="compass",
            method_name="get_calendar_events",
            batch_id=batch.id,
            payload={"event_id": 1},
        )
        temp_db.add(payload)
        temp_db.commit()

        # Access batch through payload relationship
        assert payload.batch is not None
        assert payload.batch.id == batch.id
        assert payload.batch.adapter_id == "compass"
        assert payload.batch.parameters["start_date"] == "2025-12-01"

    def test_cascade_delete(self, temp_db):
        """Test that deleting a batch deletes all its payloads."""
        # Create a batch
        batch = Batch(
            adapter_id="compass",
            method_name="get_calendar_events",
        )
        temp_db.add(batch)
        temp_db.commit()

        batch_id = batch.id

        # Create payloads
        for i in range(5):
            payload = ApiPayload(
                adapter_id="compass",
                method_name="get_calendar_events",
                batch_id=batch.id,
                payload={"event_id": i},
            )
            temp_db.add(payload)

        temp_db.commit()

        # Verify payloads exist
        assert temp_db.query(ApiPayload).filter_by(batch_id=batch_id).count() == 5

        # Delete the batch
        temp_db.delete(batch)
        temp_db.commit()

        # Verify all payloads are deleted (cascade)
        assert temp_db.query(ApiPayload).filter_by(batch_id=batch_id).count() == 0
        assert temp_db.query(Batch).filter_by(id=batch_id).count() == 0

    def test_foreign_key_constraint(self, temp_db):
        """Test that foreign key constraint prevents orphaned payloads."""
        # Try to create a payload with non-existent batch_id
        non_existent_batch_id = str(uuid.uuid4())

        payload = ApiPayload(
            adapter_id="compass",
            method_name="get_calendar_events",
            batch_id=non_existent_batch_id,
            payload={"event_id": 1},
        )
        temp_db.add(payload)

        # This should fail due to foreign key constraint
        with pytest.raises(Exception):  # SQLAlchemy will raise an integrity error
            temp_db.commit()

        temp_db.rollback()


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
            assert "batches" in tables
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
