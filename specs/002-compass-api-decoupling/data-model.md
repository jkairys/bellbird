# Data Model: Compass API Decoupling and Mock Data Infrastructure

**Feature**: `002-compass-api-decoupling` | **Date**: 2025-12-09 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Overview

This document defines the data structures, entities, and relationships for the `compass-client` package and its integration with the Bellweaver application. The decoupled architecture supports both real Compass API integration and mock data mode for development and testing.

## Package Architecture

```
compass-client (standalone package)
    ├── Client Layer: CompassClient, CompassMockClient
    ├── Model Layer: CompassEvent, CompassUser
    ├── Parser Layer: CompassParser
    ├── Factory Layer: create_client()
    └── Data Layer: Mock JSON files

bellweaver (application)
    └── Consumer: Imports from compass-client package
```

---

## 1. Entities and Models

### 1.1 Client Entities

#### 1.1.1 CompassClient (Real HTTP Client)

**Purpose**: Authenticates with and fetches data from real Compass Education API.

**Location**: `packages/compass-client/compass_client/client.py`

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `base_url` | `str` | Yes | Compass instance URL (e.g., "https://school.compass.education") |
| `username` | `str` | Yes | Compass login username |
| `password` | `str` | Yes | Compass login password |
| `session` | `requests.Session` | Auto | HTTP session with cookies and headers |
| `user_id` | `Optional[int]` | Auto | Authenticated user's Compass ID (extracted after login) |
| `school_config_key` | `Optional[str]` | Auto | School-specific config key (extracted after login) |
| `_authenticated` | `bool` | Auto | Authentication state flag |

**Methods**:

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `login()` | None | `bool` | Authenticates with Compass via HTTP POST, extracts session metadata |
| `get_user_details()` | `target_user_id: Optional[int]` | `Dict[str, Any]` | Fetches user details from `/Services/User.svc/GetUserDetailsBlobByUserId` |
| `get_calendar_events()` | `start_date: str, end_date: str, limit: int` | `List[Dict[str, Any]]` | Fetches calendar events from `/Services/Calendar.svc/GetCalendarEventsByUser` |
| `close()` | None | `None` | Closes HTTP session |

**State Transitions**:

```
[Created] → login() → [Authenticated]
[Authenticated] → get_user_details() | get_calendar_events() → [Data Fetched]
[Data Fetched] → close() → [Closed]
```

**Validation Rules**:
- `base_url` must be valid URL, stripped of trailing slashes
- Authentication must succeed before data fetching methods can be called
- `user_id` must be extracted from session before API calls (auto-fetched if missing)
- Raises `Exception` on authentication failure, HTTP errors, or invalid JSON responses

---

#### 1.1.2 CompassMockClient (Mock Client)

**Purpose**: Returns realistic mock data without requiring Compass credentials, enabling local development and CI testing.

**Location**: `packages/compass-client/compass_client/mock_client.py`

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `base_url` | `str` | Yes | Mock URL (not used but maintains interface compatibility) |
| `username` | `str` | Yes | Mock username (not used but maintains interface compatibility) |
| `password` | `str` | Yes | Mock password (not used but maintains interface compatibility) |
| `user_id` | `int` | Auto | Hardcoded mock user ID (e.g., 12345) |
| `_authenticated` | `bool` | Auto | Authentication state flag (always True after login) |
| `_events` | `List[Dict[str, Any]]` | Auto | Loaded mock calendar events |
| `_user` | `Dict[str, Any]` | Auto | Loaded mock user details |

**Methods**:

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `login()` | None | `bool` | Mock login (always succeeds, sets `_authenticated = True`) |
| `get_user_details()` | `target_user_id: Optional[int]` | `Dict[str, Any]` | Returns mock user data from `data/mock/compass_user.json` |
| `get_calendar_events()` | `start_date: str, end_date: str, limit: int` | `List[Dict[str, Any]]` | Returns filtered mock events from `data/mock/compass_events.json` |
| `close()` | None | `None` | No-op (maintains interface parity) |
| `_load_mock_events()` | None | `List[Dict[str, Any]]` | Loads events from JSON file, falls back to hardcoded data |
| `_load_mock_user()` | None | `Dict[str, Any]` | Loads user from JSON file, falls back to hardcoded data |

**State Transitions**:

```
[Created] → _load_mock_events() + _load_mock_user() → [Data Loaded]
[Data Loaded] → login() → [Authenticated]
[Authenticated] → get_user_details() | get_calendar_events() → [Mock Data Returned]
```

**Validation Rules**:
- Must maintain identical interface to `CompassClient` (duck typing)
- If mock data files are missing, must fall back to hardcoded synthetic data
- Date filtering for events must match real client behavior
- Raises `Exception` if called before `login()` (interface parity)

---

### 1.2 Domain Models (Pydantic)

#### 1.2.1 CompassEvent

**Purpose**: Validated model for Compass calendar events.

**Location**: `packages/compass-client/compass_client/models.py` (moved from `backend/bellweaver/models/compass.py`)

**Schema** (37 fields total, key fields shown):

| Field | Type | Alias (API) | Required | Description |
|-------|------|-------------|----------|-------------|
| `type` | `str` | `__type` | Yes | API type identifier |
| `activity_id` | `int` | `activityId` | Yes | Unique activity identifier |
| `title` | `str` | `title` | Yes | Event title |
| `long_title` | `str` | `longTitle` | Yes | Full event title with time |
| `long_title_without_time` | `str` | `longTitleWithoutTime` | Yes | Event title without time prefix |
| `description` | `str` | `description` | Yes | Event description |
| `start` | `datetime` | `start` | Yes | Event start datetime (ISO 8601) |
| `finish` | `datetime` | `finish` | Yes | Event end datetime (ISO 8601) |
| `all_day` | `bool` | `allDay` | Yes | Whether event is all-day |
| `location` | `Optional[str]` | `location` | No | Location string |
| `locations` | `Optional[List[CalendarEventLocation]]` | `locations` | No | Structured location data |
| `managers` | `Optional[List[CalendarEventManager]]` | `managers` | No | Event managers |
| `instance_id` | `str` | `instanceId` | Yes | Event instance UUID |
| `guid` | `str` | `guid` | Yes | Global unique identifier |
| `is_recurring` | `bool` | `isRecurring` | Yes | Whether event recurs |
| `attendee_user_id` | `int` | `attendeeUserId` | Yes | Attendee's user ID |
| `background_color` | `str` | `backgroundColor` | Yes | Event color (hex) |

**Nested Models**:

**CalendarEventLocation**:
| Field | Type | Alias | Required |
|-------|------|-------|----------|
| `type` | `str` | `__type` | Yes |
| `location_id` | `int` | `locationId` | Yes |
| `location_name` | `Optional[str]` | `locationName` | No |
| `covering_location_id` | `Optional[int]` | `coveringLocationId` | No |
| `covering_location_name` | `Optional[str]` | `coveringLocationName` | No |

**CalendarEventManager**:
| Field | Type | Alias | Required |
|-------|------|-------|----------|
| `type` | `str` | `__type` | Yes |
| `manager_user_id` | `int` | `managerUserId` | Yes |
| `manager_import_identifier` | `str` | `managerImportIdentifier` | Yes |
| `covering_user_id` | `Optional[int]` | `coveringUserId` | No |
| `covering_import_identifier` | `Optional[str]` | `coveringImportIdentifier` | No |

**Validation Rules**:
- All datetime fields must be valid ISO 8601 format
- `activity_id` must be positive integer
- `all_day` must be boolean
- `background_color` should be valid hex color (not enforced by model)
- Field aliases handle camelCase → snake_case transformation
- Pydantic `ConfigDict(populate_by_name=True)` allows both snake_case and camelCase

---

#### 1.2.2 CompassUser

**Purpose**: Validated model for Compass user details.

**Location**: `packages/compass-client/compass_client/models.py` (moved from `backend/bellweaver/models/compass.py`)

**Schema** (40 fields total, key fields shown):

| Field | Type | Alias (API) | Required | Description |
|-------|------|-------------|----------|-------------|
| `type` | `str` | `__type` | Yes | API type identifier ("UserDetailsBlob") |
| `user_id` | `int` | `userId` | Yes | Compass user ID |
| `user_first_name` | `str` | `userFirstName` | Yes | User's first name |
| `user_last_name` | `str` | `userLastName` | Yes | User's last name |
| `user_preferred_name` | `str` | `userPreferredName` | Yes | User's preferred first name |
| `user_full_name` | `str` | `userFullName` | Yes | Full name |
| `user_email` | `str` | `userEmail` | Yes | Email address |
| `user_display_code` | `str` | `userDisplayCode` | Yes | School identifier (e.g., "ABC-0000") |
| `user_compass_person_id` | `str` | `userCompassPersonId` | Yes | Person UUID |
| `user_year_level` | `Optional[str]` | `userYearLevel` | No | Year level (e.g., "8") |
| `user_form_group` | `Optional[str]` | `userFormGroup` | No | Form group |
| `user_house` | `Optional[str]` | `userHouse` | No | House name |
| `user_role` | `int` | `userRole` | Yes | User role (e.g., 3 for parent) |
| `age` | `Optional[int]` | `age` | No | User's age |
| `birthday` | `Optional[datetime]` | `birthday` | No | Date of birth |
| `gender` | `Optional[str]` | `gender` | No | Gender |
| `user_photo_path` | `str` | `userPhotoPath` | Yes | Photo URL path |
| `chronicle_pinned_count` | `int` | `chroniclePinnedCount` | Yes | Pinned chronicle items count |
| `has_email_restriction` | `bool` | `hasEmailRestriction` | Yes | Email restriction flag |

**Validation Rules**:
- `user_id` must be positive integer
- Email should be valid format (not enforced by model)
- All boolean fields must be True/False
- Optional datetime fields must be valid ISO 8601 if provided
- Field aliases handle camelCase → snake_case transformation

---

### 1.3 Parser Entity

#### 1.3.1 CompassParser

**Purpose**: Generic validation layer that transforms raw API dictionaries into validated Pydantic models.

**Location**: `packages/compass-client/compass_client/parser.py` (moved from `backend/bellweaver/parsers/compass.py`)

**Type Parameters**:
- `T = TypeVar("T", bound=BaseModel)` - Generic Pydantic model type

**Methods**:

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `parse()` | `(model: Type[T], raw: Dict \| List[Dict]) -> T \| List[T]` | Validated model(s) | Generic parser, auto-detects single vs list |
| `parse_safe()` | `(model: Type[T], raw_list: List[Dict], skip_invalid: bool) -> Tuple[List[T], List[CompassParseError]]` | (valid_items, errors) | Safe parsing with error collection |
| `_parse_single()` | `(model: Type[T], raw: Dict) -> T` | Single validated model | Internal: parse one object |
| `_parse_list()` | `(model: Type[T], raw_list: List[Dict]) -> List[T]` | List of validated models | Internal: parse list (strict mode) |

**Exception**:

**CompassParseError**:
| Attribute | Type | Description |
|-----------|------|-------------|
| `message` | `str` | Human-readable error message |
| `raw_data` | `Any` | The raw data that failed parsing |
| `validation_errors` | `Optional[List[Any]]` | Pydantic validation errors |

**Validation Rules**:
- `parse()` fails fast on first validation error
- `parse_safe()` collects all errors but continues parsing valid items
- All Pydantic validation rules from model schemas apply
- Returns type-safe validated instances (enforced via generics)

---

### 1.4 Factory Entity

#### 1.4.1 Client Factory

**Purpose**: Creates appropriate client instance based on configuration mode.

**Location**: `packages/compass-client/compass_client/factory.py` (NEW)

**Function Signature**:

```python
def create_client(
    base_url: str,
    username: str,
    password: str,
    mode: Optional[str] = None
) -> CompassClient | CompassMockClient
```

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `base_url` | `str` | Yes | - | Compass instance URL |
| `username` | `str` | Yes | - | Username |
| `password` | `str` | Yes | - | Password |
| `mode` | `Optional[str]` | No | `os.getenv("COMPASS_MODE", "real")` | Mode: "real" or "mock" |

**Returns**: `CompassClient` (real mode) or `CompassMockClient` (mock mode)

**Raises**: `ValueError` if mode is not "real" or "mock"

**State Transitions**:

```
create_client(mode="real") → CompassClient instance
create_client(mode="mock") → CompassMockClient instance
create_client() → reads COMPASS_MODE env var → appropriate client
```

**Validation Rules**:
- `mode` must be "real" or "mock" (case-insensitive)
- If `mode` is None, reads from `COMPASS_MODE` environment variable
- Defaults to "real" if environment variable not set
- Credentials are required even for mock mode (interface consistency)

---

## 2. Data Structures

### 2.1 Mock Data Files

Mock data is stored in the compass-client package and committed to version control.

**Location**: `packages/compass-client/data/mock/`

**Files**:

#### 2.1.1 compass_events.json

**Purpose**: Mock calendar events for testing and development.

**Schema**: Array of event objects matching CompassEvent model

**Example Structure**:

```json
[
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
]
```

**Validation Rules**:
- Must be valid JSON array
- Each object must validate against `CompassEvent` Pydantic model
- Should include diverse event types (all-day, recurring, single events)
- Dates should span reasonable test range (e.g., 3 months)
- Minimum 5-10 events for realistic testing

---

#### 2.1.2 compass_user.json

**Purpose**: Mock user details for testing and development.

**Schema**: Single user object matching CompassUser model

**Example Structure**:

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
  "userPhotoPath": "/images/default-avatar.png",
  "userSquarePhotoPath": "/images/default-avatar-square.png",
  "chroniclePinnedCount": 0,
  "hasEmailRestriction": false,
  "isBirthday": false,
  "userFlags": [],
  "userTimeLinePeriods": []
}
```

**Validation Rules**:
- Must be valid JSON object
- Must validate against `CompassUser` Pydantic model
- Should represent realistic user profile
- PII should be synthetic/anonymized

---

#### 2.1.3 schema_version.json

**Purpose**: Tracks schema version for mock data compatibility checks.

**Schema**:

```json
{
  "version": "1.0.0",
  "last_updated": "2025-12-09T10:00:00Z",
  "source": "real",
  "compass_version": "unknown",
  "notes": "Initial mock data collected from production Compass API"
}
```

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | `str` | Yes | Semantic version of mock data schema |
| `last_updated` | `str` | Yes | ISO 8601 timestamp of last update |
| `source` | `str` | Yes | "real" (from API) or "synthetic" (hardcoded) |
| `compass_version` | `str` | No | Compass API version if known |
| `notes` | `str` | No | Human-readable notes about this data |

**Validation Rules**:
- `version` must follow semantic versioning (X.Y.Z)
- `last_updated` must be valid ISO 8601 datetime
- `source` must be "real" or "synthetic"
- Version increments on schema-breaking changes

---

### 2.2 Environment Configuration

#### 2.2.1 Environment Variables

**Location**: `.env` file in project root (for Bellweaver) or `packages/compass-client/.env` (for standalone testing)

**Variables**:

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `COMPASS_MODE` | `str` | No | `"real"` | Client mode: "real" or "mock" |
| `COMPASS_BASE_URL` | `str` | Yes (real mode) | - | Compass instance URL |
| `COMPASS_USERNAME` | `str` | Yes (real mode) | - | Compass username |
| `COMPASS_PASSWORD` | `str` | Yes (real mode) | - | Compass password |

**Example `.env`**:

```bash
# Compass Configuration
COMPASS_MODE=mock                              # Use mock data for development
COMPASS_BASE_URL=https://school.compass.education
COMPASS_USERNAME=your_username
COMPASS_PASSWORD=your_password

# Other Bellweaver config...
```

**Validation Rules**:
- `COMPASS_MODE` is case-insensitive ("MOCK" == "mock")
- In real mode, credentials are required
- In mock mode, credentials can be dummy values (not used)
- Bellweaver CI sets `COMPASS_MODE=mock` to bypass geo-blocking

---

#### 2.2.2 Configuration Loading

**Location**: `packages/compass-client/compass_client/factory.py`

**Logic**:

```python
def create_client(..., mode: Optional[str] = None):
    # Priority: explicit parameter > environment variable > default
    effective_mode = mode or os.getenv("COMPASS_MODE", "real")

    if effective_mode.lower() == "mock":
        return CompassMockClient(base_url, username, password)
    elif effective_mode.lower() == "real":
        return CompassClient(base_url, username, password)
    else:
        raise ValueError(f"Invalid mode: {effective_mode}")
```

**Configuration Precedence**:
1. Explicit `mode` parameter (highest priority)
2. `COMPASS_MODE` environment variable
3. Default value `"real"` (lowest priority)

---

## 3. Relationships

### 3.1 Package Dependencies

```
compass-client (standalone, no dependencies on bellweaver)
    ↓ (installed as dependency)
bellweaver (depends on compass-client)
```

**Dependency Direction**: One-way only (bellweaver → compass-client)

**Installation**:
- Bellweaver's `pyproject.toml` includes:
  ```toml
  [tool.poetry.dependencies]
  compass-client = {path = "../packages/compass-client", develop = true}
  ```

---

### 3.2 Client-to-Data Relationships

```
CompassClient → Real Compass API
    ├── login() → POST /login.aspx
    ├── get_user_details() → POST /Services/User.svc/GetUserDetailsBlobByUserId
    └── get_calendar_events() → POST /Services/Calendar.svc/GetCalendarEventsByUser

CompassMockClient → Mock JSON Files
    ├── get_user_details() → data/mock/compass_user.json
    └── get_calendar_events() → data/mock/compass_events.json
```

---

### 3.3 Data Flow

```
[Raw API Data]
    ↓
[Client Layer] (CompassClient or CompassMockClient)
    ↓ returns Dict[str, Any] or List[Dict[str, Any]]
[Parser Layer] (CompassParser.parse())
    ↓ validates with Pydantic
[Domain Models] (CompassEvent, CompassUser)
    ↓
[Bellweaver Application] (uses validated models)
```

**Key Insight**: Parser acts as validation boundary. Clients return raw dicts, parsers guarantee type safety.

---

### 3.4 Mock Data to Real API Alignment

**Principle**: Mock data must be structurally identical to real API responses.

**Enforcement**:
1. Mock data is initially collected from real API using `CompassClient`
2. Mock data files validate against same Pydantic models as real data
3. `CompassParser` tests run against both real and mock sources
4. Schema version tracking alerts to drift

**Drift Detection**:
- When real API returns fields not in mock data → validation passes (extra fields ignored by Pydantic)
- When mock data missing required fields → validation fails (caught in tests)
- Schema version incremented when mock data refreshed from real API

---

## 4. Validation Rules

### 4.1 Model Validation (Pydantic)

All Pydantic models use these settings:

```python
model_config = ConfigDict(populate_by_name=True)
```

**Rules**:
- **Field Aliases**: Accept both camelCase (API) and snake_case (Python)
  - Example: `userFullName` and `user_full_name` both work
- **Extra Fields**: Ignored by default (allows API to add fields without breaking)
- **Type Coercion**: Basic coercion (e.g., string to int) if unambiguous
- **Required Fields**: Validation fails if missing
- **Optional Fields**: None allowed if `Optional[]` type hint
- **Datetime Parsing**: Automatic ISO 8601 parsing to Python `datetime`

---

### 4.2 Mock Data Validation

**File Validation** (on load):

```python
# In CompassMockClient.__init__()
try:
    with open("data/mock/compass_events.json") as f:
        events_data = json.load(f)
    # Validate immediately
    parsed = CompassParser.parse(CompassEvent, events_data)
except (FileNotFoundError, json.JSONDecodeError, CompassParseError):
    # Fall back to hardcoded synthetic data
    events_data = self._get_fallback_events()
```

**Validation Rules**:
- Mock data files must be valid JSON
- Mock data must validate against Pydantic models
- If validation fails, fall back to hardcoded data (don't crash)
- Log warnings when falling back

---

### 4.3 Schema Version Validation

**Version Check** (on application startup in mock mode):

```python
def validate_mock_data_version():
    """Check mock data schema version compatibility."""
    with open("data/mock/schema_version.json") as f:
        version_info = json.load(f)

    current_version = version_info["version"]
    if not is_compatible(current_version, EXPECTED_VERSION):
        logger.warning(
            f"Mock data version {current_version} may be incompatible "
            f"with expected version {EXPECTED_VERSION}"
        )
```

**Rules**:
- Semantic versioning: MAJOR.MINOR.PATCH
- MAJOR increment: Breaking schema changes (incompatible)
- MINOR increment: New optional fields (backward compatible)
- PATCH increment: Data updates, no schema change
- Application logs warning if major version mismatch

---

### 4.4 Client Interface Validation

**Contract**: Both clients must implement identical interface.

**Enforcement**:
- Python duck typing (no formal interface/protocol yet)
- Integration tests run against both clients
- Future: Define `Protocol` for type checking

**Required Methods** (identical signatures):
- `login() -> bool`
- `get_user_details(target_user_id: Optional[int]) -> Dict[str, Any]`
- `get_calendar_events(start_date: str, end_date: str, limit: int) -> List[Dict[str, Any]]`
- `close() -> None`

**Test Coverage**:
```python
@pytest.mark.parametrize("client_factory", [
    lambda: CompassClient(...),
    lambda: CompassMockClient(...)
])
def test_client_interface(client_factory):
    """Verify both clients implement same interface."""
    client = client_factory()
    assert hasattr(client, "login")
    assert hasattr(client, "get_user_details")
    # ... etc
```

---

## 5. State Transitions

### 5.1 CompassClient State Machine

```
┌─────────┐
│ Created │
└────┬────┘
     │ login()
     ↓
┌──────────────┐
│Authenticated │◄──────────┐
└──┬───────────┘           │
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
- **Created**: Instance initialized, no network calls made
- **Authenticated**: Logged in, session cookies active, `user_id` extracted
- **Data Fetched**: API data retrieved (can fetch multiple times)
- **Closed**: Session closed, no further operations allowed

**Transitions**:
- `login()`: Created → Authenticated (raises Exception on failure)
- `get_*()`: Authenticated → Data Fetched (can repeat)
- `close()`: Any state → Closed

---

### 5.2 CompassMockClient State Machine

```
┌─────────┐
│ Created │ (mock data loaded)
└────┬────┘
     │ login() (always succeeds)
     ↓
┌──────────────┐
│Authenticated │◄──────────┐
└──┬───────────┘           │
   │ get_user_details()    │ (returns pre-loaded data)
   │ get_calendar_events() │
   ↓                       │
┌──────────────┐           │
│ Data Fetched │───────────┘
└──────┬───────┘
       │ close() (no-op)
       ↓
   ┌────────┐
   │ Closed │
   └────────┘
```

**States**: Same as `CompassClient` for interface parity

**Key Difference**: Data is loaded at initialization, not fetched on-demand

---

### 5.3 Mock Data Loading States

```
┌─────────────────┐
│ Initialization  │
└────────┬────────┘
         │ try load from file
         ↓
    ┌────────────┐
    │ File Load  │
    └─┬────────┬─┘
      │        │
  success   failure (FileNotFoundError, JSONDecodeError)
      │        │
      ↓        ↓
┌──────────┐ ┌─────────────────┐
│ Validate │ │ Fallback Load   │
│ with     │ │ (hardcoded data)│
│ Pydantic │ └─────────────────┘
└─┬────┬───┘
  │    │
valid invalid
  │    │
  ↓    ↓
┌─────────────┐  ┌─────────────────┐
│ Data Ready  │  │ Fallback Load   │
│ (from file) │  │ (hardcoded data)│
└─────────────┘  └─────────────────┘
         │              │
         └──────┬───────┘
                ↓
        ┌───────────────┐
        │ Data Loaded   │
        │ (ready to use)│
        └───────────────┘
```

**Fallback Strategy**: Never crash on missing/invalid mock data, always provide working defaults.

---

## 6. Data Persistence and Lifecycle

### 6.1 Mock Data Lifecycle

**Storage**:
- Mock data files committed to git repository
- Location: `packages/compass-client/data/mock/`
- Versioned alongside code

**Refresh Process**:

```bash
# Command to refresh mock data (uses real Compass API)
$ cd packages/compass-client
$ poetry run python -m compass_client.cli refresh-mock-data \
    --base-url $COMPASS_BASE_URL \
    --username $COMPASS_USERNAME \
    --password $COMPASS_PASSWORD
```

**Refresh Steps**:
1. Authenticate with real Compass API using `CompassClient`
2. Fetch user details and calendar events (configurable date range)
3. Sanitize PII (anonymize names, emails, student IDs)
4. Validate against Pydantic models
5. Write to `compass_user.json` and `compass_events.json`
6. Update `schema_version.json` with new timestamp and version
7. Commit updated files to repository

**Refresh Frequency**: Manual, as needed (recommended quarterly or when API changes)

---

### 6.2 Real API Data Lifecycle

**Storage**: Not persisted by compass-client (client is stateless)

**Bellweaver Integration**:
- Bellweaver stores API responses in `ApiPayload` database table
- `compass-client` remains stateless (fetch-only)

---

## 7. Security and Privacy

### 7.1 Mock Data Sanitization

**PII to Anonymize**:
- User names → Generic names (e.g., "Student A", "Jane Smith")
- Email addresses → Generic emails (e.g., "student1@example.com")
- Student IDs → Synthetic IDs
- Phone numbers → Removed
- Addresses → Removed
- Photos → Default avatar paths

**Retained Data**:
- Event types and structures
- Field names and data types
- Relationships (e.g., user_id references)
- Date patterns (e.g., school terms)

**Implementation**:
```python
def sanitize_user_data(user: Dict[str, Any]) -> Dict[str, Any]:
    """Remove PII from user data."""
    return {
        **user,
        "userFirstName": "Jane",
        "userLastName": "Smith",
        "userEmail": "student@example.com",
        "userPhotoPath": "/images/default-avatar.png",
        # ... preserve structure but anonymize values
    }
```

---

### 7.2 Credential Handling

**Real Mode**:
- Credentials read from environment variables
- Never logged or stored in mock data
- Session cookies stored in `requests.Session` (memory only)

**Mock Mode**:
- Credentials not used (dummy values accepted)
- No authentication performed
- Safe for CI environments

---

## 8. Testing Strategy

### 8.1 Model Validation Tests

**Location**: `packages/compass-client/tests/unit/test_models.py`

**Coverage**:
- Valid data parses correctly
- Invalid data raises ValidationError
- Field aliases work (both camelCase and snake_case)
- Optional fields handle None
- Datetime parsing works

---

### 8.2 Parser Tests

**Location**: `packages/compass-client/tests/unit/test_parser.py`

**Coverage**:
- `parse()` handles single objects and lists
- `parse_safe()` collects errors without stopping
- Invalid data raises `CompassParseError`
- Partial data with missing required fields fails

---

### 8.3 Client Tests

**Location**: `packages/compass-client/tests/unit/test_client.py` (mock), `tests/integration/test_client.py` (real, optional)

**Coverage**:
- Mock client loads data from files
- Mock client falls back to hardcoded data
- Real client authenticates (integration test, skipped in CI)
- Interface parity between both clients

---

### 8.4 Integration Tests

**Location**: `packages/bellweaver/tests/integration/test_compass_integration.py`

**Coverage**:
- Bellweaver can use `create_client()` factory
- Mock mode works end-to-end
- API endpoints return data from mock client

---

## 9. Migration Path

### 9.1 Code Migration

**From** (current monolithic structure):
```
backend/bellweaver/
├── adapters/compass.py
├── adapters/compass_mock.py
├── models/compass.py
└── parsers/compass.py
```

**To** (decoupled packages):
```
packages/compass-client/compass_client/
├── client.py         # moved from adapters/compass.py
├── mock_client.py    # moved from adapters/compass_mock.py
├── models.py         # moved from models/compass.py
├── parser.py         # moved from parsers/compass.py
└── factory.py        # NEW
```

**Import Changes**:

```python
# OLD
from bellweaver.adapters.compass import CompassClient
from bellweaver.models.compass import CompassEvent

# NEW
from compass_client import create_client, CompassEvent, CompassParser
```

---

### 9.2 Data Migration

**Mock Data**:
- Existing mock data at `backend/data/mock/compass_events_sanitized.json`
- Move to `packages/compass-client/data/mock/compass_events.json`
- Add `compass_user.json` (extract from existing data or fetch fresh)
- Create `schema_version.json`

---

## 10. Appendix

### 10.1 Complete Field Reference

**CompassEvent** (all 37 fields):

1. `type` (str)
2. `activity_id` (int)
3. `activity_import_identifier` (Optional[str])
4. `activity_type` (int)
5. `all_day` (bool)
6. `attendance_mode` (int)
7. `attendee_user_id` (int)
8. `background_color` (str)
9. `calendar_id` (int)
10. `category_ids` (Optional[str])
11. `comment` (Optional[str])
12. `description` (str)
13. `event_setup_status` (Optional[int])
14. `finish` (datetime)
15. `guid` (str)
16. `in_class_status` (Optional[int])
17. `instance_id` (str)
18. `is_recurring` (bool)
19. `learning_task_activity_id` (Optional[int])
20. `learning_task_id` (Optional[int])
21. `lesson_plan_configured` (bool)
22. `location` (Optional[str])
23. `locations` (Optional[List[CalendarEventLocation]])
24. `long_title` (str)
25. `long_title_without_time` (str)
26. `manager_id` (int)
27. `managers` (Optional[List[CalendarEventManager]])
28. `minutes_meeting_id` (Optional[int])
29. `period` (Optional[str])
30. `recurring_finish` (Optional[datetime])
31. `recurring_start` (Optional[datetime])
32. `repeat_days` (Optional[str])
33. `repeat_forever` (bool)
34. `repeat_frequency` (int)
35. `repeat_until` (Optional[datetime])
36. `roll_marked` (bool)
37. `running_status` (int)
38. `session_name` (Optional[str])
39. `start` (datetime)
40. `subject_id` (Optional[int])
41. `subject_long_name` (Optional[str])
42. `target_student_id` (int)
43. `teaching_days_only` (bool)
44. `text_color` (Optional[str])
45. `title` (str)
46. `unavailable_pd` (Optional[int])

**CompassUser** (all 40 fields):

1. `type` (str)
2. `age` (Optional[int])
3. `birthday` (Optional[datetime])
4. `chronicle_pinned_count` (int)
5. `contextual_form_group` (str)
6. `date_of_death` (Optional[datetime])
7. `gender` (Optional[str])
8. `has_email_restriction` (bool)
9. `is_birthday` (bool)
10. `user_act_student_id` (Optional[str])
11. `user_access_restrictions` (Optional[str])
12. `user_compass_person_id` (str)
13. `user_confirmation_photo_path` (str)
14. `user_details` (Optional[str])
15. `user_display_code` (str)
16. `user_email` (str)
17. `user_first_name` (str)
18. `user_flags` (list)
19. `user_form_group` (Optional[str])
20. `user_full_name` (str)
21. `user_gender_pronouns` (Optional[str])
22. `user_house` (Optional[str])
23. `user_id` (int)
24. `user_last_name` (str)
25. `user_phone_extension` (Optional[str])
26. `user_photo_path` (str)
27. `user_preferred_last_name` (str)
28. `user_preferred_name` (str)
29. `user_report_name` (str)
30. `user_report_pref_first_last` (str)
31. `user_role` (int)
32. `user_role_in_school` (Optional[str])
33. `user_school_id` (str)
34. `user_school_url` (str)
35. `user_sex` (Optional[str])
36. `user_square_photo_path` (str)
37. `user_status` (int)
38. `user_sussi_id` (str)
39. `user_time_line_periods` (list)
40. `user_vsn` (Optional[str])
41. `user_year_level` (Optional[str])
42. `user_year_level_id` (Optional[int])

---

### 10.2 JSON Schema Examples

**compass_events.json** (minimal valid example):

```json
[
  {
    "__type": "CalendarTransport:http://jdlf.com.au/ns/data/calendar",
    "activityId": 1,
    "activityType": 1,
    "allDay": false,
    "attendanceMode": 0,
    "attendeeUserId": 12345,
    "backgroundColor": "#4CAF50",
    "calendarId": 1,
    "description": "Test event",
    "finish": "2025-12-15T15:00:00+11:00",
    "guid": "test-guid",
    "instanceId": "test-instance",
    "isRecurring": false,
    "lessonPlanConfigured": false,
    "longTitle": "Test Event",
    "longTitleWithoutTime": "Test Event",
    "managerId": 101,
    "repeatForever": false,
    "repeatFrequency": 0,
    "rollMarked": false,
    "runningStatus": 0,
    "start": "2025-12-15T09:00:00+11:00",
    "targetStudentId": 12345,
    "teachingDaysOnly": false,
    "title": "Test Event"
  }
]
```

---

## Document Metadata

- **Created**: 2025-12-09
- **Author**: Claude Code
- **Feature**: 002-compass-api-decoupling
- **Related Documents**:
  - [spec.md](./spec.md) - Feature specification
  - [plan.md](./plan.md) - Implementation plan
  - [quickstart.md](./quickstart.md) - Developer quickstart (to be created)
  - [contracts/](./contracts/) - API contracts (to be created)
