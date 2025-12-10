# Compass Client API Contract

**Package**: `compass-client`
**Module**: `compass_client`
**Version**: 1.0.0
**Date**: 2025-12-09

## Overview

The `compass-client` package provides a standalone Python client for the Compass Education API. It supports both real API integration and mock data mode for development and testing without requiring Compass credentials.

## Public API

### Module: `compass_client`

#### Exported Symbols

```python
from compass_client import (
    # Factory
    create_client,

    # Client Classes
    CompassClient,
    CompassMockClient,

    # Models
    CompassEvent,
    CompassUser,
    CalendarEventLocation,
    CalendarEventManager,

    # Parser
    CompassParser,

    # Exceptions
    CompassClientError,
    CompassAuthenticationError,
    CompassParseError,
)
```

---

## Classes

### 1. CompassClient

**Purpose**: Real HTTP client for Compass Education API.

**Constructor**:

```python
def __init__(
    self,
    base_url: str,
    username: str,
    password: str
) -> None
```

**Parameters**:
- `base_url` (str): Base URL of Compass instance (e.g., `"https://school.compass.education"`)
- `username` (str): Compass username
- `password` (str): Compass password

**Attributes**:
- `base_url` (str): Normalized base URL (trailing slash removed)
- `username` (str): Username
- `password` (str): Password (not stored in plaintext after auth)
- `session` (requests.Session): HTTP session with cookies
- `user_id` (Optional[int]): Authenticated user's Compass ID
- `school_config_key` (Optional[str]): School-specific config key
- `_authenticated` (bool): Authentication state

**Methods**:

#### `login() -> bool`

Authenticates with Compass API using form-based login.

**Returns**: `True` if authentication succeeds

**Raises**:
- `CompassAuthenticationError`: Invalid credentials or authentication failure
- `CompassClientError`: Network error or server unavailable

**Side Effects**:
- Sets `_authenticated = True`
- Populates `user_id` and `school_config_key` if found in response
- Stores session cookies in `self.session`

**Example**:

```python
client = CompassClient(
    base_url="https://school.compass.education",
    username="parent@example.com",
    password="secure_password"
)
client.login()  # Returns True on success
```

---

#### `get_user_details(target_user_id: Optional[int] = None) -> Dict[str, Any]`

Fetches detailed user information from Compass.

**Parameters**:
- `target_user_id` (Optional[int]): User ID to fetch. Defaults to authenticated user.

**Returns**: Dictionary with user details (raw API response). See [User Details Schema](#user-details-schema).

**Raises**:
- `CompassClientError`: Not authenticated, network error, or invalid response
- `ValueError`: Invalid user ID

**Pre-conditions**:
- `login()` must have been called successfully
- `_authenticated` must be `True`

**Example**:

```python
user_data = client.get_user_details()
print(user_data["userFullName"])  # "Jane Smith"
print(user_data["userEmail"])     # "jane.smith@example.com"
```

---

#### `get_calendar_events(start_date: str, end_date: str, limit: int = 100) -> List[Dict[str, Any]]`

Fetches calendar events from Compass for a date range.

**Parameters**:
- `start_date` (str): Start date in `YYYY-MM-DD` format
- `end_date` (str): End date in `YYYY-MM-DD` format
- `limit` (int): Maximum number of events to return (default: 100)

**Returns**: List of event dictionaries (raw API response). See [Event Schema](#event-schema).

**Raises**:
- `CompassClientError`: Not authenticated, network error, or invalid response
- `ValueError`: Invalid date format

**Pre-conditions**:
- `login()` must have been called successfully
- `_authenticated` must be `True`
- Dates must be in `YYYY-MM-DD` format

**Example**:

```python
events = client.get_calendar_events("2025-12-01", "2025-12-31")
for event in events:
    print(f"{event['title']} at {event['start']}")
```

---

#### `close() -> None`

Closes the HTTP session and releases resources.

**Returns**: None

**Side Effects**: Closes `requests.Session` and releases network resources

**Example**:

```python
client.close()
```

**Best Practice**: Use context manager pattern (future enhancement):

```python
# Future API (not yet implemented)
with CompassClient(...) as client:
    client.login()
    events = client.get_calendar_events(...)
# Automatically closes
```

---

### 2. CompassMockClient

**Purpose**: Mock client returning realistic sample data without requiring Compass credentials.

**Constructor**:

```python
def __init__(
    self,
    base_url: str,
    username: str,
    password: str
) -> None
```

**Parameters**: Same as `CompassClient` (for interface compatibility, not used)

**Attributes**:
- `base_url` (str): Mock URL (not used)
- `username` (str): Mock username (not used)
- `password` (str): Mock password (not used)
- `user_id` (int): Hardcoded mock user ID (e.g., 12345)
- `_authenticated` (bool): Authentication state
- `_events` (List[Dict]): Loaded mock calendar events
- `_user` (Dict): Loaded mock user details

**Methods**:

#### `login() -> bool`

Mock authentication (always succeeds).

**Returns**: `True`

**Raises**: Never raises (for simplicity in testing)

**Side Effects**: Sets `_authenticated = True`

**Example**:

```python
mock_client = CompassMockClient("", "", "")
mock_client.login()  # Always returns True
```

---

#### `get_user_details(target_user_id: Optional[int] = None) -> Dict[str, Any]`

Returns mock user details from `data/mock/compass_user.json`.

**Parameters**:
- `target_user_id` (Optional[int]): Ignored (mock returns same user)

**Returns**: Dictionary with mock user details

**Raises**:
- `CompassClientError`: Not authenticated (must call `login()` first)

**Data Source**:
1. Loads from `data/mock/compass_user.json` if available
2. Falls back to hardcoded synthetic user if file missing/invalid

**Example**:

```python
user_data = mock_client.get_user_details()
# Returns realistic mock data matching CompassUser schema
```

---

#### `get_calendar_events(start_date: str, end_date: str, limit: int = 100) -> List[Dict[str, Any]]`

Returns filtered mock events from `data/mock/compass_events.json`.

**Parameters**: Same as `CompassClient.get_calendar_events()`

**Returns**: List of mock events filtered by date range and limited by count

**Raises**:
- `CompassClientError`: Not authenticated (must call `login()` first)

**Data Source**:
1. Loads from `data/mock/compass_events.json` if available
2. Falls back to hardcoded synthetic events if file missing/invalid

**Filtering**: Events are filtered to match the date range (same behavior as real client)

**Example**:

```python
events = mock_client.get_calendar_events("2025-12-01", "2025-12-31", limit=50)
# Returns up to 50 mock events within date range
```

---

#### `close() -> None`

No-op (maintains interface parity).

**Returns**: None

---

### 3. CompassParser

**Purpose**: Generic parser for transforming raw API dictionaries into validated Pydantic models.

**Methods**:

#### `parse(model: Type[T], raw: Dict[str, Any] | List[Dict[str, Any]]) -> T | List[T]`

Generic parsing method that validates raw data into Pydantic models.

**Type Parameters**:
- `T`: Generic type bound to `BaseModel` (any Pydantic model)

**Parameters**:
- `model` (Type[T]): Pydantic model class to parse into
- `raw` (Dict | List[Dict]): Raw data from API (single object or list)

**Returns**:
- Single model instance if `raw` is a dict
- List of model instances if `raw` is a list

**Raises**:
- `CompassParseError`: Validation fails for any item

**Example**:

```python
from compass_client import CompassParser, CompassEvent, CompassUser

# Parse single object
raw_user = client.get_user_details()
user = CompassParser.parse(CompassUser, raw_user)
print(user.user_full_name)  # Type-safe access

# Parse list of objects
raw_events = client.get_calendar_events("2025-12-01", "2025-12-31")
events = CompassParser.parse(CompassEvent, raw_events)
for event in events:
    print(f"{event.title} at {event.start}")  # Type-safe access
```

---

#### `parse_safe(model: Type[T], raw_list: List[Dict[str, Any]], skip_invalid: bool = True) -> Tuple[List[T], List[CompassParseError]]`

Safe parsing that collects errors instead of failing fast.

**Parameters**:
- `model` (Type[T]): Pydantic model class to parse into
- `raw_list` (List[Dict]): List of raw dictionaries from API
- `skip_invalid` (bool): Whether to skip invalid items (default: True)

**Returns**: Tuple of `(valid_items, errors)`
- `valid_items` (List[T]): Successfully parsed model instances
- `errors` (List[CompassParseError]): Parse errors for failed items

**Example**:

```python
raw_events = client.get_calendar_events("2025-12-01", "2025-12-31")
events, errors = CompassParser.parse_safe(CompassEvent, raw_events)

print(f"Successfully parsed {len(events)} events")
print(f"Failed to parse {len(errors)} events")

for error in errors:
    print(f"Error: {error}")
    print(f"Invalid data: {error.raw_data}")
```

---

## Models

### 4. CompassEvent

**Purpose**: Validated model for Compass calendar events.

**Type**: Pydantic `BaseModel`

**Key Fields** (37 total, see [Event Schema](#event-schema) for complete list):

```python
class CompassEvent(BaseModel):
    activity_id: int                   # Unique activity ID
    title: str                         # Event title
    long_title: str                    # Full title with time prefix
    long_title_without_time: str       # Title without time prefix
    description: str                   # Event description
    start: datetime                    # Start datetime (ISO 8601)
    finish: datetime                   # End datetime (ISO 8601)
    all_day: bool                      # Whether event is all-day
    location: Optional[str]            # Location string
    locations: Optional[List[CalendarEventLocation]]  # Structured locations
    managers: Optional[List[CalendarEventManager]]    # Event managers
    instance_id: str                   # Event instance UUID
    guid: str                          # Global unique identifier
    is_recurring: bool                 # Whether event recurs
    attendee_user_id: int              # Attendee's user ID
    background_color: str              # Event color (hex)
    # ... 21 more fields
```

**Field Aliases**: Supports both `camelCase` (API) and `snake_case` (Python)

**Example**:

```python
event = CompassEvent.model_validate({
    "activityId": 123456,
    "title": "Year 8 Science Excursion",
    "start": "2025-12-15T09:00:00+11:00",
    "finish": "2025-12-15T15:00:00+11:00",
    # ... other fields
})

print(event.activity_id)  # 123456 (snake_case access)
print(event.title)        # "Year 8 Science Excursion"
```

---

### 5. CompassUser

**Purpose**: Validated model for Compass user details.

**Type**: Pydantic `BaseModel`

**Key Fields** (40 total, see [User Details Schema](#user-details-schema) for complete list):

```python
class CompassUser(BaseModel):
    user_id: int                       # Compass user ID
    user_first_name: str               # First name
    user_last_name: str                # Last name
    user_preferred_name: str           # Preferred first name
    user_full_name: str                # Full name
    user_email: str                    # Email address
    user_display_code: str             # School identifier (e.g., "ABC-0000")
    user_compass_person_id: str        # Person UUID
    user_year_level: Optional[str]     # Year level (e.g., "8")
    user_form_group: Optional[str]     # Form group
    user_house: Optional[str]          # House name
    user_role: int                     # User role (e.g., 3 for parent)
    age: Optional[int]                 # User's age
    birthday: Optional[datetime]       # Date of birth
    gender: Optional[str]              # Gender
    user_photo_path: str               # Photo URL path
    # ... 24 more fields
```

**Field Aliases**: Supports both `camelCase` (API) and `snake_case` (Python)

**Example**:

```python
user = CompassUser.model_validate({
    "userId": 12345,
    "userFirstName": "Jane",
    "userLastName": "Smith",
    "userEmail": "jane.smith@example.com",
    # ... other fields
})

print(user.user_full_name)  # "Jane Smith" (snake_case access)
print(user.user_email)      # "jane.smith@example.com"
```

---

## Factory Function

### 6. create_client()

**Purpose**: Factory function that creates appropriate client based on configuration mode.

**Signature**:

```python
def create_client(
    base_url: str,
    username: str,
    password: str,
    mode: Optional[str] = None
) -> CompassClient | CompassMockClient
```

**Parameters**:
- `base_url` (str): Compass instance URL
- `username` (str): Username
- `password` (str): Password
- `mode` (Optional[str]): Mode string: `"real"` or `"mock"`. If `None`, reads from `COMPASS_MODE` environment variable (default: `"real"`)

**Returns**:
- `CompassClient` instance if mode is `"real"`
- `CompassMockClient` instance if mode is `"mock"`

**Raises**:
- `ValueError`: Invalid mode (not "real" or "mock")

**Environment Variables**:
- `COMPASS_MODE`: Mode selection (`"real"` or `"mock"`, case-insensitive)

**Configuration Precedence**:
1. Explicit `mode` parameter (highest priority)
2. `COMPASS_MODE` environment variable
3. Default value `"real"` (lowest priority)

**Example**:

```python
import os
from compass_client import create_client

# Explicit mode
client = create_client(
    base_url="https://school.compass.education",
    username="parent@example.com",
    password="password",
    mode="mock"  # Explicitly use mock mode
)

# Mode from environment variable
os.environ["COMPASS_MODE"] = "mock"
client = create_client(
    base_url="https://school.compass.education",
    username="parent@example.com",
    password="password"
    # mode=None reads from COMPASS_MODE env var
)

# Default to real mode
client = create_client(
    base_url="https://school.compass.education",
    username="parent@example.com",
    password="password"
    # No mode parameter, COMPASS_MODE not set → defaults to "real"
)
```

---

## Exceptions

### 7. CompassClientError

**Base exception for all Compass client errors.**

**Hierarchy**:

```
Exception
└── CompassClientError
    ├── CompassAuthenticationError
    └── CompassParseError
```

**Attributes**:
- `message` (str): Human-readable error message

**Example**:

```python
try:
    client.get_user_details()
except CompassClientError as e:
    print(f"Compass error: {e}")
```

---

### 8. CompassAuthenticationError

**Raised when authentication fails.**

**Inherits From**: `CompassClientError`

**Common Causes**:
- Invalid credentials
- Network error during login
- Compass server unavailable
- Session expired

**Example**:

```python
try:
    client.login()
except CompassAuthenticationError as e:
    print(f"Authentication failed: {e}")
```

---

### 9. CompassParseError

**Raised when parsing/validation fails.**

**Inherits From**: `CompassClientError`

**Attributes**:
- `message` (str): Human-readable error message
- `raw_data` (Any): The raw data that failed to parse
- `validation_errors` (Optional[List[Any]]): Pydantic validation errors

**Example**:

```python
from compass_client import CompassParser, CompassEvent, CompassParseError

try:
    events = CompassParser.parse(CompassEvent, raw_events)
except CompassParseError as e:
    print(f"Parse error: {e}")
    print(f"Invalid data: {e.raw_data}")
    print(f"Validation errors: {e.validation_errors}")
```

---

## Schemas

### Event Schema

**Raw API Response** (Dict returned by clients):

```json
{
  "__type": "CalendarTransport:http://jdlf.com.au/ns/data/calendar",
  "activityId": 123456,
  "title": "Year 8 Science Excursion",
  "longTitle": "09:00 - Year 8 Science Excursion",
  "longTitleWithoutTime": "Year 8 Science Excursion",
  "description": "Museum of Science and Industry. Bring lunch.",
  "start": "2025-12-15T09:00:00+11:00",
  "finish": "2025-12-15T15:00:00+11:00",
  "allDay": false,
  "location": "Museum of Science",
  "locations": [
    {
      "__type": "CalendarEventLocation:http://jdlf.com.au/ns/data/calendar",
      "locationId": 789,
      "locationName": "Museum of Science"
    }
  ],
  "managers": [
    {
      "__type": "CalendarEventManager:http://jdlf.com.au/ns/data/calendar",
      "managerUserId": 101,
      "managerImportIdentifier": "teacher1@school.edu"
    }
  ],
  "instanceId": "uuid-123-456",
  "guid": "guid-789-012",
  "isRecurring": false,
  "attendeeUserId": 12345,
  "backgroundColor": "#4CAF50"
}
```

**Pydantic Model** (Type-safe access after parsing):

```python
event: CompassEvent = CompassParser.parse(CompassEvent, raw_event)

event.activity_id        # 123456 (int)
event.title              # "Year 8 Science Excursion" (str)
event.start              # datetime(2025, 12, 15, 9, 0, tzinfo=...) (datetime)
event.all_day            # False (bool)
event.locations[0].location_name  # "Museum of Science" (str)
```

---

### User Details Schema

**Raw API Response** (Dict returned by clients):

```json
{
  "__type": "UserDetailsBlob",
  "userId": 12345,
  "userFirstName": "Jane",
  "userLastName": "Smith",
  "userPreferredName": "Jane",
  "userFullName": "Jane Smith",
  "userEmail": "jane.smith@example.com",
  "userDisplayCode": "JSM-0001",
  "userCompassPersonId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "userYearLevel": "8",
  "userFormGroup": "8A",
  "userHouse": "Blue House",
  "userRole": 4,
  "age": 13,
  "birthday": "2012-03-15T00:00:00+11:00",
  "gender": "Female",
  "userPhotoPath": "/images/default-avatar.png"
}
```

**Pydantic Model** (Type-safe access after parsing):

```python
user: CompassUser = CompassParser.parse(CompassUser, raw_user)

user.user_id             # 12345 (int)
user.user_full_name      # "Jane Smith" (str)
user.user_email          # "jane.smith@example.com" (str)
user.birthday            # datetime(2012, 3, 15, tzinfo=...) (Optional[datetime])
```

---

## Usage Examples

### Basic Usage (Real Mode)

```python
from compass_client import create_client, CompassParser, CompassEvent, CompassUser

# Create client (real mode)
client = create_client(
    base_url="https://school.compass.education",
    username="parent@example.com",
    password="secure_password",
    mode="real"
)

# Authenticate
client.login()

# Fetch raw data
raw_user = client.get_user_details()
raw_events = client.get_calendar_events("2025-12-01", "2025-12-31")

# Parse into validated models
user = CompassParser.parse(CompassUser, raw_user)
events = CompassParser.parse(CompassEvent, raw_events)

# Type-safe access
print(f"Welcome, {user.user_full_name}!")
for event in events:
    print(f"{event.title} on {event.start.strftime('%Y-%m-%d')}")

# Cleanup
client.close()
```

---

### Basic Usage (Mock Mode)

```python
import os
from compass_client import create_client, CompassParser, CompassEvent

# Set mock mode via environment
os.environ["COMPASS_MODE"] = "mock"

# Create client (reads mode from environment)
client = create_client(
    base_url="",  # Ignored in mock mode
    username="",  # Ignored in mock mode
    password=""   # Ignored in mock mode
)

# Mock login (always succeeds)
client.login()

# Fetch mock data
raw_events = client.get_calendar_events("2025-12-01", "2025-12-31")

# Parse into validated models (same as real mode)
events = CompassParser.parse(CompassEvent, raw_events)

# Type-safe access (identical to real mode)
for event in events:
    print(f"{event.title} on {event.start.strftime('%Y-%m-%d')}")
```

---

### Safe Parsing with Error Handling

```python
from compass_client import create_client, CompassParser, CompassEvent

client = create_client(...)
client.login()

raw_events = client.get_calendar_events("2025-12-01", "2025-12-31")

# Parse with error collection
events, errors = CompassParser.parse_safe(CompassEvent, raw_events)

print(f"Successfully parsed {len(events)} events")
print(f"Failed to parse {len(errors)} events")

# Handle errors
for error in errors:
    print(f"Validation error: {error}")
    print(f"Invalid data: {error.raw_data}")

    # Log to monitoring system
    logger.error("Parse error", extra={
        "raw_data": error.raw_data,
        "validation_errors": error.validation_errors
    })
```

---

## Versioning and Compatibility

**Semantic Versioning**: This package follows [SemVer 2.0.0](https://semver.org/)

- **Major version**: Breaking API changes (e.g., method signature changes, removed methods)
- **Minor version**: Backward-compatible new features (e.g., new optional parameters, new methods)
- **Patch version**: Backward-compatible bug fixes

**Current Version**: 1.0.0

**Compatibility Policy**:
- Mock data schema changes increment mock data version (see `schema_version.json`)
- Package API changes increment package version
- New Compass API fields are backward-compatible (Pydantic ignores extra fields)

---

## Testing

### Contract Testing

Consumers can verify interface compliance using parametrized tests:

```python
import pytest
from compass_client import CompassClient, CompassMockClient

@pytest.mark.parametrize("client_class", [CompassClient, CompassMockClient])
def test_client_interface(client_class):
    """Verify both clients implement same interface."""
    client = client_class("", "", "")

    # Verify methods exist
    assert callable(client.login)
    assert callable(client.get_user_details)
    assert callable(client.get_calendar_events)
    assert callable(client.close)

    # Verify attributes
    assert hasattr(client, "base_url")
    assert hasattr(client, "username")
    assert hasattr(client, "password")
    assert hasattr(client, "_authenticated")
```

---

## Migration Guide

### Migrating from Bellweaver Monolith

**Old Import** (monolithic):

```python
from bellweaver.adapters.compass import CompassClient
from bellweaver.adapters.compass_mock import CompassMockClient
from bellweaver.models.compass import CompassEvent, CompassUser
from bellweaver.parsers.compass import CompassParser
```

**New Import** (decoupled package):

```python
from compass_client import (
    create_client,
    CompassClient,
    CompassMockClient,
    CompassEvent,
    CompassUser,
    CompassParser,
)
```

**Factory Pattern** (recommended):

```python
# Old: Manual client selection
if os.getenv("USE_MOCK") == "true":
    client = CompassMockClient(...)
else:
    client = CompassClient(...)

# New: Automatic mode detection
client = create_client(...)  # Reads COMPASS_MODE env var
```

---

## Document Metadata

- **Created**: 2025-12-09
- **Feature**: 002-compass-api-decoupling
- **Package Version**: 1.0.0
- **Related Documents**:
  - [client-interface.md](./client-interface.md) - Interface protocol
  - [factory-contract.md](./factory-contract.md) - Factory function contract
  - [mock-data-schema.json](./mock-data-schema.json) - Mock data JSON schema
