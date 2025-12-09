"""
Factory for creating Compass client instances.

Provides a simple way to create the appropriate client (real or mock)
based on configuration or environment variables.
"""

import os
from typing import Optional, Union

from .client import CompassClient
from .mock_client import CompassMockClient


def create_client(
    base_url: str,
    username: str,
    password: str,
    mode: Optional[str] = None,
) -> Union[CompassClient, CompassMockClient]:
    """
    Create a Compass client instance.

    The client type is determined by the mode parameter, which can be:
    - "real": Use the real Compass API client
    - "mock": Use the mock client with sample data

    Mode is determined by (in order of precedence):
    1. Explicit `mode` parameter
    2. COMPASS_MODE environment variable
    3. Default: "real"

    Args:
        base_url: Base URL of Compass instance (e.g., "https://compass.example.com")
        username: Compass username
        password: Compass password
        mode: Client mode: "real" or "mock" (optional)

    Returns:
        CompassClient for real mode, CompassMockClient for mock mode

    Raises:
        ValueError: If mode is not "real" or "mock"

    Example:
        >>> # Use environment variable (COMPASS_MODE=mock)
        >>> client = create_client(base_url, username, password)
        >>>
        >>> # Explicitly use mock mode
        >>> client = create_client(base_url, username, password, mode="mock")
        >>>
        >>> # Use real mode
        >>> client = create_client(base_url, username, password, mode="real")
    """
    effective_mode = mode or os.getenv("COMPASS_MODE", "real")
    effective_mode = effective_mode.lower().strip()

    if effective_mode == "mock":
        return CompassMockClient(base_url, username, password)
    elif effective_mode == "real":
        return CompassClient(base_url, username, password)
    else:
        raise ValueError(
            f"Invalid COMPASS_MODE: '{effective_mode}'. Must be 'real' or 'mock'."
        )
