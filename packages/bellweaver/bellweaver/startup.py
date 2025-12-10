"""
Startup validation for Bellweaver application.

Performs runtime checks based on configured Compass mode to ensure
the application can function properly before handling requests.
"""

import os
from pathlib import Path # Add Path import
from typing import Optional

from compass_client.mock_validator import (
    MockDataValidationError,
    validate_mock_data_schema,
)


class StartupValidationError(Exception):
    """Raised when startup validation fails."""

    pass


def startup_checks(compass_mode: Optional[str] = None) -> None:
    """
    Run startup validation checks based on Compass mode.

    Validates mock data if running in mock mode. Does nothing for real mode.

    Args:
        compass_mode: Compass mode ('mock' or 'real'). If None, reads from COMPASS_MODE env var.

    Raises:
        StartupValidationError: If validation fails.
    """
    if compass_mode is None:
        compass_mode = os.getenv("COMPASS_MODE", "real")

    if compass_mode == "mock":
        validate_mock_data_startup()
    elif compass_mode not in ("real", "mock"):
        raise StartupValidationError(
            f"Invalid COMPASS_MODE '{compass_mode}'. Must be 'real' or 'mock'."
        )


def validate_mock_data_startup() -> None:
    """
    Validate mock data at startup when running in mock mode.

    Ensures all required mock data files exist and are valid before
    the application starts accepting requests.

    Raises:
        StartupValidationError: If mock data validation fails.
    """
    # Explicitly define mock data path for Docker environment
    mock_data_path = Path("/app/packages/compass-client/data/mock")
    try:
        validate_mock_data_schema(mock_data_path) # Pass the explicit path
    except MockDataValidationError as e:
        raise StartupValidationError(
            f"Mock data validation failed: {e}"
        ) from e
