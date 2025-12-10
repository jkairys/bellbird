# Bellweaver

A unified school calendar event aggregation and filtering tool that consolidates events from multiple sources (Compass, Class Dojo, HubHello, Xplore) and intelligently filters them based on relevance to specific children.

## Documentation

- **[Documentation Index](docs/index.md)** - Complete documentation and current status
- **[Quick Start](docs/quick-start.md)** - Get started in 5 minutes
- **[Architecture](docs/architecture.md)** - System design and technical decisions
- **[Docker Deployment](docs/docker-deployment.md)** - Deploy with Docker (frontend + backend in one container)

## Project Vision

Parents receive overwhelming amounts of communication from multiple school sources. Bellweaver solves this by:

- **Consolidating** events from multiple calendar systems into one place
- **Filtering** for relevant events based on child/year level/event type
- **Providing** advance notifications and a clear "next 2 weeks" view
- **Syncing** to Google Calendar for easy mobile access

## Current Status

✅ **Compass HTTP Client** - Direct HTTP authentication working (~1 second)
✅ **Tests Passing** - Integration tests with real credentials working
✅ **Mock Client** - Realistic test data for development
⏳ **In Progress** - Database integration, API routes, and filtering pipeline

See [docs/index.md](docs/index.md) for detailed status.

## MVP Scope (Phase 1)

The MVP focuses on **Compass only** for local development:

- Fetch calendar events from Compass
- Filter events intelligently using Claude API
- Provide both CLI and Web UI interfaces
- Store data locally in SQLite with encrypted credentials

## Project Structure

This is a **monorepo** containing two independent Python packages:

### 1. compass-client Package (Independent Library)

Standalone Compass Education API client with mock data support. Can be used independently or as a dependency.

```
packages/compass-client/
├── compass_client/              # Package source
│   ├── __init__.py             # Public API exports
│   ├── client.py               # Real Compass HTTP client
│   ├── mock_client.py          # Mock client with sample data
│   ├── models.py               # Pydantic models (CompassEvent, CompassUser)
│   ├── parser.py               # Generic validation parser
│   ├── factory.py              # create_client() factory function
│   ├── exceptions.py           # Custom exceptions
│   └── cli/                    # CLI commands
│       └── refresh_mock_data.py
├── data/mock/                  # Mock data (committed to repo)
│   ├── compass_events.json
│   ├── compass_user.json
│   └── schema_version.json
├── tests/                      # compass-client tests
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── pyproject.toml              # Package dependencies
└── README.md                   # Package documentation
```

### 2. bellweaver Package (Main Application)

Event aggregation and filtering application. Depends on compass-client package.

```
packages/bellweaver/
├── bellweaver/                 # Main Python package
│   ├── __init__.py
│   ├── cli/                    # CLI interface
│   │   ├── main.py
│   │   └── commands/
│   │       ├── compass.py      # Uses compass_client
│   │       ├── api.py
│   │       └── mock.py
│   │
│   ├── db/                     # Database layer
│   │   ├── database.py         # SQLAlchemy connection & schema
│   │   ├── credentials.py      # Encrypted credential storage
│   │   └── models.py           # ORM models
│   │
│   ├── api/                    # REST API (Flask)
│   │   ├── __init__.py         # Flask app factory
│   │   └── routes.py           # Route handlers (uses compass_client)
│   │
│   ├── filtering/              # Event filtering & enrichment
│   │   └── llm_filter.py       # Claude API filtering logic
│   │
│   ├── mappers/                # Domain model transformations
│   │   └── compass.py          # compass_client → bellweaver models
│   │
│   └── models/                 # Bellweaver domain models
│       └── config.py
│
├── tests/                      # Bellweaver tests
│   ├── unit/
│   ├── integration/
│   │   └── test_compass_integration.py  # Tests compass_client usage
│   └── conftest.py             # Fixtures (sets COMPASS_MODE=mock)
│
├── data/                       # Data directory (gitignored)
│   └── bellweaver.db           # SQLite database
│
├── pyproject.toml              # Includes compass-client dependency
└── README.md                   # Package documentation
```

### Supporting Files

```
bellweaver/                     # Project root
├── packages/                   # Python packages (see above)
├── frontend/                   # React frontend application
│   ├── src/
│   ├── public/
│   └── README.md
├── docs/                       # Project documentation
│   ├── index.md
│   ├── quick-start.md
│   ├── architecture.md
│   └── docker-deployment.md
├── .github/workflows/          # CI/CD pipelines
│   ├── test-compass.yml        # CI for compass-client only
│   └── test-bellweaver.yml     # CI for bellweaver only
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── docker-compose.yml          # Docker deployment
└── README.md                   # This file
```

### Architecture Overview

```
┌─────────────────────────────────────────┐
│  bellweaver (Main Application)          │
│  ├── Flask REST API                     │
│  ├── Database (SQLite + SQLAlchemy)     │
│  ├── CLI Commands                       │
│  ├── LLM Filtering (Claude API)         │
│  └── Event Mappers                      │
│                                          │
│  Depends on ↓                            │
└─────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  compass-client (Independent Package)   │
│  ├── CompassClient (Real API)           │
│  ├── CompassMockClient (Mock Data)      │
│  ├── create_client() Factory            │
│  ├── Pydantic Models                    │
│  └── Generic Parser                     │
│                                          │
│  Mode: "real" or "mock" (via env var)   │
└─────────────────────────────────────────┘
```

**Key Benefits:**
- **Decoupled**: compass-client can be developed/tested independently
- **Mock Support**: Full development possible without Compass credentials
- **CI-Friendly**: Tests run in mock mode, no geo-blocking issues
- **Testable**: Each package has its own isolated test suite
- **Clear Boundaries**: API client logic separated from application logic

## Deployment Options

### Option 1: Docker (Recommended - Easiest)

See **[Docker Deployment Guide](docs/docker-deployment.md)** for complete instructions.

The Docker setup uses a multi-stage build that packages both frontend and backend into a single container. The database and environment file are mounted as volumes, so they're shared between Docker and local development.

Quick start:

```bash
# Copy environment template
cp .env.example .env

# Build and start the services
docker-compose build
docker-compose up -d

# By default, COMPASS_MODE is set to 'mock' in docker-compose.yml for convenience.
# To run in 'real' mode, you can override this in your .env file or directly in docker-compose.yml.
# Ensure your Compass credentials are set in .env if running in 'real' mode.

# Sync data from Compass (can run in Docker or locally)
docker exec -it bellweaver bellweaver compass sync

# Access at http://localhost:5000
```

**Key features:**
- Single container serves both frontend and backend
- Database persists in `packages/bellweaver/data/` (mounted volume)
- Same environment and database used whether running in Docker or locally
- No data migration needed when switching between Docker and local development

### Option 2: Local Development

#### Prerequisites

- Python 3.10+
- Node.js 20+
- Poetry (for dependency management)
- Compass account credentials

#### Installation

1. **Clone the repository**:

```bash
git clone <repo-url>
cd bellweaver
```

2. **Set up the Python packages**:

```bash
# Install compass-client package first
cd packages/compass-client
poetry install --with dev

# Install bellweaver package (includes compass-client as dependency)
cd ../bellweaver
poetry install --with dev

# Verify both packages are installed
poetry run python -c "from compass_client import create_client; print('✓ compass-client available')"
```

3. **Set up the frontend**:

```bash
cd ../../frontend
npm install
```

4. **Set up environment variables**:

```bash
# From project root
cp .env.example .env
```

Then edit `.env` with your actual values:

```bash
# Compass API Mode (mock for development, real for production)
COMPASS_MODE=mock  # Start with mock mode (no credentials needed)

# Compass credentials (only required when COMPASS_MODE=real)
COMPASS_USERNAME=your_compass_username
COMPASS_PASSWORD=your_compass_password
COMPASS_BASE_URL=https://your-school.compass.education

# Claude API Key (required for filtering)
CLAUDE_API_KEY=your-anthropic-api-key
```

5. **Verify installation**:

```bash
cd packages/bellweaver
poetry run pytest  # All tests use mock mode by default
```

#### Running in Development Mode

Run frontend and backend separately with hot reload:

```bash
# Terminal 1: Start backend API
cd packages/bellweaver
poetry run bellweaver api serve --debug

# Terminal 2: Start frontend dev server
cd frontend
npm run dev
```

Access:
- Frontend: http://localhost:3000 (with hot reload)
- Backend API: http://localhost:5000/api/*

## Usage

### CLI Mode

Run CLI commands from `packages/bellweaver/` directory:

**Sync from Compass**:

```bash
cd packages/bellweaver
poetry run bellweaver compass sync
```

**Manage mock data** (for testing without credentials):

```bash
cd packages/bellweaver
poetry run bellweaver mock update
```

**View CLI help**:

```bash
cd packages/bellweaver
poetry run bellweaver --help
poetry run bellweaver compass --help
poetry run bellweaver api --help
```

### Web UI

**Start the Flask API server** (from `packages/bellweaver/`):

```bash
cd packages/bellweaver
poetry run bellweaver api serve
```

Then open <http://localhost:5000> in your browser.

Features:

- Onboarding form for credentials and child profile
- Dashboard showing next 2 weeks of relevant events
- Sync button to fetch & filter new events
- Simple, clean interface

## Development

All development commands should be run from the `packages/bellweaver/` directory:

### Running Tests

```bash
cd packages/bellweaver
poetry run pytest
```

### Code Quality

```bash
cd packages/bellweaver
poetry run black bellweaver tests
poetry run flake8 bellweaver tests
poetry run mypy bellweaver
```

### Development Mode

```bash
cd packages/bellweaver
export FLASK_ENV=development
poetry run flask run --debug
```

## Key Design Decisions

1. **No Browser Automation**: Unlike the JS library, our Python client uses direct HTTP requests to Compass, avoiding Puppeteer overhead.

2. **Local-First**: MVP runs on a single machine with local SQLite database. No GCP/Cloud setup required initially.

3. **Encrypted Credentials**: Uses `cryptography.fernet` for symmetric encryption. Keys stored in `.env` (never committed).

4. **LLM-Based Filtering**: Uses Claude API to intelligently filter events based on free-text rules and child profile.

5. **Mock Data for Development**: `CompassMockClient` provides realistic synthetic events for testing without real credentials.

## Architecture Highlights

### Data Flow

1. **Fetch**: Compass API → Raw events cached in SQLite
2. **Filter**: Raw events + child profile + rules → Claude API → Filtered results
3. **Display**: Filtered events shown in CLI or Web UI

### Database Schema

- `credentials`: Encrypted Compass login credentials
- `user_config`: Child profile and filter rules
- `raw_events_cache`: Unmodified Compass API responses
- `filtered_events`: Claude-filtered results with reasoning
- `sync_metadata`: Sync status and timestamps

## Next Steps

### Phase 1 (MVP - Current Phase)

- [x] Project scaffold with Poetry
- [x] Compass HTTP client
- [x] Mock Compass adapter
- [x] LLM filter implementation
- [x] Credential encryption
- [x] Integration tests
- [ ] Database layer integration
- [ ] CLI interface
- [ ] Flask backend API
- [ ] Web UI

### Phase 2 (Multi-Source)

- [ ] Add normalization layer
- [ ] Integrate Class Dojo
- [ ] Integrate HubHello
- [ ] Integrate Xplore
- [ ] Advanced filtering UI

## Troubleshooting

### Poetry Issues

```bash
# Update lock file
poetry lock --refresh

# Clear cache
poetry cache clear . --all
```

### Database Reset

```bash
rm packages/bellweaver/data/bellweaver.db
```

## Contributing

This is a personal project, but feel free to fork and adapt!

## License

TBD

## References

Keeping these for later if required:

- <https://github.com/VeNoMouS/cloudscraper>
