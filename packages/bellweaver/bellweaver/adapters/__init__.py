"""Adapters for connecting to external calendar sources.

CompassClient and CompassMockClient are now provided by the compass_client package.
Import them directly from compass_client:

    from compass_client import create_client, CompassClient, CompassMockClient

This module re-exports for backward compatibility only.
"""

# Re-export from compass_client for backward compatibility
from compass_client import CompassClient, CompassMockClient, create_client

# Keep mock_data for now (used by CLI)
from .mock_data import collect_compass_data

__all__ = ["CompassClient", "CompassMockClient", "create_client", "collect_compass_data"]
