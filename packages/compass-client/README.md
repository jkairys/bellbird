# Compass Client

A Python client library for the Compass Education API with built-in mock data support for development and testing.

## Features

- **Real API Client**: Authenticate with and fetch data from Compass Education
- **Mock Client**: Use realistic sample data without credentials (for local dev & CI)
- **Factory Pattern**: Easily switch between real and mock modes via environment variable
- **Pydantic Models**: Type-safe validated data models for events and users
- **Parser**: Generic parser with safe parsing and error collection
- **Independent Package**: Fully decoupled from Bellweaver application

## Installation

### As a dependency in another package

If using this package in a monorepo (e.g., the Bellweaver application):

```toml
# In your pyproject.toml
[tool.poetry.dependencies]
compass-client = {path = "../compass-client", develop = true}
```

Then install:

```bash
poetry install
```

### Standalone development

```bash
# Clone the repository
cd packages/compass-client

# Install with development dependencies
poetry install --with dev

# Verify installation
poetry run python -c "from compass_client import create_client; print('✓ Installation successful')"
```

## Quick Start

### 1. Using Mock Mode (No Credentials Required)

Perfect for development, testing, and CI environments:

```python
from compass_client import create_client

# Create mock client (uses sample data from data/mock/)
client = create_client(
    base_url="https://dummy.compass.education",
    username="dummy",
    password="dummy",
    mode="mock"
)

# Mock login always succeeds
client.login()

# Fetch mock data
events = client.get_calendar_events(
    start_date="2025-01-01",
    end_date="2025-12-31",
    limit=100
)

print(f"Fetched {len(events)} mock events")
```

### 2. Using Real API (Requires Compass Credentials)

```python
from compass_client import create_client

# Create real client
client = create_client(
    base_url="https://yourschool.compass.education",
    username="your_username",
    password="your_password",
    mode="real"
)

# Authenticate with Compass
success = client.login()
if not success:
    raise Exception("Authentication failed")

# Fetch real data
user_data = client.get_user_details()
events_data = client.get_calendar_events(
    start_date="2025-01-01",
    end_date="2025-01-31",
    limit=100
)

# Clean up
client.close()
```

### 3. Using Environment Variables

```bash
# Set mode via environment
export COMPASS_MODE=mock  # or "real"
export COMPASS_BASE_URL=https://yourschool.compass.education
export COMPASS_USERNAME=your_username
export COMPASS_PASSWORD=your_password
```

```python
from compass_client import create_client

# Mode is determined by COMPASS_MODE environment variable
client = create_client(
    base_url=os.getenv("COMPASS_BASE_URL"),
    username=os.getenv("COMPASS_USERNAME"),
    password=os.getenv("COMPASS_PASSWORD")
    # mode parameter omitted - reads from COMPASS_MODE env var
)

client.login()
# ... use client
```

## Usage Examples

### Parsing Data with Validated Models

```python
from compass_client import create_client, CompassParser, CompassEvent, CompassUser

# Create and authenticate client
client = create_client(..., mode="mock")
client.login()

# Fetch raw data
raw_events = client.get_calendar_events("2025-01-01", "2025-12-31", 100)
raw_user = client.get_user_details()

# Parse into type-safe Pydantic models
parser = CompassParser()
events = parser.parse(CompassEvent, raw_events)  # List[CompassEvent]
user = parser.parse(CompassUser, raw_user)        # CompassUser

# Type-safe access with IDE autocomplete
for event in events:
    print(f"{event.title} on {event.start.strftime('%Y-%m-%d')}")
    print(f"  Location: {event.location or 'TBD'}")
    print(f"  All day: {event.all_day}")
```

### Safe Parsing with Error Collection

```python
from compass_client import CompassParser, CompassEvent

parser = CompassParser()

# Parse with error collection (continues on invalid items)
valid_events, errors = parser.parse_safe(
    CompassEvent,
    raw_events_list,
    skip_invalid=True
)

print(f"Successfully parsed: {len(valid_events)} events")
print(f"Failed to parse: {len(errors)} events")

for error in errors:
    print(f"Error at index {error['index']}: {error['errors']}")
```

### Refreshing Mock Data from Real API

```bash
# Navigate to compass-client package
cd packages/compass-client

# Run refresh command with real credentials
poetry run python -m compass_client.cli refresh-mock-data \
    --base-url "https://yourschool.compass.education" \
    --username "your_username" \
    --password "your_password"

# Output:
# Authenticating with Compass...
# Fetching user details...
# Fetching calendar events...
# Sanitizing PII...
# Writing mock data files...
# ✓ Mock data refreshed successfully
```

### Using Different Clients with Same Interface

```python
from compass_client import CompassClient, CompassMockClient

# Both clients implement identical interface
def fetch_events(client):
    """Works with both real and mock clients"""
    client.login()
    events = client.get_calendar_events("2025-01-01", "2025-12-31", 100)
    return events

# Use with real client
real_client = CompassClient("https://school.compass.education", "user", "pass")
real_events = fetch_events(real_client)

# Use with mock client
mock_client = CompassMockClient("", "", "")
mock_events = fetch_events(mock_client)

# Same interface, different data sources
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `COMPASS_MODE` | No | `real` | Client mode: `real` or `mock` |
| `COMPASS_BASE_URL` | Yes (real mode) | - | Compass instance URL |
| `COMPASS_USERNAME` | Yes (real mode) | - | Compass username |
| `COMPASS_PASSWORD` | Yes (real mode) | - | Compass password |

### Configuration Precedence

1. **Explicit `mode` parameter** (highest priority)
2. **`COMPASS_MODE` environment variable**
3. **Default value**: `"real"` (lowest priority)

Example:

```python
# COMPASS_MODE=real in environment
client = create_client(..., mode="mock")  # Uses mock (explicit override)

# COMPASS_MODE=mock in environment
client = create_client(...)  # Uses mock (from env var)

# No COMPASS_MODE set
client = create_client(...)  # Uses real (default)
```

## Mock Data

### Mock Data Files

Located in `data/mock/`:

- **`compass_events.json`**: Sample calendar events (150+ events covering a school year)
- **`compass_user.json`**: Sample user details (anonymized student/parent profile)
- **`schema_version.json`**: Schema version metadata for compatibility tracking

### Mock Data Characteristics

- **Realistic Structure**: Matches real Compass API responses exactly
- **PII Sanitized**: No real names, emails, or identifying information
- **Diverse Content**: Multiple event types (classes, excursions, meetings, etc.)
- **Date Range**: Covers full school year (Jan-Dec 2025)
- **Validated**: All mock data validates against Pydantic models

### Updating Mock Data

```bash
# Refresh from real API (requires credentials)
poetry run python -m compass_client.cli refresh-mock-data

# The CLI will:
# 1. Authenticate with real Compass API
# 2. Fetch user details and events
# 3. Sanitize PII (remove names, emails, etc.)
# 4. Validate against Pydantic models
# 5. Write to data/mock/ files
# 6. Update schema_version.json with timestamp
```

## API Reference

### Factory Function

#### `create_client(base_url, username, password, mode=None)`

Creates appropriate client instance based on configuration mode.

**Parameters:**
- `base_url` (str): Compass instance URL (e.g., "https://school.compass.education")
- `username` (str): Compass username
- `password` (str): Compass password
- `mode` (Optional[str]): Operating mode: "real" or "mock" (defaults to COMPASS_MODE env var or "real")

**Returns:** `CompassClient` or `CompassMockClient`

**Raises:** `ValueError` if mode is not "real" or "mock"

### Client Classes

#### `CompassClient`

Real HTTP client for Compass Education API.

**Methods:**
- `login() -> bool`: Authenticate with Compass API
- `get_user_details(target_user_id: Optional[int] = None) -> Dict[str, Any]`: Fetch user details
- `get_calendar_events(start_date: str, end_date: str, limit: int) -> List[Dict[str, Any]]`: Fetch calendar events
- `close() -> None`: Close HTTP session

#### `CompassMockClient`

Mock client using sample data from `data/mock/`.

**Methods:** (Identical interface to `CompassClient`)
- `login() -> bool`: Mock login (always succeeds)
- `get_user_details(target_user_id: Optional[int] = None) -> Dict[str, Any]`: Return mock user data
- `get_calendar_events(start_date: str, end_date: str, limit: int) -> List[Dict[str, Any]]`: Return filtered mock events
- `close() -> None`: No-op (maintains interface parity)

### Data Models

#### `CompassEvent`

Pydantic model for Compass calendar events (37 fields).

**Key Attributes:**
- `activity_id` (int): Unique activity identifier
- `title` (str): Event title
- `description` (str): Event description
- `start` (datetime): Event start time
- `finish` (datetime): Event end time
- `all_day` (bool): Whether event is all-day
- `location` (Optional[str]): Location string
- `is_recurring` (bool): Whether event recurs

See `compass_client/models.py` for complete schema.

#### `CompassUser`

Pydantic model for Compass user details (40 fields).

**Key Attributes:**
- `user_id` (int): Compass user ID
- `user_first_name` (str): First name
- `user_last_name` (str): Last name
- `user_email` (str): Email address
- `user_year_level` (Optional[str]): Year level (e.g., "8")
- `user_house` (Optional[str]): House name

See `compass_client/models.py` for complete schema.

### Parser

#### `CompassParser`

Generic parser for transforming raw API responses into validated Pydantic models.

**Methods:**

**`parse(model: Type[T], raw: Dict | List[Dict]) -> T | List[T]`**

Parse raw data into validated model(s). Auto-detects single object vs. list.

**Parameters:**
- `model`: Pydantic model class (e.g., `CompassEvent`)
- `raw`: Raw API response (dict or list of dicts)

**Returns:** Validated model instance or list of instances

**Raises:** `CompassParseError` on validation failure

**`parse_safe(model: Type[T], raw_list: List[Dict], skip_invalid: bool) -> Tuple[List[T], List[CompassParseError]]`**

Safe parsing with error collection. Continues parsing even if some items fail.

**Parameters:**
- `model`: Pydantic model class
- `raw_list`: List of raw API responses
- `skip_invalid`: If True, skip invalid items; if False, collect errors

**Returns:** Tuple of (valid_items, errors)

### Exceptions

#### `CompassClientError`

Base exception for all compass-client errors.

#### `CompassAuthenticationError`

Raised when authentication with Compass API fails.

#### `CompassParseError`

Raised when data validation fails during parsing.

**Attributes:**
- `message` (str): Human-readable error message
- `raw_data` (Any): The raw data that failed parsing
- `validation_errors` (Optional[List]): Pydantic validation errors

## Troubleshooting

### Issue: "Module 'compass_client' not found"

**Cause:** Package not installed or not in Python path.

**Solution:**
```bash
cd packages/compass-client
poetry install --with dev

# Verify installation
poetry run python -c "import compass_client; print(compass_client.__file__)"
```

### Issue: "Authentication failed" in real mode

**Cause:** Invalid credentials or network issues.

**Solution:**
```bash
# Check environment variables
echo $COMPASS_BASE_URL
echo $COMPASS_USERNAME

# Test authentication manually
poetry run python -c "
from compass_client import CompassClient
client = CompassClient('$COMPASS_BASE_URL', '$COMPASS_USERNAME', '$COMPASS_PASSWORD')
try:
    client.login()
    print('✓ Authentication successful')
except Exception as e:
    print(f'✗ Authentication failed: {e}')
"
```

### Issue: Mock data files not found

**Cause:** Mock data files missing or in wrong location.

**Solution:**
```bash
# Verify files exist
cd packages/compass-client
ls -la data/mock/

# Expected files:
# - compass_events.json
# - compass_user.json
# - schema_version.json

# If missing, refresh mock data (requires real credentials)
poetry run python -m compass_client.cli refresh-mock-data \
    --base-url "$COMPASS_BASE_URL" \
    --username "$COMPASS_USERNAME" \
    --password "$COMPASS_PASSWORD"
```

### Issue: "ValidationError" when parsing mock data

**Cause:** Mock data schema doesn't match Pydantic models.

**Solution:**
```bash
# Validate mock data
poetry run python -c "
from compass_client import CompassParser, CompassEvent, CompassUser
import json

# Validate events
with open('data/mock/compass_events.json') as f:
    events_data = json.load(f)
try:
    events = CompassParser.parse(CompassEvent, events_data)
    print(f'✓ {len(events)} events validate successfully')
except Exception as e:
    print(f'✗ Event validation failed: {e}')

# Validate user
with open('data/mock/compass_user.json') as f:
    user_data = json.load(f)
try:
    user = CompassParser.parse(CompassUser, user_data)
    print(f'✓ User validates successfully')
except Exception as e:
    print(f'✗ User validation failed: {e}')
"

# If validation fails, refresh mock data from real API
poetry run python -m compass_client.cli refresh-mock-data
```

### Issue: "Invalid mode" error

**Cause:** COMPASS_MODE environment variable has invalid value.

**Solution:**
```bash
# Check current value
echo $COMPASS_MODE

# Set valid value (case-insensitive)
export COMPASS_MODE=mock  # or "real", "MOCK", "REAL"

# Or specify explicitly in code
client = create_client(..., mode="mock")
```

## Development

### Running Tests

```bash
# Install development dependencies
poetry install --with dev

# Run all tests
poetry run pytest -v

# Run with coverage
poetry run pytest --cov=compass_client --cov-report=term-missing

# Run specific test file
poetry run pytest tests/unit/test_client.py -v

# Run specific test
poetry run pytest tests/unit/test_client.py::test_mock_client_login -v
```

### Code Quality

```bash
# Format code (Black)
poetry run black compass_client tests

# Lint (Flake8)
poetry run flake8 compass_client tests

# Type check (mypy)
poetry run mypy compass_client
```

### Project Structure

```
compass-client/
├── compass_client/           # Package source
│   ├── __init__.py          # Public API exports
│   ├── client.py            # Real Compass HTTP client
│   ├── mock_client.py       # Mock client with sample data
│   ├── models.py            # Pydantic models
│   ├── parser.py            # Generic parser
│   ├── factory.py           # create_client() factory
│   ├── exceptions.py        # Custom exceptions
│   └── cli/                 # CLI commands
│       └── refresh_mock_data.py
├── data/mock/               # Mock data (committed)
│   ├── compass_events.json
│   ├── compass_user.json
│   └── schema_version.json
├── tests/                   # Test suite
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── pyproject.toml           # Poetry configuration
└── README.md                # This file
```

## Contributing

This package is part of the Bellweaver monorepo. See the main repository for contribution guidelines.

## License

MIT
