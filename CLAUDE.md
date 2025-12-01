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
- **Web Framework**: Flask
- **Database**: SQLite with SQLAlchemy ORM
- **CLI**: Typer

### Frontend

- **Framework**: React 18
- **Build Tool**: Vite
- **Package Manager**: npm

### Deployment

- **Containerization**: Docker (multi-stage build)
- **Orchestration**: Docker Compose

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
│   │   │   ├── __init__.py      # Flask application factory
│   │   │   └── routes.py        # Domain-specific route handlers (user_bp, etc.)
│   │   └── cli/                 # Command-line interface
│   │       ├── main.py          # Main CLI app and entry point
│   │       └── commands/        # CLI command modules
│   │           ├── mock.py      # Mock data management
│   │           ├── compass.py   # Compass sync commands
│   │           └── api.py       # API server commands
│   ├── tests/                    # Unit & integration tests
│   ├── data/                     # Runtime data directory (gitignored)
│   │   └── bellweaver.db         # SQLite database created at runtime
│   ├── pyproject.toml           # Poetry configuration + tool settings
│   └── poetry.lock              # Locked dependencies
│
├── frontend/                    # Frontend React application
│   ├── src/                     # Source files
│   │   ├── components/          # React components
│   │   │   ├── Dashboard.jsx    # Main dashboard component
│   │   │   └── Dashboard.css    # Dashboard styles
│   │   ├── services/            # API service layer
│   │   │   └── api.js           # API client for backend
│   │   ├── App.jsx              # Root component
│   │   ├── main.jsx             # Entry point
│   │   └── index.css            # Global styles
│   ├── index.html               # HTML template
│   ├── vite.config.js           # Vite configuration with API proxy
│   ├── package.json             # npm dependencies
│   └── README.md                # Frontend setup instructions
│
├── docs/                         # Project documentation
│   ├── index.md                  # Documentation index & current status
│   ├── quick-start.md           # 5-minute setup guide
│   └── architecture.md          # System design & technical decisions
├── .env.example                 # Environment variables template (for Docker and local)
├── .gitignore                   # Git ignore rules
└── README.md                    # Main project README
```

## Environment & Configuration

### Environment Files

The project uses a single `.env` file in the repository root for both Docker and local development:

- **Location**: `.env` (in project root)
- **Template**: `.env.example` (in project root)
- **Usage**:
  - Docker Compose reads this file via `env_file: .env`
  - Local development can read from the same file
- **Setup**: Copy `.env.example` to `.env` and fill in your values

**Note:** The Docker setup mounts `backend/data/` as a volume, so the SQLite database is shared between Docker and local environments. You can use the same database whether running in Docker or locally.

### Required Environment Variables

```bash
# Compass API credentials (required)
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

# Database location (optional, defaults to data/bellweaver.db)
DATABASE_URL=sqlite:///./data/bellweaver.db
```

See `.env.example` in the project root for the full template.

### Poetry Commands

All Poetry commands should be run from the `backend/` directory:

```bash
poetry install --with dev       # Install all dependencies
poetry run pytest               # Run tests
poetry add package-name         # Add production dependency
poetry add --group dev pkg      # Add dev dependency
poetry run bellweaver compass sync  # Sync data from Compass
poetry run bellweaver api serve     # Start API server
```

### Docker Commands

All Docker commands should be run from the project root:

```bash
docker-compose build            # Build the container
docker-compose up -d            # Start in detached mode
docker-compose logs -f          # View logs
docker-compose down             # Stop and remove container

# Execute commands inside the container
docker exec -it bellweaver bellweaver compass sync
docker exec -it bellweaver bash
```

### Files to Never Commit

- `.env` (contains API keys and credentials)
- `backend/.venv/` (virtual environment)
- `backend/data/bellweaver.db` (user data)
- `frontend/node_modules/` (npm dependencies)
- `frontend/dist/` (built frontend files)
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
   - `commands/api.py`: API server management commands
     - **serve**: Starts the Flask API server
       - Supports custom host and port configuration
       - Debug mode with auto-reloader available
       - Usage: `poetry run bellweaver api serve [--host HOST] [--port PORT] [--debug]`
   - All 75 tests passing

8. **Flask API** (`backend/bellweaver/api/`)
   - Flask application factory pattern in modular structure
   - `__init__.py`: Application factory (create_app)
   - `routes.py`: Domain-specific route blueprints
   - REST API endpoints for accessing aggregated data
   - Routes implemented:
     - **GET /user**: Returns latest user details from Compass
       - Fetches most recent get_user_details batch
       - Parses payloads using CompassUser Pydantic model
       - Returns parsed JSON with batch metadata
     - **GET /events**: Returns calendar events from Compass
       - Fetches most recent get_events batch
       - Parses payloads using CompassEvent Pydantic model
       - Returns parsed JSON with batch metadata and event list
   - Usage:
     - **Recommended**: `poetry run bellweaver api serve [--debug]`
     - **Legacy**: `poetry run python -m bellweaver.app` (deprecated)
   - Note: Backward compatibility maintained via `bellweaver/app.py`

9. **React Frontend** (`frontend/`)
   - Vite-based React application
   - Dashboard component displaying user details and events
   - API service layer with error handling
   - Features:
     - Displays user name and email from /user endpoint
     - Shows first 10 upcoming calendar events from /events endpoint
     - Responsive design with dark/light mode support
     - Loading states and error handling
     - Event cards with time, date, location, and attendees
   - Development server with hot reload (port 3000)
   - API proxy configured to Flask backend (port 5000)
   - All 116 npm packages installed successfully

10. **Docker Deployment**
    - Multi-stage Dockerfile combining frontend and backend
    - `Dockerfile`: Builds React frontend in stage 1, copies into Flask static dir in stage 2
    - `docker-compose.yml`: Orchestration with volume mounts
    - Shared environment: `backend/data/` mounted so database is shared between Docker and local
    - Environment file: `.env.docker` mounted and used by container
    - Health checks configured
    - Single container serves both frontend (port 5000) and API (port 5000/api)
    - Can sync data either in Docker or locally - both write to same database

### What's Not Built ⏳

- Event filtering by child/relevance
- LLM-based event filtering integration
- End-to-end pipeline integration

## References & Resources

- [Unofficial Compass API Client](https://github.com/heheleo/compass-education)
- [Anthropic Claude API Docs](https://docs.anthropic.com)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org)
- [Flask Documentation](https://flask.palletsprojects.com)
- [Poetry Documentation](https://python-poetry.org/docs)
