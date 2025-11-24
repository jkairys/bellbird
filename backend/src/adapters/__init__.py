"""Adapters for connecting to external calendar sources."""

from .compass import CompassClient
from .compass_mock import CompassMockClient

__all__ = ["CompassClient", "CompassMockClient"]
