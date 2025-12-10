# Compass Client

A Python client library for the Compass Education API with built-in mock data support for development and testing.

## Features

- **Real API Client**: Authenticate with and fetch data from Compass Education
- **Mock Client**: Use realistic sample data without credentials (for local dev & CI)
- **Factory Pattern**: Easily switch between real and mock modes via environment variable
- **Pydantic Models**: Type-safe validated data models for events and users
- **Parser**: Generic parser with safe parsing and error collection

## Installation

```bash
cd packages/compass-client
poetry install
```

## Usage

### Basic Usage

```python
from compass_client import create_client, CompassEvent, CompassUser, CompassParser

# Create client (mode determined by COMPASS_MODE env var, defaults to "real")
client = create_client(
    base_url="https://school.compass.education",
    username="your_username",
    password="your_password"
)

# Authenticate
client.login()

# Fetch data
user_data = client.get_user_details()
events_data = client.get_calendar_events(
    start_date="2025-01-01",
    end_date="2025-01-31",
    limit=100
)

# Parse into validated models
parser = CompassParser()
user = parser.parse(CompassUser, user_data)
events = parser.parse(CompassEvent, events_data)

# Clean up
client.close()
```

### Mock Mode (Local Development)

Set the environment variable:

```bash
export COMPASS_MODE=mock
```

Or pass explicitly:

```python
client = create_client(
    base_url="https://school.compass.education",
    username="dummy",
    password="dummy",
    mode="mock"
)
```

The mock client returns realistic sample data from `data/mock/` without making any network calls.

### Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `COMPASS_MODE` | `real` | Client mode: `real` or `mock` |
| `COMPASS_BASE_URL` | - | Compass instance URL (required for real mode) |
| `COMPASS_USERNAME` | - | Compass username (required for real mode) |
| `COMPASS_PASSWORD` | - | Compass password (required for real mode) |

## Mock Data

Mock data files are located in `data/mock/`:

- `compass_events.json` - Sample calendar events
- `compass_user.json` - Sample user details
- `schema_version.json` - Schema version metadata

### Refreshing Mock Data

To update mock data from a real Compass instance:

```bash
poetry run python -m compass_client.cli refresh-mock-data
```

This requires valid Compass credentials and sanitizes PII before saving.

## API Reference

### Classes

- `CompassClient` - Real HTTP client for Compass API
- `CompassMockClient` - Mock client using sample data
- `CompassEvent` - Pydantic model for calendar events
- `CompassUser` - Pydantic model for user details
- `CompassParser` - Generic parser for raw API responses

### Functions

- `create_client(base_url, username, password, mode=None)` - Factory function

### Exceptions

- `CompassClientError` - Base exception for client errors
- `CompassAuthenticationError` - Authentication failures
- `CompassParseError` - Data validation failures

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=compass_client

# Format code
poetry run black .

# Lint
poetry run flake8
```

## License

MIT
