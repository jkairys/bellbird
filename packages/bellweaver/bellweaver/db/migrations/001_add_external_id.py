"""
Database migration: Add external_id and updated_at to api_payloads table.

This migration adds:
1. external_id column to api_payloads table (for deduplication)
2. updated_at column to api_payloads table (for tracking updates)
3. Unique constraint on (adapter_id, method_name, external_id)

Run this migration before using the new watermarking features.
"""

import sqlite3
import sys
from pathlib import Path


def migrate(db_path: str = "backend/data/bellweaver.db"):
    """
    Apply migration to add external_id and updated_at to api_payloads.

    Args:
        db_path: Path to the SQLite database file
    """
    db_file = Path(db_path)

    if not db_file.exists():
        print(f"Database not found at {db_path}")
        print("Please run 'poetry run bellweaver compass sync' first to create the database.")
        return False

    print(f"Migrating database at {db_path}...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if external_id column already exists
        cursor.execute("PRAGMA table_info(api_payloads)")
        columns = [row[1] for row in cursor.fetchall()]

        if "external_id" in columns:
            print("✓ Migration already applied (external_id column exists)")
            return True

        print("  Adding external_id column...")
        cursor.execute("""
            ALTER TABLE api_payloads
            ADD COLUMN external_id VARCHAR(255)
        """)

        print("  Adding updated_at column...")
        cursor.execute("""
            ALTER TABLE api_payloads
            ADD COLUMN updated_at DATETIME
        """)

        # Populate external_id for existing records
        print("  Populating external_id for existing records...")
        cursor.execute("""
            SELECT id, adapter_id, method_name, payload FROM api_payloads
        """)

        rows = cursor.fetchall()
        for row_id, adapter_id, method_name, payload_json in rows:
            import json
            import hashlib

            payload = json.loads(payload_json) if payload_json else {}

            # Generate external_id based on adapter
            if adapter_id == "compass" and method_name == "get_calendar_events":
                # Use instanceId from Compass events
                external_id = payload.get("instanceId", "")
                if not external_id:
                    # Fallback to hash of identifying fields
                    activity_id = payload.get("activityId", "")
                    start = payload.get("start", "")
                    guid = payload.get("guid", "")
                    hash_input = f"{activity_id}:{start}:{guid}"
                    external_id = hashlib.sha256(hash_input.encode()).hexdigest()[:32]
            elif adapter_id == "compass" and method_name == "get_user_details":
                # Use userId for user details
                external_id = str(payload.get("userId", "unknown"))
            else:
                # Generic fallback
                payload_str = str(sorted(payload.items()))
                external_id = hashlib.sha256(payload_str.encode()).hexdigest()[:32]

            cursor.execute(
                "UPDATE api_payloads SET external_id = ? WHERE id = ?",
                (external_id, row_id)
            )

        # Set updated_at to created_at for existing records
        print("  Setting updated_at for existing records...")
        cursor.execute("""
            UPDATE api_payloads
            SET updated_at = created_at
            WHERE updated_at IS NULL
        """)

        # Make external_id NOT NULL after population
        print("  Creating new table with constraints...")
        cursor.execute("""
            CREATE TABLE api_payloads_new (
                id VARCHAR(36) PRIMARY KEY NOT NULL,
                adapter_id VARCHAR(50) NOT NULL,
                method_name VARCHAR(100) NOT NULL,
                batch_id VARCHAR(36) NOT NULL,
                external_id VARCHAR(255) NOT NULL,
                payload JSON NOT NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                FOREIGN KEY (batch_id) REFERENCES batches(id),
                UNIQUE (adapter_id, method_name, external_id)
            )
        """)

        print("  Copying data to new table (keeping most recent for duplicates)...")
        cursor.execute("""
            INSERT INTO api_payloads_new
            SELECT id, adapter_id, method_name, batch_id, external_id, payload, created_at, updated_at
            FROM (
                SELECT *,
                    ROW_NUMBER() OVER (
                        PARTITION BY adapter_id, method_name, external_id
                        ORDER BY created_at DESC
                    ) as rn
                FROM api_payloads
            )
            WHERE rn = 1
        """)

        print("  Replacing old table...")
        cursor.execute("DROP TABLE api_payloads")
        cursor.execute("ALTER TABLE api_payloads_new RENAME TO api_payloads")

        # Recreate indexes
        print("  Creating indexes...")
        cursor.execute("CREATE INDEX ix_api_payloads_adapter_id ON api_payloads(adapter_id)")
        cursor.execute("CREATE INDEX ix_api_payloads_method_name ON api_payloads(method_name)")
        cursor.execute("CREATE INDEX ix_api_payloads_batch_id ON api_payloads(batch_id)")
        cursor.execute("CREATE INDEX ix_api_payloads_external_id ON api_payloads(external_id)")
        cursor.execute("CREATE INDEX ix_api_payloads_created_at ON api_payloads(created_at)")

        conn.commit()
        print("✓ Migration completed successfully!")
        return True

    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "backend/data/bellweaver.db"
    success = migrate(db_path)
    sys.exit(0 if success else 1)
