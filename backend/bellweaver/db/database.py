"""
Database configuration and session management.

Provides SQLAlchemy database engine, session factory, and base declarative class.
"""

import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Determine database path
DATA_DIR = Path(__file__).parent.parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "bellweaver.db"

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

print(f"Using DATABASE_URL={DATABASE_URL}")

# Create engine
# Enable foreign key constraints for SQLite
connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
)

# Enable foreign key constraints for SQLite (required for CASCADE DELETE)
if "sqlite" in DATABASE_URL:
    from sqlalchemy import event

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base class for ORM models
class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


def get_db() -> Generator[Session, None, None]:
    """
    Get database session.

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database schema.

    Creates all tables defined in models.
    """
    from bellweaver.db import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
