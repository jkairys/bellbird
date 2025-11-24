# Bellweaver Documentation Index

**Last Updated**: November 24, 2025
**Current Focus**: Optimize session management in CompassClient

## Quick Start (5 Minutes)

New to the project? Start here:

1. **README.md** (5 min) - Project overview and setup
2. **NEXT_STEPS.md** (3 min) - Current priorities and roadmap
3. **IMPLEMENTATION_SUMMARY.md** (3 min) - What's working now

## Core Documentation

| File | Purpose | When to Read |
|------|---------|-------------|
| **README.md** | Project overview & structure | First time |
| **NEXT_STEPS.md** | Current priorities & roadmap | Planning work |
| **IMPLEMENTATION_SUMMARY.md** | What's built & working | Understanding status |
| **MVP_ARCHITECTURE.md** | System design & data flow | Before coding |
| **PLAN.md** | Original vision & requirements | Understanding goals |

## Compass Integration

| File | Purpose |
|------|---------|
| **COMPASS_AUTHENTICATION_STRATEGIES.md** | Current auth approach + usage examples |
| **INTEGRATION_TEST_GUIDE.md** | Running integration tests |
| **COMPASS_PYTHON_CLIENT_PLAN.md** | Original design doc (historical reference) |

## Current Priority

**Optimize CompassClient Session Management**

The Compass client works but logs in on every request (~10-15s). See:
- **NEXT_STEPS.md** - Detailed optimization tasks
- **IMPLEMENTATION_SUMMARY.md** - Current implementation status
- **COMPASS_AUTHENTICATION_STRATEGIES.md** - How auth works now

## Development Roadmap

### Week 1: Session Optimization
- Persistent browser context
- Cookie caching in database
- Session lifecycle management
- **Goal:** < 2s request time (after first login)

### Weeks 2-3: MVP Features
- Database layer with encryption
- LLM filtering (Claude API)
- Flask API routes
- Basic web frontend

See **NEXT_STEPS.md** for complete roadmap.

## Common Tasks

| Task | Documentation |
|------|--------------|
| Understanding current status | IMPLEMENTATION_SUMMARY.md |
| Setting up environment | README.md, QUICK_START.md |
| Using Compass client | COMPASS_AUTHENTICATION_STRATEGIES.md |
| Running tests | INTEGRATION_TEST_GUIDE.md |
| Understanding architecture | MVP_ARCHITECTURE.md |
| Planning next work | NEXT_STEPS.md |

## Project Structure

```
bellweaver/
├── src/adapters/
│   ├── compass.py           # ✅ Puppeteer-based client (working, needs optimization)
│   └── compass_mock.py      # ✅ Mock data for testing
├── src/db/                  # ⏳ TODO - Database layer
├── src/filtering/           # ⏳ TODO - LLM filtering
├── src/api/                 # ⏳ TODO - Flask API
├── frontend/                # ⏳ TODO - Web UI
└── tests/
    ├── test_compass_client_real.py  # ✅ Integration tests
    └── test_compass_client_mock.py  # ✅ Mock tests
```

## Document Status

✅ **Current & Active**: NEXT_STEPS, IMPLEMENTATION_SUMMARY, COMPASS_AUTHENTICATION_STRATEGIES, QUICK_START
✅ **Reference**: MVP_ARCHITECTURE, PLAN, INTEGRATION_TEST_GUIDE
📚 **Historical**: COMPASS_PYTHON_CLIENT_PLAN (original design, not implemented)

## For New Developers

1. **QUICK_START.md** - Get set up quickly
2. **IMPLEMENTATION_SUMMARY.md** - See what's working
3. **NEXT_STEPS.md** - Know what to build next

## For Compass Integration

1. **COMPASS_AUTHENTICATION_STRATEGIES.md** - How it works + usage examples
2. **INTEGRATION_TEST_GUIDE.md** - Running tests

---

**Ready to start?** → See NEXT_STEPS.md for immediate priorities
