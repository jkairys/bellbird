# Bellweaver Backend

This is the backend application for Bellweaver - a school calendar event aggregation and filtering tool that consolidates calendar events from multiple sources and intelligently filters them based on relevance to specific children.

## Overview

The Bellweaver package is the main application that consumes the `compass-client` package for Compass API integration. This package contains:

- **Database layer**: SQLite with SQLAlchemy ORM for storing events, user config, and credentials
- **API layer**: Flask REST API for frontend communication
- **CLI commands**: Command-line interface for syncing and managing data
- **Filtering logic**: Claude API integration for intelligent event filtering
- **Mappers**: Transform Compass events into Bellweaver domain models

## Architecture

```
bellweaver (this package)
    ↓ depends on
compass-client (independent package)
    ├── CompassClient (real API)
    ├── CompassMockClient (mock data)
    └── create_client() factory
```

**Key Benefits of Decoupled Architecture:**
- Use mock data for development without Compass credentials
- Independent testing of Compass integration
- Clear separation between API client and application logic
- Easier to add support for additional calendar sources

## Setup

### Prerequisites
- Python 3.11+
- Poetry (for dependency management)
- compass-client package (installed automatically as dependency)
- Compass account credentials (optional - only needed for real API mode)
- Claude API key (from Anthropic)

### Installation

#### Option 1: Install Both Packages (Recommended for Development)

```bash
# Install compass-client first
cd ../compass-client
poetry install --with dev

# Install bellweaver (includes compass-client as dependency)
cd ../bellweaver
poetry install --with dev
```

#### Option 2: Install Bellweaver Only

```bash
# From bellweaver package directory
cd packages/bellweaver
poetry install --with dev
```

**Note:** The `compass-client` package is automatically installed via Poetry path dependency.

### Environment Configuration

1. **Copy environment template** (from project root):
```bash
cp .env.example .env
```

2. **Edit `.env` with your configuration**:
```bash
# Compass API Mode
COMPASS_MODE=mock  # Use "real" for actual Compass API, "mock" for development

# Compass API credentials (only required when COMPASS_MODE=real)
COMPASS_USERNAME=your_compass_username
COMPASS_PASSWORD=your_compass_password
COMPASS_BASE_URL=https://your-school.compass.education

# Claude API Key (required)
CLAUDE_API_KEY=your-anthropic-api-key-here

# Database Encryption Key (auto-generated on first run if not provided)
BELLWEAVER_ENCRYPTION_KEY=will-be-auto-generated-on-first-run

# Flask Configuration (optional)
FLASK_ENV=development
FLASK_DEBUG=1
```

3. **Verify installation**:
```bash
# Verify compass-client is available
poetry run python -c "from compass_client import create_client; print('✓ compass-client available')"

# Run tests
poetry run pytest
```

## Using Compass Client Integration

### Import Pattern

```python
# Import from compass-client package (NOT from bellweaver)
from compass_client import create_client, CompassEvent, CompassParser

# Create client (mode determined by COMPASS_MODE environment variable)
client = create_client(
    base_url=os.getenv("COMPASS_BASE_URL"),
    username=os.getenv("COMPASS_USERNAME"),
    password=os.getenv("COMPASS_PASSWORD")
)

# Authenticate
client.login()

# Fetch data
events_data = client.get_calendar_events("2025-01-01", "2025-12-31", 100)

# Parse into validated models
parser = CompassParser()
events = parser.parse(CompassEvent, events_data)

# Use in Bellweaver application
for event in events:
    # Map to Bellweaver domain models
    bellweaver_event = compass_event_to_event(event)
    # ... save to database, filter, etc.
```

### Mock Mode vs Real Mode

#### Development with Mock Data (No Credentials Required)

```bash
# Set mock mode
export COMPASS_MODE=mock

# Start API server
poetry run bellweaver api serve

# All Compass API calls will use mock data from compass-client package
```

#### Production with Real API

```bash
# Set real mode
export COMPASS_MODE=real

# Ensure credentials are set in .env
# COMPASS_BASE_URL=https://yourschool.compass.education
# COMPASS_USERNAME=your_username
# COMPASS_PASSWORD=your_password

# Start API server
poetry run bellweaver api serve

# All Compass API calls will connect to real Compass API
```

### Configuration Precedence

The `create_client()` factory determines which client to use based on:

1. **Explicit `mode` parameter** (highest priority)
2. **`COMPASS_MODE` environment variable**
3. **Default value**: `"real"` (lowest priority)

```python
# Force mock mode regardless of environment
client = create_client(..., mode="mock")

# Use environment variable
client = create_client(...)  # Reads COMPASS_MODE

# Explicit override
client = create_client(..., mode="real")  # Always uses real API
```

## Usage

### CLI Commands

```bash
# Sync calendar events from Compass
poetry run bellweaver compass sync

# Sync with custom date range
poetry run bellweaver compass sync --days 30

# Start API server
poetry run bellweaver api serve

# Start with debug mode
poetry run bellweaver api serve --debug

# View available commands
poetry run bellweaver --help
```

### Running Tests

```bash
# Run all tests (uses mock mode automatically)
poetry run pytest

# Run with coverage
poetry run pytest --cov=bellweaver --cov-report=term-missing

# Run specific test file
poetry run pytest tests/integration/test_compass_integration.py -v

# Run integration tests that require real API (optional)
COMPASS_MODE=real poetry run pytest tests/integration/ -v
```

### Code Quality

```bash
# Format code (Black)
poetry run black bellweaver tests

# Lint (Flake8)
poetry run flake8 bellweaver tests

# Type check (mypy)
poetry run mypy bellweaver
```

## Project Structure

```
bellweaver/
├── bellweaver/               # Main Python package
│   ├── __init__.py
│   ├── cli/                  # CLI interface
│   │   ├── main.py
│   │   └── commands/
│   │       ├── compass.py    # Uses compass_client
│   │       ├── api.py
│   │       └── mock.py
│   │
│   ├── db/                   # Database layer
│   │   ├── database.py       # SQLAlchemy connection & schema
│   │   ├── credentials.py    # Encrypted credential storage
│   │   └── models.py         # ORM models
│   │
│   ├── api/                  # REST API (Flask)
│   │   ├── __init__.py       # Flask app factory
│   │   └── routes.py         # Route handlers (uses compass_client)
│   │
│   ├── filtering/            # Event filtering & enrichment
│   │   └── llm_filter.py     # Claude API filtering logic
│   │
│   ├── mappers/              # Domain model transformations
│   │   └── compass.py        # compass_client → bellweaver models
│   │
│   └── models/               # Bellweaver domain models
│       └── config.py
│
├── tests/                    # Unit & integration tests
│   ├── unit/
│   ├── integration/
│   │   └── test_compass_integration.py  # Tests compass_client usage
│   └── conftest.py           # Fixtures (sets COMPASS_MODE=mock)
│
├── data/                     # Data directory (gitignored)
│   └── bellweaver.db         # SQLite database
│
├── pyproject.toml            # Poetry configuration with compass-client dependency
└── README.md                 # This file
```

## Troubleshooting

### Issue: "Module 'compass_client' not found"

**Cause:** compass-client package not installed or not in Python path.

**Solution:**
```bash
# Navigate to compass-client and install it
cd ../compass-client
poetry install --with dev

# Then install bellweaver
cd ../bellweaver
poetry install --with dev

# Verify both packages are installed
poetry run python -c "import compass_client, bellweaver; print('✓ Both packages installed')"
```

### Issue: "Import error" when importing from compass_client

**Cause:** Incorrect import path or package not installed.

**Solution:**
```python
# ✓ CORRECT: Import from compass_client package
from compass_client import create_client, CompassEvent, CompassParser

# ✗ WRONG: Don't import from bellweaver.adapters
# from bellweaver.adapters.compass import CompassClient  # OLD PATTERN
```

### Issue: Tests failing with "Compass authentication failed"

**Cause:** Tests trying to connect to real API instead of using mock mode.

**Solution:**
```bash
# Check test fixtures set COMPASS_MODE=mock
cat tests/conftest.py | grep COMPASS_MODE

# Ensure .env.test exists with COMPASS_MODE=mock
echo "COMPASS_MODE=mock" > .env.test

# Run tests
poetry run pytest
```

### Issue: "Mock data files not found" at startup

**Cause:** compass-client mock data missing.

**Solution:**
```bash
# Verify compass-client mock data exists
ls -la ../compass-client/data/mock/

# Expected files:
# - compass_events.json
# - compass_user.json
# - schema_version.json

# If missing, refresh mock data (requires real Compass credentials)
cd ../compass-client
poetry run python -m compass_client.cli refresh-mock-data \
    --base-url "$COMPASS_BASE_URL" \
    --username "$COMPASS_USERNAME" \
    --password "$COMPASS_PASSWORD"
```

### Issue: "ValidationError" when parsing Compass data

**Cause:** Compass API response doesn't match Pydantic models.

**Solution:**
```bash
# Check if using outdated mock data
cd ../compass-client
cat data/mock/schema_version.json

# Refresh mock data from real API
poetry run python -m compass_client.cli refresh-mock-data

# If issue persists with real API, check Compass API version changes
```

### Issue: Cannot switch between mock and real modes

**Cause:** Environment variable not being read or cached.

**Solution:**
```bash
# Check current mode
echo $COMPASS_MODE

# Explicitly set mode
export COMPASS_MODE=mock  # or "real"

# Restart application to pick up environment changes
poetry run bellweaver api serve

# Or set in code explicitly
client = create_client(..., mode="mock")  # Force mock mode
```

### Issue: Poetry dependency resolution fails

**Cause:** Path dependency to compass-client not resolving.

**Solution:**
```bash
# Verify compass-client path is correct in pyproject.toml
grep compass-client pyproject.toml

# Expected:
# compass-client = {path = "../compass-client", develop = true}

# Clear Poetry cache and reinstall
poetry cache clear . --all
poetry lock --no-update
poetry install --with dev
```

## Development Workflow

### 1. Local Development with Mock Data (Docker)

When using `docker-compose up`, `COMPASS_MODE` is automatically set to `mock` in the container's environment via `docker-compose.yml`.

```bash
# Ensure docker-compose is up (this will start in mock mode by default)
docker-compose up -d

# All Compass data comes from compass-client mock files
# Access API at http://localhost:5000
```

To run with real data in Docker, you can override `COMPASS_MODE` in your local `.env` file or directly modify `docker-compose.yml`.

```bash
# Example: Temporarily set COMPASS_MODE to real via .env
# In your .env file (ensure it's sourced by docker-compose, or pass directly):
# COMPASS_MODE=real
# COMPASS_USERNAME=your_username
# COMPASS_PASSWORD=your_password
#
# Then rebuild and restart (if .env changed)
# docker-compose up -d --build
```

### 2. Testing with Real Compass API

```bash
# Set real mode and ensure credentials are in .env
export COMPASS_MODE=real

# Start API server
poetry run bellweaver api serve

# Test with real data
curl http://localhost:5000/user
curl http://localhost:5000/events

# Data fetched from actual Compass API
```

### 3. Running CI Locally

```bash
# CI always uses mock mode
export COMPASS_MODE=mock

# Run tests
poetry run pytest --cov=bellweaver

# All tests use mock compass-client (no real API calls)
```

## Documentation

- **[compass-client README](../compass-client/README.md)** - Compass API client documentation
- **[Root README](../../README.md)** - Complete project documentation
- **[Architecture Docs](../../docs/architecture.md)** - System design and technical decisions
- **[Quick Start Guide](../../docs/quick-start.md)** - Get started in 5 minutes

## Contributing

This package is part of the Bellweaver monorepo. See the main repository for contribution guidelines.

## License

TBD
