# Bellweaver Documentation

**Last Updated:** December 1, 2025

## Project Overview

Bellweaver is a school calendar event aggregation and filtering tool that consolidates events from multiple sources and intelligently filters them based on relevance to specific children.

**Problem:** Parents receive overwhelming communication from multiple school sources (Compass, Class Dojo, HubHello, Xplore) with no unified view.

**Solution:** Single dashboard showing relevant calendar events for each child, powered by Claude API for intelligent filtering.

## Quick Links

- **[Quick Start Guide](quick-start.md)** - Get up and running in 5 minutes
- **[Architecture](architecture.md)** - System design and technical decisions
- **[Main README](../README.md)** - Project overview

## Current Status

### What's Working ✅

1. **Compass HTTP Client** (`backend/src/adapters/compass.py`)
   - Direct HTTP authentication (no browser automation)
   - Calendar event fetching from Compass API
   - Session management with cookies
   - Fast performance (~1 second total)
   - Integration tests passing

2. **Mock Client** (`backend/src/adapters/compass_mock.py`)
   - Realistic synthetic test data
   - Same interface as real client
   - No credentials required

3. **LLM Filter** (`backend/src/filtering/llm_filter.py`)
   - Claude API integration implemented
   - Event filtering and summarization
   - Not yet integrated into pipeline

4. **Credential Manager** (`backend/src/db/credentials.py`)
   - Fernet encryption implemented
   - Not yet integrated with database

### What's Not Built ⏳

- Database layer (SQLAlchemy models, schema)
- Flask API routes
- Web UI
- CLI interface
- End-to-end pipeline integration

## Tech Stack

### Backend
- **Language:** Python 3.10+
- **Package Manager:** Poetry
- **Web Framework:** Flask (planned)
- **Database:** SQLite (planned)
- **ORM:** SQLAlchemy (planned)
- **Encryption:** cryptography (Fernet)
- **LLM Integration:** Anthropic Claude API

### Development Tools
- **Testing:** pytest + pytest-cov
- **Formatting:** black
- **Linting:** flake8
- **Type Checking:** mypy

## Project Structure

```
bellweaver/
├── backend/
│   ├── src/
│   │   ├── adapters/
│   │   │   ├── compass.py         # ✅ HTTP-based Compass client
│   │   │   └── compass_mock.py    # ✅ Mock client for testing
│   │   ├── filtering/
│   │   │   └── llm_filter.py      # ✅ Claude API filtering
│   │   ├── db/
│   │   │   └── credentials.py     # ✅ Credential encryption
│   │   ├── api/                   # ⏳ TODO - Flask routes
│   │   └── models/                # ⏳ TODO - Data models
│   ├── tests/
│   │   ├── test_compass_client_real.py   # ✅ Integration tests
│   │   └── test_fixtures.py              # ✅ Fixture tests
│   ├── pyproject.toml             # Poetry configuration
│   └── .env.example               # Environment template
├── docs/
│   ├── index.md                   # This file
│   ├── quick-start.md            # Setup guide
│   └── architecture.md           # Technical design
└── README.md                      # Project overview
```

## Development Workflow

### Setup

```bash
cd backend
poetry install --with dev
cp .env.example .env
# Edit .env with your credentials
```

### Testing

```bash
cd backend
poetry run pytest -v                                    # All tests
poetry run pytest tests/test_compass_client_real.py -v  # Integration tests
```

### Code Quality

```bash
cd backend
poetry run black src tests    # Format
poetry run flake8 src tests   # Lint
poetry run mypy src          # Type check
```

## Environment Configuration

Required environment variables (in `backend/.env`):

```bash
# Compass credentials
COMPASS_USERNAME=your_compass_username
COMPASS_PASSWORD=your_compass_password
COMPASS_BASE_URL=https://your-school.compass.education

# Claude API (optional, for filtering features)
CLAUDE_API_KEY=sk-ant-xxxxx

# Encryption key (auto-generated on first run)
BELLWEAVER_ENCRYPTION_KEY=
```

See `backend/.env.example` for full template.

## Development Roadmap

### Phase 1: MVP Foundation (Current Phase)

**Completed:**
- [x] Compass HTTP client implementation
- [x] Mock client for testing
- [x] LLM filter implementation
- [x] Credential encryption implementation
- [x] Integration tests
- [x] Project structure and tooling

**Next Steps:**
- [ ] Database layer (SQLAlchemy models and schema)
- [ ] Flask API routes
- [ ] CLI interface
- [ ] Web UI (basic configuration and event display)
- [ ] End-to-end pipeline integration
- [ ] Full workflow testing

### Phase 2: Multi-Source Support (Future)

- [ ] Class Dojo adapter
- [ ] HubHello adapter
- [ ] Xplore adapter
- [ ] Event normalization layer
- [ ] Advanced filtering UI
- [ ] Improved styling

### Phase 3: Advanced Features (Future)

- [ ] Google Calendar sync
- [ ] Email/SMS notifications
- [ ] Scheduling and automation
- [ ] Multi-user support
- [ ] Cloud deployment (GCP)
- [ ] Mobile app

## Key Technical Decisions

### HTTP Client vs Browser Automation

**Decision:** Use HTTP client with direct requests

**Rationale:**
- Cloudflare blocks browser automation (even with stealth)
- HTTP client is faster (~1s vs ~10-15s)
- Simpler deployment (no browser dependencies)
- More reliable (fewer moving parts)
- Better Cloudflare bypass

### SQLite vs Cloud Database

**Decision:** Start with SQLite for MVP

**Rationale:**
- No server setup required
- Simple file-based storage
- Good enough for single-user local development
- Easy migration path to PostgreSQL/Cloud SQL later

### Fernet Encryption

**Decision:** Use symmetric encryption for credentials

**Rationale:**
- Simple and built-in to Python cryptography
- Suitable for local credential storage
- Key stored in environment (not in code)
- Good enough for single-user MVP

## Testing Strategy

### Integration Tests
- Real Compass authentication
- Calendar event fetching
- Various date ranges
- Error handling

### Unit Tests (Planned)
- Database operations
- Credential encryption/decryption
- LLM filtering logic
- API endpoints

### Test Data
- Mock client with realistic synthetic events
- Real Compass credentials for integration testing
- Synthetic user configs for filtering tests

## Troubleshooting

### Poetry Issues

```bash
cd backend
poetry lock --refresh
poetry install --with dev
poetry cache clear . --all
```

### Test Failures

```bash
# Verify .env has correct credentials
cat backend/.env

# Ensure you're in backend directory
cd backend
poetry run pytest -v
```

### Virtual Environment Issues

```bash
cd backend
poetry env remove python
poetry install --with dev
```

## Git Workflow

### Current Status
- **Branch:** main
- **Recent Work:** Compass client implementation and testing

### Never Commit
- `backend/.env` (contains credentials)
- `backend/.venv/` (virtual environment)
- `backend/data/` (user data and database)
- `__pycache__/` and `.pytest_cache/`

### Commit Style
- Clear, imperative tense
- Component prefix (e.g., "adapters:", "db:", "docs:")
- Example: "adapters: add HTTP-based Compass client"

## Common Tasks

### Adding Dependencies

```bash
cd backend
poetry add package-name                # Production
poetry add --group dev package-name    # Development
```

### Running Specific Tests

```bash
cd backend
poetry run pytest tests/test_compass_client_real.py::test_login -v
poetry run pytest tests/test_fixtures.py -v
```

### Updating Dependencies

```bash
cd backend
poetry update
```

## Performance Notes

### Compass Client
- Authentication: ~500ms
- Event fetch: ~500ms
- Total: ~1 second
- No browser overhead
- Session cookies reused within process

### Future Optimizations
- Database session cookie persistence (optional)
- Event caching to avoid repeated API calls
- Background sync jobs
- Rate limiting to avoid overwhelming Compass

## Security Considerations

### Credentials
- Stored encrypted using Fernet
- Encryption key in environment variable
- Never committed to git
- Database file gitignored

### API Keys
- Claude API key in environment
- Never hardcoded in source
- Rotation supported via environment update

### Session Management
- Cookies handled by requests.Session()
- Auto-cleanup on process exit
- Optional database persistence for cross-session reuse

## Success Metrics

### MVP Success Criteria
- User can authenticate with Compass
- User can fetch calendar events
- User can configure filtering rules
- User can view filtered events
- Events fetched and filtered within 5 seconds
- System works reliably with real data

### Future Success Criteria
- Support for 10+ concurrent users
- 99% uptime
- Automatic sync every 6 hours
- Support for multiple schools/sources

## Resources

- [Anthropic Claude API Docs](https://docs.anthropic.com)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org)
- [Flask Documentation](https://flask.palletsprojects.com)
- [Poetry Documentation](https://python-poetry.org/docs)
- [cryptography.io](https://cryptography.io/)

## Getting Help

1. Check [Quick Start Guide](quick-start.md) for setup issues
2. Review [Architecture](architecture.md) for technical questions
3. Check existing tests for usage examples
4. Review git history for implementation context

---

**Ready to start developing?** See [quick-start.md](quick-start.md) to get set up.
