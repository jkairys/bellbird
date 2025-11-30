# Next Steps - Bellweaver Development

## Current Status

✅ **Authentication Working** - HTTP-based Compass authentication successfully implemented and tested
✅ **Mock Client Available** - Realistic test data for development without credentials
✅ **Project Structure** - Complete scaffold with Poetry, database models, and API framework
✅ **Fast Performance** - Direct HTTP client authenticates and fetches events in ~1 second

## Phase 1: MVP Development (Next 2-3 Weeks)

### Week 1: Core Infrastructure
- [ ] Database layer (`src/db/database.py`, `src/db/models.py`)
- [ ] Credential encryption (`src/db/credentials.py`)
- [ ] Session cookie persistence in database (optional - requests already handles sessions well)
- [ ] Basic unit tests for database layer

### Week 2: Filtering & API
- [ ] LLM filtering implementation (`src/filtering/llm_filter.py`)
- [ ] Flask routes (`src/api/routes.py`)
- [ ] Request/response validation (`src/api/schemas.py`)
- [ ] Integration tests for full pipeline

### Week 3: UI & Polish
- [ ] CLI interface (`src/cli.py`)
- [ ] Web frontend (HTML/CSS/JS in `frontend/`)
- [ ] End-to-end testing
- [ ] Documentation updates

## Technical Debt to Address

### High Priority
1. ✅ Remove debug files and temporary test scripts
2. ✅ Clean up browser automation code and tests
3. Update CLAUDE.md with current HTTP-based architecture

### Medium Priority
1. Add retry logic for transient Compass API failures
2. Implement rate limiting to avoid overwhelming Compass
3. Add comprehensive error messages for users
4. Handle session expiration and auto-re-authentication

### Low Priority
1. Consider switching from SQLite to PostgreSQL for production
2. Evaluate cloud deployment options (Cloud Run, etc.)

## Compass Client Optimization (Optional)

The current HTTP client is already fast (~1s total), but we could further optimize:

### Optional Session Persistence
- Store session cookies in database (encrypted)
- Check cookie validity before login
- Refresh cookies when expired

### Session Lifecycle
- Detect session expiration from API responses (401/403)
- Auto-re-authenticate when needed
- Graceful session cleanup

**Note:** The current implementation already uses `requests.Session()` which handles cookies automatically for the duration of the Python process. Database persistence is only needed if we want sessions to survive app restarts.

## Future Enhancements (Phase 2+)

### Multi-Source Support
- Class Dojo adapter
- HubHello adapter
- Xplore adapter
- Event normalization layer

### Advanced Features
- Google Calendar sync
- Email/SMS notifications
- Event tagging and categorization
- Custom filter rules per child
- Mobile app (React Native)

### Scalability
- Deploy to Google Cloud Run
- Implement job queue for event syncing
- Add caching layer (Redis)
- Database migration to Cloud SQL

## Development Workflow

### Daily Development
```bash
cd backend

# Run tests
poetry run pytest -v

# Run specific test file
poetry run pytest tests/test_compass_client_real.py -v

# Code formatting
poetry run black src tests

# Linting
poetry run flake8 src tests

# Type checking
poetry run mypy src
```

### Testing with Real Credentials
```bash
# Ensure .env is configured
cat .env

# Run integration tests
poetry run pytest tests/test_compass_client_real.py::test_login -v
poetry run pytest tests/test_compass_client_real.py::test_get_calendar_events -v
```

### Testing with Mock Data
```bash
# No credentials needed
poetry run pytest tests/test_compass_mock_client.py -v
```

## Documentation Updates Needed

1. **README.md** - Add quickstart guide
2. **CLAUDE.md** - Update with HTTP client architecture
3. **API_REFERENCE.md** - Document all API endpoints (when implemented)
4. **DEPLOYMENT.md** - Cloud deployment instructions (when ready)

## Success Metrics

### MVP (Phase 1)
- [ ] User can configure credentials via UI
- [ ] User can add child profiles with filtering rules
- [ ] User can view filtered calendar events
- [ ] Events are fetched and filtered within 5 seconds
- [ ] System works reliably for 1 week without manual intervention

### Production (Phase 2)
- [ ] Support for 10+ concurrent users
- [ ] 99% uptime
- [ ] Events sync every 6 hours automatically
- [ ] Support for multiple schools/sources
