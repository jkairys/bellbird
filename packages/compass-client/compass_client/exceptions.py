"""Exceptions for the Compass client library."""

from typing import Any, List, Optional


class CompassClientError(Exception):
    """Base exception for Compass client errors."""

    pass


class CompassAuthenticationError(CompassClientError):
    """Raised when authentication with Compass fails."""

    pass


class CompassParseError(CompassClientError):
    """Raised when parsing Compass API response fails."""

    def __init__(
        self,
        message: str,
        raw_data: Any = None,
        validation_errors: Optional[List[Any]] = None,
    ):
        """
        Initialize parse error with context.

        Args:
            message: Human-readable error message
            raw_data: The raw data that failed to parse
            validation_errors: Pydantic validation errors if available
        """
        super().__init__(message)
        self.raw_data = raw_data
        self.validation_errors = validation_errors
