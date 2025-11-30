# Claude Code Context Guide for Bellweaver

This file documents key information about the Bellweaver project to help Claude Code understand the codebase, architecture, and development context.

## Project Overview

**Bellweaver** is a school calendar event aggregation and filtering tool that consolidates events from multiple sources (Compass, Class Dojo, HubHello, Xplore) and intelligently filters them based on relevance to specific children.

**Problem**: Parents receive overwhelming communication from multiple school sources with no unified view.

**Solution**: Single dashboard showing relevant calendar events for each child, powered by Claude API for intelligent filtering.

## Tech Stack

### Backend

- **Language**: Python 3.10+
- **Package Manager**: Poetry
- **Web Framework**: Flask
- **Database**: SQLite (local development)
- **ORM**: SQLAlchemy 2.0
- **Encryption**: cryptography (Fernet)
- **LLM Integration**: Anthropic Claude API

### Frontend

- **HTML/JS/CSS** - Simple vanilla JS (Phase 1)
- **Static assets** in `frontend/` directory

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
│   │   ├── filtering/           # LLM-based event filtering
│   │   │   └── llm_filter.py    # Claude API integration
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
├── frontend/                     # Frontend application (TBD)
│   ├── src/                     # Source files
│   ├── public/                  # Static assets
│   └── README.md                # Frontend setup instructions
│
├── docs/                         # Project documentation
├── .gitignore                   # Git ignore rules
└── README.md                    # Main project README
```

## Architecture & Data Flow

### Layered Architecture

```
CLI/Web UI
    ↓
Flask Routes / CLI Commands
    ↓
Filtering Layer (Claude API)
    ↓
Database Layer (SQLAlchemy)
    ├─ Adapters (Compass, etc.)
    └─ Encryption (Fernet)
```

## Environment & Configuration

### Required Environment Variables

```bash
CLAUDE_API_KEY                  # Anthropic API key (required)
BELLWEAVER_ENCRYPTION_KEY         # Fernet encryption key (auto-generated on first run)
FLASK_ENV=development           # Optional, defaults to production
FLASK_DEBUG=1                   # Optional, for development
DATABASE_URL=sqlite:///./data/bellweaver.db  # Optional, defaults as shown
```

See `.env.example` for full template.

### Poetry Commands

All Poetry commands should be run from the `backend/` directory:

```bash
cd backend
poetry install --with dev       # Install all dependencies
poetry run pytest               # Run tests
poetry run black src tests      # Format code
poetry run flake8 src tests     # Lint
poetry run mypy src             # Type check
poetry add package-name         # Add production dependency
poetry add --group dev pkg      # Add dev dependency
poetry run bellweaver --help      # CLI help (when implemented)
poetry run flask run            # Flask development server (when implemented)
```

## Phase 1 MVP Roadmap (10 Days)

### Days 1-2: Database Foundation

- [ ] Implement `backend/src/db/database.py` (SQLAlchemy session, schema creation)
- [ ] Implement `backend/src/db/models.py` (Credential, UserConfig, RawEvent, FilteredEvent, SyncMetadata)
- [ ] Implement `backend/src/db/credentials.py` (encrypted credential storage)

### Days 2-3: Testing Framework (Parallel)

- [ ] Implement `backend/src/adapters/compass_mock.py` (15-20 synthetic events)
- [ ] Add unit tests for mock adapter

### Days 3-5: Filtering & Real Integration

- [ ] Implement `backend/src/filtering/llm_filter.py` (Claude API integration)
- [ ] Implement `backend/src/adapters/compass.py` (real Compass API client)
- [ ] Test with real credentials

### Days 5-7: Web & CLI

- [ ] Implement `backend/src/cli.py` (argument parser, commands: --fetch, --filter, --full, --show-filtered)
- [ ] Implement `backend/src/app.py` (Flask app factory)
- [ ] Implement `backend/src/api/routes.py` (REST endpoints: /config, /sync, /events, /sync-status)
- [ ] Implement `backend/src/api/schemas.py` (request/response validation)

### Days 7-9: User Interface

- [ ] Implement `frontend/` application structure
- [ ] Implement onboarding form UI
- [ ] Implement event dashboard UI
- [ ] Implement basic styling and API integration

### Days 9-10: Integration & Polish

- [ ] End-to-end testing
- [ ] Error handling and edge cases
- [ ] Documentation
- [ ] Performance testing
- [ ] Final testing with real data

## Compass API Integration

**Approach**: Direct HTTP requests to Compass API (no browser automation)

**Authentication**:

1. POST credentials to `/login.aspx`
2. Capture cookies and session metadata
3. Reuse cookies for API calls via `requests.Session()`

**API Endpoint**: `POST /Services/Calendar.svc/GetCalendarEventsByUser`

**Payload Structure**:

```python
{
    'userId': int,
    'homePage': bool,
    'activityId': None,
    'locationId': None,
    'staffIds': None,
    'startDate': 'YYYY-MM-DD',
    'endDate': 'YYYY-MM-DD',
    'page': 1,
    'start': 0,
    'limit': 100
}
```

See `docs/COMPASS_PYTHON_CLIENT_PLAN.md` for full implementation details.

## Claude API Integration

**Model**: claude-opus-4-1-20250805 (or latest)

**Usage**: Filtering calendar events based on user config

**Prompt Structure**:

- Child profile (name, school, year level, class, interests)
- Filter rules (free text)
- Raw calendar events (JSON array)
- Task: Determine relevance and reasoning for each event

**Output Format**: JSON array with fields: event_id, title, date, is_relevant, reason, action_needed

See `backend/src/filtering/llm_filter.py` implementation for details.

## Documentation Files

All documentation is in the `docs/` directory except README.md and this file.

| File | Purpose | Read First? |
|------|---------|-------------|
| README.md | Project overview | ✅ Yes |
| docs/INDEX.md | Navigation guide | ✅ Yes |
| docs/NEXT_STEPS.md | Current priorities & roadmap | ✅ Yes |
| docs/IMPLEMENTATION_SUMMARY.md | What's working now | ✅ Yes |
| docs/QUICK_START.md | 5-minute setup guide | For setup |
| docs/MVP_ARCHITECTURE.md | System design & data flow | Before coding |
| docs/COMPASS_AUTHENTICATION_STRATEGIES.md | Compass auth approach | For Compass work |
| docs/COMPASS_USAGE_GUIDE.md | Using Compass client | For Compass work |
| CLAUDE.md | This file | For Claude context |

## Common Patterns & Conventions

### Database Access

```python
from src.db.database import get_session
from src.db.models import UserConfig

with get_session() as session:
    config = session.query(UserConfig).first()
```

### Encryption

```python
from src.db.credentials import CredentialManager

cred_manager = CredentialManager(session)
cred_manager.save_compass_credentials(username, password)
username, password = cred_manager.load_compass_credentials()
```

### LLM Filtering

```python
from src.filtering.llm_filter import LLMFilter

filter_engine = LLMFilter(api_key)
results = filter_engine.filter_events(raw_events, user_config)
```

### CLI Commands

All CLI commands should be run from the `backend/` directory:

```bash
cd backend
poetry run bellweaver --set-credentials compass --username X --password Y
poetry run bellweaver --set-config --child-name Sophia --year-level "Year 3" ...
poetry run bellweaver --fetch
poetry run bellweaver --filter
poetry run bellweaver --full
poetry run bellweaver --show-filtered
```

## Testing Strategy

### Unit Tests

- Test each adapter (mock and real Compass)
- Test filtering logic with mock data
- Test database operations (CRUD)
- Test credential encryption/decryption

### Integration Tests

- Test full pipeline: fetch → normalize → filter → display
- Test CLI with mock data
- Test Flask endpoints

### Test Data

- Use `CompassMockClient` for development
- Real Compass credentials for integration testing
- Synthetic user configs for filtering tests

## Git Workflow

### Repository Status

- **Current Branch**: main
- **Status**: Initial project structure, ready for implementation
- **Gitignore**: Properly configured for Python + project-specific files

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

### Poetry Issues

```bash
cd backend
poetry lock --refresh
poetry install --with dev
poetry cache clear . --all
```

### Database Issues

```bash
cd backend
rm data/bellweaver.db  # Reset database
poetry run pytest    # Verify tests pass
```

### Type Checking

```bash
cd backend
poetry run mypy src  # Full type check
```

### Code Quality

```bash
cd backend
poetry run black src tests       # Auto-format
poetry run flake8 src tests      # Check style
poetry run mypy src              # Check types
```

## Important Notes for Future Sessions

1. **MVP Timeline**: 10 days of focused development to working tool
2. **Priority**: Get something usable early (Days 1-6), polish later (Days 7-10)
3. **Testing**: Use mock data extensively during development
4. **Encryption**: Credentials stored encrypted in SQLite, key in .env
5. **API Key**: CLAUDE_API_KEY required in .env to run filtering
6. **Database**: SQLite for MVP, can migrate to Firestore/Cloud SQL in Phase 2
7. **Authentication**: Compass uses simple form-based auth (not OAuth)
8. **Compass API**: Returns events with various properties, normalize on access
9. **Mock Data**: Realistic synthetic events for testing, swap with real adapter easily
10. **Error Handling**: Gracefully handle API failures, missing credentials, malformed data

## Phase 2 Considerations

When expanding beyond Compass:

- Implement normalization layer for multi-source events
- Create adapter interface for Class Dojo, HubHello, Xplore
- Enhance filtering to handle cross-source event deduplication
- Advanced UI with tagging, date range filtering
- Consider Firestore/Cloud SQL for scalability
- Implement Google Calendar sync

## References & Resources

- [Anthropic Claude API Docs](https://docs.anthropic.com)
- [SQLAlchemy ORM Docs](https://docs.sqlalchemy.org)
- [Flask Documentation](https://flask.palletsprojects.com)
- [Poetry Documentation](https://python-poetry.org/docs)
- [cryptography.io - Fernet](https://cryptography.io/en/latest/fernet/)

---

**Last Updated**: November 22, 2025
**Created For**: Claude Code future sessions
**Project Status**: Ready for Phase 1 MVP implementation
**Next Priority**: Implement database layer (src/db/)
