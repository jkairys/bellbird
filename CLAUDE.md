# Claude Code Context Guide for Bellweaver

This file documents key information about the Bellweaver project to help Claude Code understand the codebase, architecture, and development context.

## Project Overview

**Bellweaver** is a school calendar event aggregation and filtering tool that consolidates events from multiple sources (Compass, Class Dojo, HubHello, Xplore) and intelligently filters them based on relevance to specific children.

**Problem**: Parents receive overwhelming communication from multiple school sources with no unified view.

**Solution**: Single dashboard showing relevant calendar events for each child, powered by Claude API for intelligent filtering.

## Workflow

- When starting a new context / session, create a new branch on which to commit all changes
  - always start branches by pullling the latest from `main`
  - to determine branch name:
    - summarise the intent of the session into a git-friendly slug, e.g. `add-tabs-to-school-details` and
    - generate a string represntation of the current date in `YYYYMMDD-HH24MISS` format, e.g. `20251201-093322`
  - create a new branch using `<slug>-<date>` e.g. `add-tabs-to-school-details-20241201093322`
  - make changes to files interactively during the session
  - commit changes to the branch as you go - whenever you prompt for input, you should commit your changes before showing the prompt
- When you are done
  - run tests and fix if failing
  - update documentation
  - push the branch to the remote
  - create a pull request using the `gh` cli and let me review and merge it

## When waiting for input, or the task is complete

Use the command line below to notify the user every signle time Claude Code execution finishes, whether it's waiting for input or a task is complete.

```zsh
osascript -e 'display notification "Waiting for your input" with title "Claude Code" sound name "Glass"'
```

## Tech Stack

### Backend

- **Language**: Python
- **Package Manager**: Poetry

### Development Tools

- **Testing**: pytest + pytest-cov
- **Formatting**: black
- **Linting**: flake8
- **Type Checking**: mypy

## Project Structure & Key Directories

```
bellweaver/
├── backend/                      # Backend Python application
│   ├── bellweaver/                      # Main application code
│   │   ├── adapters/            # External API clients
│   │   │   ├── compass.py       # Real Compass API (HTTP-based, returns raw dicts)
│   │   │   └── compass_mock.py  # Synthetic data for testing
│   │   ├── parsers/             # Data validation layer
│   │   │   └── compass.py       # Transforms raw dicts → validated Pydantic models
│   │   ├── db/                  # Database layer
│   │   │   ├── database.py      # SQLAlchemy session, connection, schema
│   │   │   ├── models.py        # ORM models (Credential, ApiPayload)
│   │   │   └── credentials.py   # Encrypted credential storage/retrieval
│   │   ├── models/              # Pydantic/dataclass models
│   │   │   ├── compass.py       # Compass API data models (CompassEvent, CompassUser)
│   │   │   └── config.py        # User configuration models
│   │   ├── api/                 # Flask REST API
│   │   │   ├── routes.py        # Flask blueprint routes
│   │   │   └── schemas.py       # Request/response validation
│   │   ├── cli/                 # Command-line interface
│   │   │   ├── main.py          # Main CLI app and entry point
│   │   │   └── commands/        # CLI command modules
│   │   │       ├── mock.py      # Mock data management
│   │   │       └── compass.py   # Compass sync commands
│   │   └── app.py               # Flask application factory
│   ├── tests/                    # Unit & integration tests
│   ├── data/                     # Runtime data directory (gitignored)
│   │   └── bellweaver.db         # SQLite database created at runtime
│   ├── pyproject.toml           # Poetry configuration + tool settings
│   ├── .env.example             # Environment variables template
│   └── poetry.lock              # Locked dependencies
│
├── frontend/                    # Frontend application (TBD)
│   ├── src/                     # Source files
│   ├── public/                  # Static assets
│   └── README.md                # Frontend setup instructions
│
├── docs/                         # Project documentation
│   ├── index.md                  # Documentation index & current status
│   ├── quick-start.md           # 5-minute setup guide
│   └── architecture.md          # System design & technical decisions
├── .gitignore                   # Git ignore rules
└── README.md                    # Main project README
```

## Environment & Configuration

### Required Environment Variables

```bash
# Credentials for Compass API
COMPASS_USERNAME=""
COMPASS_PASSWORD=""
COMPASS_BASE_URL=""
```

See `backend/.env.example` for full template.

### Poetry Commands

All Poetry commands should be run from the `backend/` directory:

```bash
poetry install --with dev       # Install all dependencies
poetry run pytest               # Run tests
poetry add package-name         # Add production dependency
poetry add --group dev pkg      # Add dev dependency
poetry run bellweaver --help    # CLI help (when implemented)
```

### Files to Never Commit

- `backend/.env` (has API keys)
- `backend/.venv/` (virtual environment)
- `backend/data/bellweaver.db` (user data)
- `__pycache__/` and `.pytest_cache/`

### Commit Message Style

- Clear, imperative ("Add database models" not "Added")
- Reference the component ("db:" or "api:" prefix)
- Example: "db: add encrypted credential storage"

## Debugging & Troubleshooting

All troubleshooting commands should be run from the `backend/` directory:

## Documentation

For detailed information, see:

- **[docs/index.md](docs/index.md)** - Complete documentation index, current status, and roadmap
- **[docs/quick-start.md](docs/quick-start.md)** - Setup instructions
- **[docs/architecture.md](docs/architecture.md)** - System design and technical decisions

## Current Implementation Status

### What's Working ✅

1. **Compass HTTP Client** (`backend/bellweaver/adapters/compass.py`)
   - Direct HTTP authentication (no browser automation)
   - Fast performance (~1 second)
   - Returns raw dict responses
   - Integration tests passing

2. **Mock Client** (`backend/bellweaver/adapters/compass_mock.py`)
   - Realistic test data
   - Same interface as real client

3. **Compass Parser** (`backend/bellweaver/parsers/compass.py`)
   - Generic parser using Python TypeVar
   - Single `parse()` method works with any Pydantic model
   - Validates raw API responses into type-safe models
   - Comprehensive error handling
   - Safe parsing with partial success support
   - Full test coverage (22 tests passing)

4. **Pydantic Models** (`backend/bellweaver/models/compass.py`)
   - CompassEvent model with all fields
   - CompassUser model with all fields
   - Proper field aliases (camelCase → snake_case)

5. **Database Layer** (`backend/bellweaver/db/`)
   - SQLAlchemy 2.0 setup with proper DeclarativeBase
   - `database.py`: Engine, session management, init functions
   - `models.py`: ORM models for data persistence
     - **Batch**: Adapter method invocation tracking
       - Stores metadata about each adapter method call
       - Tracks adapter_id, method_name, and parameters (as JSON)
       - Acts as foreign key for related ApiPayload records
       - Supports cascade delete (deleting batch removes all payloads)
       - Auto-generated UUID primary keys
     - **ApiPayload**: Stores raw API responses as JSON with batch tracking
       - Flexible schema to handle API changes gracefully
       - Foreign key relationship to Batch model
       - Indexed by adapter_id, method_name, batch_id, created_at
       - Auto-generated UUID primary keys
     - **Credential**: Encrypted credential storage
       - Primary key on source (compass, classdojo, etc.)
       - Timestamps for created_at and updated_at
   - `credentials.py`: Credential encryption/decryption using Fernet
   - Foreign key constraints enabled in SQLite
   - Full test coverage (26 tests for database models)
   - All 75 tests passing

6. **LLM Filter** (`backend/bellweaver/filtering/llm_filter.py`)
   - Claude API integration
   - Not yet integrated into pipeline

7. **CLI Interface** (`backend/bellweaver/cli/`)
   - Typer-based command-line interface
   - `main.py`: Main CLI application entry point
   - `commands/mock.py`: Mock data management commands
   - `commands/compass.py`: Compass sync commands
     - **sync**: Syncs user details and calendar events from Compass to database
       - Creates separate Batch records to track each sync operation
       - Fetches user details for the authenticated user
       - Fetches calendar events for current calendar year or custom date range
       - Stores raw API responses in ApiPayload table
       - Usage: `poetry run bellweaver compass sync [--days N] [--limit N]`
   - All 75 tests passing

8. **Flask API** (`backend/bellweaver/app.py`)
   - Flask application factory pattern
   - REST API endpoints for accessing aggregated data
   - Routes implemented:
     - **GET /user**: Returns latest user details from Compass
       - Fetches most recent get_user_details batch
       - Parses payloads using CompassUser Pydantic model
       - Returns parsed JSON with batch metadata
   - Usage: `poetry run python -m bellweaver.app`
   - Environment variables:
     - `FLASK_DEBUG=true` to enable debug mode and reloader
   - Note: Debug reloader can cause database connection issues; disabled by default

### What's Not Built ⏳

- Additional Flask API routes (events, filtering)
- Web UI
- End-to-end pipeline integration

## References & Resources

- [Unofficial Compass API Client](https://github.com/heheleo/compass-education)
- [Anthropic Claude API Docs](https://docs.anthropic.com)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org)
- [Flask Documentation](https://flask.palletsprojects.com)
- [Poetry Documentation](https://python-poetry.org/docs)
