"""
Parser for Compass API responses.

This module provides a parsing layer between raw API responses (dicts) and
validated Pydantic models. It separates concerns:
- Adapters handle HTTP communication and return raw dicts
- Parsers handle validation and transformation into domain models
- Application code works with type-safe, validated models

Example usage:
    >>> from compass_client import CompassClient, CompassParser, CompassEvent, CompassUser
    >>>
    >>> client = CompassClient(base_url, username, password)
    >>> client.login()
    >>>
    >>> # Get raw data from client
    >>> raw_events = client.get_calendar_events("2025-01-01", "2025-01-31")
    >>>
    >>> # Parse into validated models using generic method
    >>> events = CompassParser.parse(CompassEvent, raw_events)
    >>> for event in events:
    ...     print(f"{event.title} at {event.start}")
    >>>
    >>> # Parse user details
    >>> raw_user = client.get_user_details()
    >>> user = CompassParser.parse(CompassUser, raw_user)
    >>> print(user.user_full_name)
"""

from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel, ValidationError

from .exceptions import CompassParseError

T = TypeVar("T", bound=BaseModel)


class CompassParser:
    """
    Parser for Compass Education API responses.

    Transforms raw API responses (dicts) into validated Pydantic models using generics.
    Provides clear separation between HTTP communication and data validation.

    This parser uses Python generics (TypeVar) to provide a single, scalable interface
    for parsing any Pydantic model, rather than having separate methods for each model type.
    """

    @staticmethod
    def parse(model: Type[T], raw: Dict[str, Any] | List[Dict[str, Any]]) -> T | List[T]:
        """
        Parse and validate raw data into a Pydantic model.

        This is a generic method that works with any Pydantic model type.
        Automatically detects whether raw data is a single dict or a list.

        Args:
            model: The Pydantic model class to parse into
            raw: Raw data from API (single dict or list of dicts)

        Returns:
            Validated model instance or list of instances (type matches input)

        Raises:
            CompassParseError: If validation fails

        Example:
            >>> from compass_client import CompassEvent, CompassUser
            >>> # Parse single object
            >>> event = CompassParser.parse(CompassEvent, raw_event_dict)
            >>> # Parse list of objects
            >>> events = CompassParser.parse(CompassEvent, raw_events_list)
            >>> user = CompassParser.parse(CompassUser, raw_user_dict)
        """
        if isinstance(raw, list):
            return CompassParser._parse_list(model, raw)
        else:
            return CompassParser._parse_single(model, raw)

    @staticmethod
    def _parse_single(model: Type[T], raw: Dict[str, Any]) -> T:
        """
        Parse a single object.

        Args:
            model: The Pydantic model class to parse into
            raw: Raw dictionary from API

        Returns:
            Validated model instance

        Raises:
            CompassParseError: If validation fails
        """
        try:
            return model.model_validate(raw)
        except ValidationError as e:
            raise CompassParseError(
                f"Failed to parse {model.__name__}: {e.error_count()} validation error(s)",
                raw_data=raw,
                validation_errors=e.errors(),
            ) from e

    @staticmethod
    def _parse_list(model: Type[T], raw_list: List[Dict[str, Any]]) -> List[T]:
        """
        Parse a list of objects (strict mode - fails on first error).

        Args:
            model: The Pydantic model class to parse into
            raw_list: List of raw dictionaries from API

        Returns:
            List of validated model instances

        Raises:
            CompassParseError: If any item fails validation

        Note:
            Stops at first validation error. For partial parsing with error handling,
            use parse_safe() instead.
        """
        try:
            return [model.model_validate(item) for item in raw_list]
        except ValidationError as e:
            for idx, item in enumerate(raw_list):
                try:
                    model.model_validate(item)
                except ValidationError:
                    raise CompassParseError(
                        f"Failed to parse {model.__name__} at index {idx}: {e.error_count()} validation error(s)",
                        raw_data=item,
                        validation_errors=e.errors(),
                    ) from e
            raise CompassParseError(
                f"Failed to parse {model.__name__} list: {e.error_count()} validation error(s)",
                raw_data=raw_list,
                validation_errors=e.errors(),
            ) from e

    @staticmethod
    def parse_safe(
        model: Type[T], raw_list: List[Dict[str, Any]], skip_invalid: bool = True
    ) -> tuple[List[T], List[CompassParseError]]:
        """
        Parse a list with error handling for individual items (safe mode).

        Args:
            model: The Pydantic model class to parse into
            raw_list: List of raw dictionaries from API
            skip_invalid: If True, skip invalid items and continue parsing.
                         If False, collect errors but parse all valid items.

        Returns:
            Tuple of (valid_items, errors):
                - valid_items: List of successfully parsed model instances
                - errors: List of CompassParseError for failed items

        Example:
            >>> events, errors = CompassParser.parse_safe(CompassEvent, raw_events)
            >>> print(f"Parsed {len(events)} events, {len(errors)} failed")
            >>> for error in errors:
            ...     print(f"Error: {error}")
        """
        valid_items: List[T] = []
        errors: List[CompassParseError] = []

        for idx, raw_item in enumerate(raw_list):
            try:
                item = model.model_validate(raw_item)
                valid_items.append(item)
            except ValidationError as e:
                error = CompassParseError(
                    f"Failed to parse {model.__name__} at index {idx}: {e.error_count()} validation error(s)",
                    raw_data=raw_item,
                    validation_errors=e.errors(),
                )
                errors.append(error)
                if not skip_invalid:
                    continue

        return valid_items, errors
