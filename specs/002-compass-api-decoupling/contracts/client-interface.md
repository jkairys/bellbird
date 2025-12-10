# Compass Client Interface Contract

**Package**: `compass-client`
**Version**: 1.0.0
**Date**: 2025-12-09

## Overview

This document defines the protocol/interface that all Compass client implementations must adhere to. Both `CompassClient` (real API) and `CompassMockClient` (mock data) must implement this interface to ensure behavioral parity and interchangeability.

## Design Principles

1. **Interface Parity**: Both clients must have identical public APIs
2. **Substitutability**: Clients must be interchangeable without code changes
3. **Duck Typing**: Python duck typing ensures interface compliance without formal protocols (may add `Protocol` in future)
4. **Fail-Fast**: Violations of pre-conditions raise exceptions immediately
5. **Consistency**: Same behavior across both implementations where possible

---

## CompassClientProtocol

**Status**: Informal interface (duck typing). Formal `typing.Protocol` may be added in future.

### Required Methods

All Compass client implementations MUST provide these methods with exact signatures:

#### 1. `__init__(base_url: str, username: str, password: str) -> None`

**Purpose**: Initialize client with connection parameters.

**Parameters**:
- `base_url` (str): Base URL of Compass instance (e.g., `"https://school.compass.education"`)
- `username` (str): Username for authentication
- `password` (str): Password for authentication

**Post-conditions**:
- Client is in **Created** state
- `base_url`, `username`, `password` are stored as attributes
- `_authenticated` is `False`
- No network calls made

**Contract**:
- MUST accept these three parameters
- MUST NOT perform authentication in constructor
- MUST store parameters for later use
- MUST initialize `_authenticated = False`

**Implementation Notes**:
- **Real Client**: Stores actual credentials, creates `requests.Session`
- **Mock Client**: Stores credentials (not used), loads mock data files

---

#### 2. `login() -> bool`

**Purpose**: Authenticate with Compass (or simulate authentication).

**Parameters**: None

**Returns**: `bool`
- `True` if authentication succeeds
- MUST NOT return `False` (raise exception instead)

**Raises**:
- `CompassAuthenticationError`: Authentication failure (real client only)
- `CompassClientError`: Network error or server unavailable (real client only)
- Mock client MUST NOT raise exceptions (always succeeds)

**Pre-conditions**:
- Client must be in **Created** or **Closed** state (not already authenticated)

**Post-conditions**:
- Client transitions to **Authenticated** state
- `_authenticated` is set to `True`
- Session metadata extracted (real client: `user_id`, `school_config_key`)
- Ready to call data fetching methods

**State Transition**:
```
[Created] --login()--> [Authenticated]
```

**Contract**:
- MUST set `_authenticated = True` on success
- MUST raise exception on failure (real client)
- MUST return `True` (never `False`)
- Mock client MUST always succeed (no exceptions)

**Interface Parity**:
- Both clients MUST have identical signature
- Both clients MUST return `True` on success
- Mock client simulates success without network calls

**Implementation Notes**:
- **Real Client**: HTTP form POST, cookie handling, metadata extraction
- **Mock Client**: Sets `_authenticated = True`, no network activity

**Example**:

```python
client = CompassClient(...)  # Or CompassMockClient
success = client.login()
assert success is True
assert client._authenticated is True
```

---

#### 3. `get_user_details(target_user_id: Optional[int] = None) -> Dict[str, Any]`

**Purpose**: Fetch user details for specified user (or authenticated user).

**Parameters**:
- `target_user_id` (Optional[int]): User ID to fetch. If `None`, fetch authenticated user's details.

**Returns**: `Dict[str, Any]`
- Dictionary containing user details
- MUST match schema defined by `CompassUser` Pydantic model
- MAY contain extra fields (Pydantic ignores them)

**Raises**:
- `CompassClientError`: Not authenticated, network error, or invalid response

**Pre-conditions**:
- Client MUST be in **Authenticated** state
- `_authenticated` MUST be `True`
- MUST call `login()` before this method

**Post-conditions**:
- Returns valid user details dictionary
- No state change (remains in **Authenticated** state)

**State Transition**:
```
[Authenticated] --get_user_details()--> [Authenticated] (no change)
```

**Contract**:
- MUST raise exception if not authenticated
- MUST return dictionary (never `None` or empty)
- Returned dictionary MUST validate against `CompassUser` model (parseable)
- MUST accept `Optional[int]` parameter (even if mock ignores it)

**Interface Parity**:
- Both clients MUST have identical signature
- Both clients MUST return dictionary matching `CompassUser` schema
- Mock client MAY ignore `target_user_id` (returns same mock user)

**Implementation Notes**:
- **Real Client**: HTTP POST to `/Services/User.svc/GetUserDetailsBlobByUserId`
- **Mock Client**: Returns data from `data/mock/compass_user.json` or fallback

**Example**:

```python
client.login()
user_data = client.get_user_details()
assert isinstance(user_data, dict)
assert "userId" in user_data
assert "userFullName" in user_data

# Must be parseable by CompassParser
from compass_client import CompassParser, CompassUser
user = CompassParser.parse(CompassUser, user_data)  # Must not raise
```

---

#### 4. `get_calendar_events(start_date: str, end_date: str, limit: int = 100) -> List[Dict[str, Any]]`

**Purpose**: Fetch calendar events within date range.

**Parameters**:
- `start_date` (str): Start date in `YYYY-MM-DD` format
- `end_date` (str): End date in `YYYY-MM-DD` format
- `limit` (int): Maximum number of events to return (default: 100)

**Returns**: `List[Dict[str, Any]]`
- List of event dictionaries
- Each dictionary MUST match schema defined by `CompassEvent` Pydantic model
- MAY return empty list if no events in range
- MUST respect `limit` parameter (return at most `limit` events)

**Raises**:
- `CompassClientError`: Not authenticated, network error, or invalid response
- `ValueError`: Invalid date format (both clients)

**Pre-conditions**:
- Client MUST be in **Authenticated** state
- `_authenticated` MUST be `True`
- MUST call `login()` before this method
- Dates MUST be in `YYYY-MM-DD` format

**Post-conditions**:
- Returns list of events (may be empty)
- No state change (remains in **Authenticated** state)

**State Transition**:
```
[Authenticated] --get_calendar_events()--> [Authenticated] (no change)
```

**Contract**:
- MUST raise exception if not authenticated
- MUST return list (never `None`)
- List MAY be empty (valid response)
- Each item MUST be a dictionary
- Each dictionary MUST validate against `CompassEvent` model (parseable)
- MUST filter events by date range
- MUST respect `limit` parameter

**Interface Parity**:
- Both clients MUST have identical signature
- Both clients MUST return list of dictionaries matching `CompassEvent` schema
- Both clients MUST filter by date range
- Both clients MUST respect `limit` parameter

**Implementation Notes**:
- **Real Client**: HTTP POST to `/Services/Calendar.svc/GetCalendarEventsByUser`
- **Mock Client**: Returns filtered data from `data/mock/compass_events.json`

**Example**:

```python
client.login()
events = client.get_calendar_events("2025-12-01", "2025-12-31", limit=50)
assert isinstance(events, list)
assert len(events) <= 50

# Each event must be parseable by CompassParser
from compass_client import CompassParser, CompassEvent
parsed_events = CompassParser.parse(CompassEvent, events)  # Must not raise
```

---

#### 5. `close() -> None`

**Purpose**: Release resources and close session.

**Parameters**: None

**Returns**: `None`

**Raises**: Never raises exceptions

**Pre-conditions**: None (can be called in any state)

**Post-conditions**:
- Client transitions to **Closed** state
- Resources released (real client: HTTP session closed)
- Subsequent API calls SHOULD fail (not enforced in v1.0)

**State Transition**:
```
[Any State] --close()--> [Closed]
```

**Contract**:
- MUST be idempotent (safe to call multiple times)
- MUST NOT raise exceptions
- MUST release resources (real client)

**Interface Parity**:
- Both clients MUST have identical signature
- Real client releases HTTP session
- Mock client is no-op (maintains interface parity)

**Implementation Notes**:
- **Real Client**: Calls `self.session.close()`
- **Mock Client**: No-op (nothing to close)

**Example**:

```python
client.close()
client.close()  # Idempotent - safe to call again
```

---

### Required Attributes

All Compass client implementations MUST provide these attributes:

#### 1. `base_url: str`

**Purpose**: Store Compass instance URL

**Type**: `str`

**Contract**:
- MUST be set in `__init__()`
- Real client SHOULD normalize (strip trailing slash)
- Mock client MAY store as-is (not used)

---

#### 2. `username: str`

**Purpose**: Store username for authentication

**Type**: `str`

**Contract**:
- MUST be set in `__init__()`
- Real client uses for login
- Mock client stores but doesn't use

---

#### 3. `password: str`

**Purpose**: Store password for authentication

**Type**: `str`

**Contract**:
- MUST be set in `__init__()`
- Real client uses for login
- Mock client stores but doesn't use

---

#### 4. `user_id: Optional[int]`

**Purpose**: Store authenticated user's Compass ID

**Type**: `Optional[int]`

**Contract**:
- MUST be `None` before authentication
- MUST be set after successful `login()`
- Real client extracts from session
- Mock client uses hardcoded value (e.g., 12345)

---

#### 5. `_authenticated: bool`

**Purpose**: Track authentication state

**Type**: `bool`

**Contract**:
- MUST be `False` initially
- MUST be set to `True` after successful `login()`
- MUST be checked by data fetching methods (raise if `False`)

---

## Method Contracts

### Pre-conditions and Post-conditions

#### `login()`

**Pre-conditions**:
- NONE (can be called anytime)

**Post-conditions**:
- `_authenticated == True`
- `user_id` is set (real client: extracted from session, mock client: hardcoded)

**Invariants**:
- If method returns successfully, `_authenticated` MUST be `True`

---

#### `get_user_details()`

**Pre-conditions**:
- `_authenticated == True` (MUST call `login()` first)

**Post-conditions**:
- Returns non-empty dictionary
- Dictionary validates against `CompassUser` model

**Invariants**:
- Always returns dictionary (never `None`)
- Dictionary structure matches Compass API schema

---

#### `get_calendar_events()`

**Pre-conditions**:
- `_authenticated == True` (MUST call `login()` first)
- `start_date` is valid `YYYY-MM-DD` format
- `end_date` is valid `YYYY-MM-DD` format
- `limit > 0`

**Post-conditions**:
- Returns list (may be empty)
- List length ≤ `limit`
- Each item validates against `CompassEvent` model
- Events are within `[start_date, end_date]` range

**Invariants**:
- Always returns list (never `None`)
- List items match Compass API schema

---

#### `close()`

**Pre-conditions**:
- NONE (can be called anytime)

**Post-conditions**:
- Resources released (real client)

**Invariants**:
- Idempotent (safe to call multiple times)
- Never raises exceptions

---

## State Machine

Both clients MUST implement this state machine:

```
┌─────────┐
│ Created │ (after __init__)
└────┬────┘
     │ login()
     ↓
┌──────────────┐
│Authenticated │◄──────────┐
└──┬───────────┘           │
   │                       │
   │ get_user_details()    │ (can be called multiple times)
   │ get_calendar_events() │
   ↓                       │
┌──────────────┐           │
│ Data Fetched │───────────┘
└──────┬───────┘
       │ close()
       ↓
   ┌────────┐
   │ Closed │
   └────────┘
```

**States**:

1. **Created**: Instance initialized, no network activity
2. **Authenticated**: Logged in, ready to fetch data
3. **Data Fetched**: Data retrieved (can fetch more)
4. **Closed**: Session closed, resources released

**State Transitions**:

| From State | Method | To State | Notes |
|------------|--------|----------|-------|
| Created | `login()` | Authenticated | MUST succeed (or raise exception) |
| Authenticated | `get_user_details()` | Authenticated | Can repeat |
| Authenticated | `get_calendar_events()` | Authenticated | Can repeat |
| Any State | `close()` | Closed | Idempotent |

---

## Error Handling

### Exception Hierarchy

Both clients MUST use this exception hierarchy:

```
Exception
└── CompassClientError
    ├── CompassAuthenticationError
    └── CompassParseError (not raised by clients, only parser)
```

### Exception Contracts

#### `CompassClientError`

**When to Raise**:
- General client errors
- Network failures (real client)
- Not authenticated when calling data methods

**Contract**:
- Base class for all client exceptions
- MUST include descriptive error message

---

#### `CompassAuthenticationError`

**When to Raise**:
- `login()` fails with invalid credentials (real client)
- Authentication server unreachable (real client)

**Contract**:
- ONLY raised by real client
- Mock client MUST NOT raise this (always succeeds)

---

### Exception Parity

**Real Client**:
- MAY raise `CompassAuthenticationError` on login failure
- MAY raise `CompassClientError` on network errors

**Mock Client**:
- MUST raise `CompassClientError` if data methods called before `login()`
- MUST NOT raise authentication errors (login always succeeds)

---

## Data Contract

### Response Schemas

Both clients MUST return data that validates against these Pydantic models:

#### User Details Response

```python
{
    "__type": "UserDetailsBlob",
    "userId": int,
    "userFirstName": str,
    "userLastName": str,
    "userPreferredName": str,
    "userFullName": str,
    "userEmail": str,
    "userDisplayCode": str,
    # ... 33 more fields (see CompassUser model)
}
```

**Contract**:
- MUST be parseable by `CompassParser.parse(CompassUser, data)`
- All required fields MUST be present
- Optional fields MAY be `None` or missing

---

#### Calendar Events Response

```python
[
    {
        "__type": "CalendarTransport:http://jdlf.com.au/ns/data/calendar",
        "activityId": int,
        "title": str,
        "longTitle": str,
        "longTitleWithoutTime": str,
        "description": str,
        "start": str,  # ISO 8601 datetime
        "finish": str,  # ISO 8601 datetime
        "allDay": bool,
        # ... 29 more fields (see CompassEvent model)
    }
]
```

**Contract**:
- MUST be parseable by `CompassParser.parse(CompassEvent, data)`
- Each event MUST have all required fields
- Optional fields MAY be `None` or missing

---

## Interface Parity Requirements

### Must Match

Both clients MUST match these exactly:

1. **Method Signatures**: Identical parameter names, types, defaults
2. **Return Types**: Same types (Dict, List, bool, None)
3. **Attributes**: Same names and types
4. **Exception Types**: Same exception classes (though mock may not raise some)

### May Differ

These MAY differ between implementations:

1. **Internal Implementation**: Network calls vs. file loading
2. **Performance**: Real client is slower (network latency)
3. **Error Frequency**: Real client may fail, mock rarely fails
4. **Session Management**: Real client uses HTTP session, mock doesn't

### Must NOT Differ

Consumers MUST NOT observe these differences:

1. **Public API**: Same methods and signatures
2. **Data Schemas**: Same response structures
3. **State Transitions**: Same state machine
4. **Pre/Post Conditions**: Same contracts

---

## Verification

### Interface Compliance Tests

Both clients MUST pass these tests:

```python
import pytest
from compass_client import CompassClient, CompassMockClient

@pytest.mark.parametrize("client_class", [CompassClient, CompassMockClient])
def test_interface_compliance(client_class):
    """Verify both clients implement the same interface."""

    # Test 1: Constructor
    client = client_class("https://example.com", "user", "pass")
    assert hasattr(client, "base_url")
    assert hasattr(client, "username")
    assert hasattr(client, "password")
    assert hasattr(client, "user_id")
    assert hasattr(client, "_authenticated")
    assert client._authenticated is False

    # Test 2: Methods exist
    assert callable(client.login)
    assert callable(client.get_user_details)
    assert callable(client.get_calendar_events)
    assert callable(client.close)

    # Test 3: Login
    result = client.login()
    assert result is True
    assert client._authenticated is True

    # Test 4: Get user details
    user_data = client.get_user_details()
    assert isinstance(user_data, dict)
    assert "userId" in user_data

    # Test 5: Get calendar events
    events = client.get_calendar_events("2025-12-01", "2025-12-31")
    assert isinstance(events, list)

    # Test 6: Close
    client.close()  # Should not raise


@pytest.mark.parametrize("client_class", [CompassClient, CompassMockClient])
def test_parser_compatibility(client_class):
    """Verify both clients return data parseable by CompassParser."""
    from compass_client import CompassParser, CompassUser, CompassEvent

    client = client_class("https://example.com", "user", "pass")
    client.login()

    # User details must be parseable
    user_data = client.get_user_details()
    user = CompassParser.parse(CompassUser, user_data)  # Must not raise
    assert user.user_id is not None

    # Calendar events must be parseable
    events_data = client.get_calendar_events("2025-12-01", "2025-12-31")
    events = CompassParser.parse(CompassEvent, events_data)  # Must not raise
    assert isinstance(events, list)
```

---

## Future Enhancements

### Formal Protocol (Planned for v2.0)

```python
from typing import Protocol, Optional, Dict, List, Any

class CompassClientProtocol(Protocol):
    """Formal protocol for Compass clients."""

    base_url: str
    username: str
    password: str
    user_id: Optional[int]
    _authenticated: bool

    def login(self) -> bool: ...

    def get_user_details(self, target_user_id: Optional[int] = None) -> Dict[str, Any]: ...

    def get_calendar_events(
        self, start_date: str, end_date: str, limit: int = 100
    ) -> List[Dict[str, Any]]: ...

    def close(self) -> None: ...
```

**Benefits**:
- Static type checking with mypy
- IDE autocompletion
- Compile-time interface verification

---

### Context Manager Support (Planned for v2.0)

```python
class CompassClient:
    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Usage
with CompassClient(...) as client:
    user = client.get_user_details()
    events = client.get_calendar_events(...)
# Automatically closes
```

---

## Document Metadata

- **Created**: 2025-12-09
- **Feature**: 002-compass-api-decoupling
- **Version**: 1.0.0
- **Related Documents**:
  - [compass-client-api.md](./compass-client-api.md) - Full API documentation
  - [factory-contract.md](./factory-contract.md) - Factory function contract
  - [mock-data-schema.json](./mock-data-schema.json) - Mock data schema
