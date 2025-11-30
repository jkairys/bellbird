# Bellweaver Architecture

## Overview

Bellweaver is a school calendar event aggregation and filtering tool. The MVP focuses on Compass calendar integration with intelligent filtering using Claude API.

## Current Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Local Development Environment                               │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Compass Client (adapters/compass.py)                │   │
│  │                                                      │   │
│  │  ├─ HTTP-based authentication                       │   │
│  │  ├─ Session management with cookies                │   │
│  │  ├─ Calendar event fetching                        │   │
│  │  └─ Returns raw event data                         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Mock Client (adapters/compass_mock.py)              │   │
│  │                                                      │   │
│  │  ├─ Realistic test data                            │   │
│  │  ├─ No authentication required                     │   │
│  │  └─ Same interface as real client                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ LLM Filter (filtering/llm_filter.py)                │   │
│  │                                                      │   │
│  │  ├─ Claude API integration                         │   │
│  │  ├─ Event relevance filtering                      │   │
│  │  └─ Event summarization                            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Credential Manager (db/credentials.py)              │   │
│  │                                                      │   │
│  │  ├─ Fernet encryption                              │   │
│  │  └─ Secure credential storage                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Implemented Components

### 1. Compass Client (HTTP-based)

**File:** `backend/src/adapters/compass.py`

**Features:**
- Direct HTTP requests using Python `requests` library
- Form-based authentication with ASP.NET ViewState handling
- Session management with cookie persistence
- Calendar event retrieval via Compass API
- Automatic userId and schoolConfigKey extraction

**Authentication Flow:**
1. GET login page to extract ViewState and form parameters
2. POST credentials with form data
3. Capture session cookies
4. Extract user metadata from response
5. Use session for subsequent API calls

**Performance:** ~1 second total (authentication + event fetch)

**Advantages:**
- No browser dependencies
- Fast authentication
- Lower resource usage
- Better Cloudflare bypass than browser automation

### 2. Mock Client

**File:** `backend/src/adapters/compass_mock.py`

**Features:**
- Realistic synthetic calendar events
- No authentication required
- Identical interface to real Compass client
- Supports development without credentials

**Use Cases:**
- Testing filtering logic
- Frontend development
- CI/CD pipelines
- Demonstrating functionality

### 3. LLM Filter

**File:** `backend/src/filtering/llm_filter.py`

**Features:**
- Claude API integration
- Event relevance determination
- Event summarization
- Structured JSON output

**Status:** Implemented but not yet integrated into pipeline

### 4. Credential Manager

**File:** `backend/src/db/credentials.py`

**Features:**
- Fernet symmetric encryption
- Secure credential storage
- Environment-based encryption keys

**Status:** Implemented but not yet integrated with database

## Planned Components

### Database Layer
- SQLite for local development
- SQLAlchemy ORM models
- Tables: credentials, user_config, raw_events, filtered_events, sync_metadata

### Flask API
- REST endpoints for configuration and event retrieval
- Request/response validation
- Authentication middleware

### Web UI
- Configuration interface
- Event dashboard
- Sync triggers

### CLI
- Command-line interface for batch operations
- Development and debugging tool

## Data Flow (Planned)

```
User Input (Credentials + Config)
    ↓
Compass Client → Fetch Events
    ↓
Store Raw Events (SQLite)
    ↓
LLM Filter → Analyze Relevance
    ↓
Store Filtered Events (SQLite)
    ↓
Display (Web UI / CLI)
```

## Technical Decisions

### Why HTTP Client Instead of Browser Automation?

We initially explored browser automation (Playwright) but discovered:
- Cloudflare detects browser automation even with stealth plugins
- HTTP client is simpler with no browser dependencies
- Better Cloudflare bypass (simple requests look like mobile apps)
- Faster with no browser startup time
- More reliable with fewer moving parts

The HTTP client successfully authenticates without any prior browser sessions.

### Why SQLite?

For the MVP:
- No server setup required
- Simple file-based storage
- Good enough for single-user local development
- Easy to migrate to PostgreSQL/Cloud SQL later

### Why Fernet Encryption?

- Simple symmetric encryption
- Built into Python cryptography library
- Suitable for local credential storage
- Key stored in environment variable (not in code)

## Future Enhancements

### Multi-Source Support (Phase 2)
- Class Dojo adapter
- HubHello adapter
- Xplore adapter
- Event normalization layer

### Advanced Features
- Google Calendar sync
- Email/SMS notifications
- Event tagging and categorization
- Custom filter rules per child
- Mobile app

### Scalability
- Deploy to Google Cloud Run
- Job queue for event syncing
- Caching layer (Redis)
- Database migration to Cloud SQL
- Multi-user support

## Key Design Principles

1. **Start Simple** - Local SQLite before cloud databases
2. **Test Early** - Mock data allows parallel development
3. **Single Source First** - Compass only before multi-source
4. **Fast Iteration** - HTTP client over browser automation
5. **Secure by Default** - Encrypted credentials from day one
