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

✅ **Compass API Decoupling**: Compass API integration has been successfully decoupled into an independent `compass-client` package.
✅ **Mock Data Infrastructure**: Full mock data support enables local development and CI/CD testing without real Compass credentials.
✅ **Monorepo Structure**: The project is now organized as a multi-package monorepo with `bellweaver` and `compass-client` as independent Python packages.
✅ **CI/CD Optimization**: GitHub Actions workflows are configured for selective testing, improving efficiency.
⏳ **In Progress**: Database integration, advanced API routes, event filtering pipeline, and comprehensive documentation updates.

See [docs/index.md](docs/index.md) for detailed status and [docs/migration-compass-decoupling.md](docs/migration-compass-decoupling.md) for migration details.

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

### Root-Level Files

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
│   ├── docker-deployment.md
│   └── migration-compass-decoupling.md # New migration guide
├── .github/workflows/          # CI/CD pipelines
│   ├── test-compass.yml        # CI for compass-client only
│   └── test-bellweaver.yml     # CI for bellweaver only
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── docker-compose.yml          # Docker deployment
├── Dockerfile                  # Docker build configuration
└── README.md                   # This file
```

## Quick Start

Get started in 5 minutes! For full details, see **[docs/quick-start.md](docs/quick-start.md)**.

### Zero to Running in 3 Commands

```bash
# 1. Clone the repository
git clone https://github.com/jkairys/bellweaver.git && cd bellweaver

# 2. Configure environment
cp .env.example .env  # Edit .env if needed, defaults to mock mode

# 3. Install all dependencies and run tests
task setup && task test
```

**Expected result**: All tests pass, you're ready to develop! 🚀

<details>
<summary>Manual installation (without Task)</summary>

```bash
# Install compass-client
cd packages/compass-client && poetry install --with dev

# Install bellweaver
cd ../bellweaver && poetry install --with dev

# Install frontend
cd ../../frontend && npm install

# Run tests
cd ../packages/bellweaver && poetry run pytest -v
```
</details>

## Architecture Overview

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
- **Decoupled**: `compass-client` can be developed/tested independently
- **Mock Support**: Full development possible without Compass credentials
- **CI-Friendly**: Tests run in mock mode, no geo-blocking issues
- **Testable**: Each package has its own isolated test suite
- **Clear Boundaries**: API client logic separated from application logic

## Usage

For detailed usage instructions, including running in mock/real modes, refreshing mock data, and testing, please refer to the **[Quick Start Guide](docs/quick-start.md)**.

### Development Mode

Start both frontend and backend development servers:

```bash
task dev
```

This starts:
- Frontend dev server at `http://localhost:5173`
- Backend API server at `http://localhost:5000`

### CLI Mode

```bash
# Using Poetry directly (from packages/bellweaver/)
cd packages/bellweaver
poetry run bellweaver compass sync    # Sync data from Compass
poetry run bellweaver mock --help     # Manage mock data
```

### API Server Only

```bash
# Using Task (from project root)
task backend:serve

# Or using Poetry (from packages/bellweaver/)
cd packages/bellweaver
poetry run bellweaver api serve
```

## Development

For a complete development workflow, including local setup, testing, and debugging, see the **[Quick Start Guide](docs/quick-start.md)**.

### Running Tests

```bash
# Using Task (from project root) - Recommended
task test              # Run all tests across all packages
task test:unit         # Run unit tests only (excludes integration tests)

# Or run tests for specific packages
task backend:bellweaver:test
task backend:compass-client:test
```

<details>
<summary>Manual testing with Poetry</summary>

```bash
# Run tests for bellweaver (uses mock compass-client by default)
cd packages/bellweaver && poetry run pytest

# Run tests for compass-client
cd packages/compass-client && poetry run pytest -m "not integration"

# Run integration tests (requires real Compass credentials)
cd packages/compass-client && poetry run pytest -m "integration"
```

</details>

### Linting and Formatting

```bash
# Using Task (from project root) - Recommended
task format            # Auto-fix formatting issues (ruff --fix, black)
task lint              # Check for linting issues (ruff, flake8, mypy)
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

This project is under active development. For detailed next steps and task breakdowns, please refer to the **[Project Documentation](docs/index.md)**.

## Contributing

We welcome contributions! If you're interested in contributing, please fork the repository and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
