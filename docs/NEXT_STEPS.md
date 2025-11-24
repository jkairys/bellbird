# Next Steps - Bellweaver Development

## Current Status

✅ **Authentication Working** - Puppeteer-based Compass authentication successfully implemented and tested
✅ **Mock Client Available** - Realistic test data for development without credentials
✅ **Project Structure** - Complete scaffold with Poetry, database models, and API framework

## Immediate Priority: Optimize CompassClient Session Management

The current implementation logs in on every request (~10-15s overhead). We need to implement session persistence.

### Tasks
1. **Persistent Browser Context**
   - Keep Puppeteer browser instance alive between requests
   - Reuse authenticated session instead of logging in each time
   - Implement connection pooling for concurrent requests

2. **Cookie Caching**
   - Store session cookies in database (encrypted)
   - Check cookie validity before login
   - Refresh cookies when expired

3. **Session Lifecycle Management**
   - Detect session expiration from API responses
   - Auto-re-authenticate when needed
   - Graceful browser cleanup on shutdown

### Success Criteria
- First request: ~10-15s (includes login)
- Subsequent requests: < 2s (reuses session)
- Session persists across app restarts (via cached cookies)

## Phase 1: MVP Development (Next 2-3 Weeks)

### Week 1: Core Infrastructure
- [ ] Implement optimized CompassClient with session persistence
- [ ] Database layer (`src/db/database.py`, `src/db/models.py`)
- [ ] Credential encryption (`src/db/credentials.py`)
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
1. Remove debug files in `debug_screenshots/` and logs
2. Clean up test files (remove old browser automation tests)
3. Update CLAUDE.md with current architecture

### Medium Priority
1. Add retry logic for transient Compass API failures
2. Implement rate limiting to avoid overwhelming Compass
3. Add comprehensive error messages for users

### Low Priority
1. Consider switching from SQLite to PostgreSQL for production
2. Evaluate cloud deployment options (Cloud Run, etc.)

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
- Multi-child support
- Mobile app

## Resources Needed

### Development
- Compass test credentials (already have)
- Claude API key (already have)
- Node.js runtime (already installed)

### Deployment
- TBD based on MVP completion

## Success Metrics

### MVP Launch
- [ ] Can authenticate with Compass in < 2s (after first login)
- [ ] Can fetch and filter 2 weeks of events
- [ ] Web UI functional and responsive
- [ ] All tests passing (>80% coverage)

### Production Ready
- [ ] Session management optimized
- [ ] Error handling comprehensive
- [ ] User documentation complete
- [ ] Deployed and accessible

---

**Last Updated:** November 24, 2025
**Focus:** Optimize CompassClient session management to eliminate repetitive logins
