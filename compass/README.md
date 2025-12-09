# Compass Education API Client

A Python client for interacting with the Compass Education platform API. This package provides authentication, data fetching, parsing, and validation for Compass Education data.

## Features

- **CompassClient**: HTTP-based client for authenticating and fetching data from Compass Education
- **CompassMockClient**: Mock client for testing without real credentials
- **Pydantic Models**: Type-safe models for Compass data (events, users, locations, managers)
- **CompassParser**: Generic parser for validating raw API responses into typed models
- **Comprehensive Tests**: Full test coverage for all components

## Installation

```bash
# Install via Poetry (recommended)
poetry add compass

# Or install in development mode
cd compass
poetry install
```

## Quick Start

```python
from compass import CompassClient, CompassParser, CompassEvent, CompassUser

# Initialize client
client = CompassClient(
    base_url="https://your-school.compass.education",
    username="your_username",
    password="your_password"
)

# Authenticate
client.login()

# Fetch raw data
raw_events = client.get_calendar_events("2025-01-01", "2025-01-31")
raw_user = client.get_user_details()

# Parse into typed models
events = CompassParser.parse(CompassEvent, raw_events)
user = CompassParser.parse(CompassUser, raw_user)

# Use the typed data
for event in events:
    print(f"{event.title} at {event.start}")

print(f"User: {user.user_full_name}")

# Close the session
client.close()
```

## Using the Mock Client

For testing without real credentials:

```python
from compass import CompassMockClient, CompassParser, CompassEvent

# Mock client returns synthetic data
client = CompassMockClient(
    base_url="https://example.compass.education",
    username="mock",
    password="mock"
)

client.login()
raw_events = client.get_calendar_events("2025-01-01", "2025-01-31")
events = CompassParser.parse(CompassEvent, raw_events)
```

## Models

### CompassEvent

Calendar event with fields including:
- `title`, `description`, `start`, `finish`
- `location`, `locations` (array of CalendarEventLocation)
- `managers` (array of CalendarEventManager)
- `all_day`, `is_recurring`
- And many more fields...

### CompassUser

User details with fields including:
- `user_full_name`, `user_email`, `user_id`
- `user_first_name`, `user_last_name`, `user_preferred_name`
- `user_year_level`, `user_form_group`, `user_house`
- `birthday`, `age`, `gender`
- And many more fields...

### CalendarEventLocation

Location information for events:
- `location_id`, `location_name`
- `covering_location_id`, `covering_location_name`

### CalendarEventManager

Manager information for events:
- `manager_user_id`, `manager_import_identifier`
- `covering_user_id`, `covering_import_identifier`

## Parser

The `CompassParser` provides safe parsing with error handling:

```python
from compass import CompassParser, CompassParseError, CompassEvent

# Strict parsing (raises on any error)
try:
    events = CompassParser.parse(CompassEvent, raw_events)
except CompassParseError as e:
    print(f"Parse error: {e}")
    print(f"Raw data: {e.raw_data}")
    print(f"Validation errors: {e.validation_errors}")

# Safe parsing (collects errors, continues parsing valid items)
valid_events, errors = CompassParser.parse_safe(CompassEvent, raw_events)
print(f"Parsed {len(valid_events)} events, {len(errors)} failed")
```

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=compass --cov-report=html

# Format code
poetry run black compass tests

# Lint code
poetry run flake8 compass tests

# Type checking
poetry run mypy compass
```

## Architecture

This package separates concerns:

1. **Client Layer** (`client.py`, `mock_client.py`): Handles HTTP communication and returns raw dicts
2. **Models Layer** (`models.py`): Defines Pydantic models for type-safe data structures
3. **Parser Layer** (`parser.py`): Validates and transforms raw data into typed models
4. **Application Layer**: Your code works with validated, type-safe models

This separation allows:
- Graceful handling of API changes at the parser layer
- Easy mocking and testing without hitting real APIs
- Type safety and IDE autocomplete throughout your application

## License

MIT License

## Contributing

Contributions welcome! Please ensure tests pass and code is formatted with black.

## Credits

Based on research from the [unofficial Compass API client](https://github.com/heheleo/compass-education).
