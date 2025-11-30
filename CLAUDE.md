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
  - push the branch to the remote and let me review and merge it

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
│   ├── src/                      # Main application code
│   │   ├── adapters/            # External API clients
│   │   │   ├── compass.py       # Real Compass API (HTTP-based, no browser automation)
│   │   │   └── compass_mock.py  # Synthetic data for testing
│   │   ├── db/                  # Database layer
│   │   │   ├── database.py      # SQLAlchemy session, connection, schema
│   │   │   ├── models.py        # ORM models (Credential, UserConfig, RawEvent, FilteredEvent, SyncMetadata)
│   │   │   └── credentials.py   # Encrypted credential storage/retrieval
│   │   ├── models/              # Pydantic/dataclass models
│   │   │   └── config.py        # User configuration models
│   │   ├── api/                 # Flask REST API
│   │   │   ├── routes.py        # Flask blueprint routes
│   │   │   └── schemas.py       # Request/response validation
│   │   ├── cli.py               # [TODO] Command-line interface
│   │   └── app.py               # [TODO] Flask application factory
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

1. **Compass HTTP Client** (`backend/src/adapters/compass.py`)
   - Direct HTTP authentication (no browser automation)
   - Fast performance (~1 second)
   - Integration tests passing

2. **Mock Client** (`backend/src/adapters/compass_mock.py`)
   - Realistic test data
   - Same interface as real client

3. **LLM Filter** (`backend/src/filtering/llm_filter.py`)
   - Claude API integration
   - Not yet integrated into pipeline

4. **Credential Manager** (`backend/src/db/credentials.py`)
   - Fernet encryption
   - Not yet integrated with database

### What's Not Built ⏳

- Database layer (SQLAlchemy models, schema)
- Flask API routes
- Web UI
- CLI interface
- End-to-end pipeline integration

## References & Resources

- [Unofficial Compass API Client](https://github.com/heheleo/compass-education)
- [Anthropic Claude API Docs](https://docs.anthropic.com)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org)
- [Flask Documentation](https://flask.palletsprojects.com)
- [Poetry Documentation](https://python-poetry.org/docs)
