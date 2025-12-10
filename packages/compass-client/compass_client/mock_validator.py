"""
Mock data validation for Compass API package.

Validates that committed mock data files exist and conform to expected schemas.
Used at startup to ensure mock mode can function properly.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class MockDataValidationError(Exception):
    """Raised when mock data validation fails."""

    pass


def load_and_validate_mock_data(
    mock_data_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Load and validate all mock data files.

    Args:
        mock_data_dir: Path to mock data directory. If None, uses default location.

    Returns:
        Dictionary with validated mock data:
        {
            'events': [...],
            'user': {...},
            'schema_version': {...}
        }

    Raises:
        MockDataValidationError: If any mock data file is missing, invalid, or
                                 doesn't match expected schema.
    """
    if mock_data_dir is None:
        # Resolve to the actual location of the package when installed in editable mode
        # Path(__file__) is <package_root>/compass_client/mock_validator.py
        # .parent is <package_root>/compass_client/
        # .parent again is <package_root>/
        mock_data_dir = Path(__file__).resolve().parent.parent / "data" / "mock"

    # Validate directory exists
    if not mock_data_dir.exists():
        raise MockDataValidationError(
            f"Mock data directory does not exist: {mock_data_dir}"
        )

    # Load and validate each required file
    events = _load_and_validate_events(mock_data_dir)
    user = _load_and_validate_user(mock_data_dir)
    schema_version = _load_and_validate_schema_version(mock_data_dir)

    return {
        "events": events,
        "user": user,
        "schema_version": schema_version,
    }


def validate_mock_data_schema(
    mock_data_dir: Optional[Path] = None,
) -> bool:
    """
    Validate that all mock data files exist and are valid JSON.

    Args:
        mock_data_dir: Path to mock data directory. If None, uses default location.

    Returns:
        True if all mock data is valid.

    Raises:
        MockDataValidationError: If any validation fails.
    """
    try:
        load_and_validate_mock_data(mock_data_dir)
        return True
    except MockDataValidationError:
        raise


def _load_and_validate_events(mock_data_dir: Path) -> List[Dict[str, Any]]:
    """Load and validate compass_events.json."""
    events_file = mock_data_dir / "compass_events.json"

    if not events_file.exists():
        raise MockDataValidationError(
            f"Mock events file not found: {events_file}"
        )

    try:
        with open(events_file, "r") as f:
            events = json.load(f)
    except json.JSONDecodeError as e:
        raise MockDataValidationError(
            f"Invalid JSON in {events_file}: {e}"
        )
    except IOError as e:
        raise MockDataValidationError(
            f"Cannot read {events_file}: {e}"
        )

    if not isinstance(events, list):
        raise MockDataValidationError(
            f"compass_events.json must contain a JSON array, got {type(events).__name__}"
        )

    # Validate each event has required fields
    for i, event in enumerate(events):
        if not isinstance(event, dict):
            raise MockDataValidationError(
                f"Event {i} in compass_events.json is not a dictionary"
            )

        required_fields = {"start", "finish", "title"}
        missing_fields = required_fields - set(event.keys())
        if missing_fields:
            raise MockDataValidationError(
                f"Event {i} in compass_events.json missing required fields: {missing_fields}"
            )

    return events


def _load_and_validate_user(mock_data_dir: Path) -> Dict[str, Any]:
    """Load and validate compass_user.json."""
    user_file = mock_data_dir / "compass_user.json"

    if not user_file.exists():
        raise MockDataValidationError(
            f"Mock user file not found: {user_file}"
        )

    try:
        with open(user_file, "r") as f:
            user = json.load(f)
    except json.JSONDecodeError as e:
        raise MockDataValidationError(
            f"Invalid JSON in {user_file}: {e}"
        )
    except IOError as e:
        raise MockDataValidationError(
            f"Cannot read {user_file}: {e}"
        )

    if not isinstance(user, dict):
        raise MockDataValidationError(
            f"compass_user.json must contain a JSON object, got {type(user).__name__}"
        )

    # Validate required user fields
    required_fields = {"userId", "userFirstName", "userLastName"}
    missing_fields = required_fields - set(user.keys())
    if missing_fields:
        raise MockDataValidationError(
            f"compass_user.json missing required fields: {missing_fields}"
        )

    return user


def _load_and_validate_schema_version(
    mock_data_dir: Path,
) -> Dict[str, Any]:
    """Load and validate schema_version.json."""
    version_file = mock_data_dir / "schema_version.json"

    if not version_file.exists():
        raise MockDataValidationError(
            f"Mock schema version file not found: {version_file}"
        )

    try:
        with open(version_file, "r") as f:
            version = json.load(f)
    except json.JSONDecodeError as e:
        raise MockDataValidationError(
            f"Invalid JSON in {version_file}: {e}"
        )
    except IOError as e:
        raise MockDataValidationError(
            f"Cannot read {version_file}: {e}"
        )

    if not isinstance(version, dict):
        raise MockDataValidationError(
            f"schema_version.json must contain a JSON object, got {type(version).__name__}"
        )

    # Validate required version fields
    required_fields = {"version", "api_version"}
    missing_fields = required_fields - set(version.keys())
    if missing_fields:
        raise MockDataValidationError(
            f"schema_version.json missing required fields: {missing_fields}"
        )

    return version
