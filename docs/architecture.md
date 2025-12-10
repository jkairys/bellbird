# Bellweaver Architecture

## Overview

Bellweaver is a school calendar event aggregation and filtering tool. The MVP focuses on Compass calendar integration with intelligent filtering using Claude API.

## Current Architecture

### Multi-Package Monorepo Structure

The system is now organized as a **monorepo with two independent Python packages**:

```
┌────────────────────────────────────────────────────────────┐
│  compass-client Package (Independent Library)              │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Factory (factory.py)                                 │  │
│  │  create_client(mode="real"|"mock") → Client         │  │
│  └──────────────────────────────────────────────────────┘  │
│         ↓                              ↓                    │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │ CompassClient    │         │ CompassMockClient│         │
│  │ (client.py)      │         │ (mock_client.py) │         │
│  │                  │         │                  │         │
│  │ • HTTP auth      │         │ • JSON files     │         │
│  │ • Session mgmt   │         │ • No network     │         │
│  │ • API calls      │         │ • Same interface │         │
│  │ • Returns dicts  │         │ • Returns dicts  │         │
│  └──────────────────┘         └──────────────────┘         │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ CompassParser (parser.py)                           │  │
│  │  • Generic parse() method                           │  │
│  │  • parse_safe() with error collection               │  │
│  │  • Dict → Pydantic validation                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Pydantic Models (models.py)                         │  │
│  │  • CompassEvent (37 fields)                         │  │
│  │  • CompassUser (40 fields)                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Mock Data (data/mock/)                              │  │
│  │  • compass_events.json                              │  │
│  │  • compass_user.json                                │  │
│  │  • schema_version.json                              │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
                          ↓ (dependency)
┌────────────────────────────────────────────────────────────┐
│  bellweaver Package (Main Application)                     │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ CLI Commands (cli/commands/)                        │  │
│  │  • compass.py - uses create_client()                │  │
│  │  • api.py                                           │  │
│  │  • mock.py                                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Flask API (api/)                                    │  │
│  │  • Routes use create_client()                       │  │
│  │  • Returns filtered events                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Domain Mappers (mappers/compass.py)                │  │
│  │  • CompassEvent → BellweaverEvent                   │  │
│  │  • Transforms compass_client models to app models   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ LLM Filter (filtering/llm_filter.py)                │  │
│  │  • Claude API integration                           │  │
│  │  • Event relevance filtering                        │  │
│  │  • Event summarization                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Database Layer (db/)                                │  │
│  │  • SQLAlchemy ORM                                   │  │
│  │  • Credential encryption                            │  │
│  │  • Event storage                                    │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

### Key Architectural Benefits

1. **Decoupled Packages**: compass-client can be developed, tested, and versioned independently
2. **Mock Mode**: Full development without Compass credentials via `COMPASS_MODE=mock`
3. **CI-Friendly**: Tests run in mock mode, avoiding geo-blocking issues
4. **Clear Boundaries**: API client logic completely separated from application logic
5. **Reusability**: compass-client can be used by other projects

## Implemented Components

### 1. compass-client Package (Independent Library)

**Location:** `packages/compass-client/`

The compass-client package is a **standalone, independently testable library** that provides Compass Education API integration.

#### CompassClient (Real API)

**File:** `packages/compass-client/compass_client/client.py`

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

#### CompassMockClient (Mock Data)

**File:** `packages/compass-client/compass_client/mock_client.py`

**Features:**

- Realistic synthetic calendar events from JSON files
- No authentication required
- Identical interface to real Compass client
- Supports development without credentials
- Committed mock data for reproducible testing

**Mock Data Location:** `packages/compass-client/data/mock/`
- `compass_events.json` - Sample calendar events
- `compass_user.json` - Sample user profile
- `schema_version.json` - Schema metadata

**Use Cases:**

- Local development without Compass credentials
- CI/CD testing in geo-blocked environments
- Frontend development
- Demonstrating functionality
- Regression testing

#### Factory Pattern

**File:** `packages/compass-client/compass_client/factory.py`

**Function:** `create_client(base_url, username, password, mode=None)`

**Mode Selection:**
1. Explicit `mode` parameter (highest priority)
2. `COMPASS_MODE` environment variable
3. Default: `"real"`

**Example:**

```python
from compass_client import create_client

# Auto-select based on COMPASS_MODE env var
client = create_client(base_url, username, password)

# Explicit override
client = create_client(..., mode="mock")  # Force mock
client = create_client(..., mode="real")  # Force real
```

#### CompassParser (Generic Validation)

**File:** `packages/compass-client/compass_client/parser.py`

**Features:**

- Transforms raw API responses (dicts) into validated Pydantic models
- Separates HTTP communication concerns from data validation
- Provides type safety and IDE autocomplete
- Comprehensive error handling with detailed validation errors

**Architecture Pattern:**

```
Raw API → Client (dicts) → Parser (Pydantic) → Application
```

**Key Methods:**

- `parse(model, raw)` - Generic static method that parses any Pydantic model (single or list)
- `parse_safe(model, raw_list, skip_invalid)` - Parse list with error collection

**Generic Design:**

Uses Python `TypeVar` to provide a single, scalable interface:

```python
from compass_client import CompassParser, CompassEvent, CompassUser

# Parse events
events = CompassParser.parse(CompassEvent, raw_events_list)

# Parse user
user = CompassParser.parse(CompassUser, raw_user_dict)

# Safe parsing with error collection
valid_events, errors = CompassParser.parse_safe(
    CompassEvent,
    raw_events_list,
    skip_invalid=True
)
```

**Benefits:**

1. **Separation of Concerns** - Client handles HTTP, parser handles validation
2. **Scalability** - Single generic interface works with any Pydantic model
3. **Flexibility** - Can work with raw dicts or validated models
4. **Error Handling** - Clear distinction between network and validation errors
5. **Testing** - Independent testing of HTTP layer and validation layer
6. **Type Safety** - Full IDE autocomplete with Python generics

#### Pydantic Models

**File:** `packages/compass-client/compass_client/models.py`

- `CompassEvent` - Calendar event model (37 fields)
- `CompassUser` - User profile model (40 fields)

All models are validated using Pydantic for type safety and runtime validation.

### 2. bellweaver Package (Main Application)

**Location:** `packages/bellweaver/`

The bellweaver package is the main application that **consumes** compass-client as a dependency.

#### Domain Mappers

**File:** `packages/bellweaver/bellweaver/mappers/compass.py`

- Transforms `CompassEvent` → Bellweaver domain models
- Handles field mapping and data normalization
- Keeps application logic decoupled from Compass API structure

### 4. LLM Filter

**File:** `packages/bellweaver/bellweaver/filtering/llm_filter.py`

**Features:**

- Claude API integration
- Event relevance determination
- Event summarization
- Structured JSON output

**Status:** Implemented but not yet integrated into pipeline

### 5. Credential Manager

**File:** `packages/bellweaver/bellweaver/db/credentials.py`

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

### Why Three-Layer Architecture (Adapter → Parser → Application)?

We chose to separate the adapter layer (HTTP communication) from the parser layer (validation) for several key reasons:

**Separation of Concerns:**
- Adapters focus solely on HTTP communication, authentication, and API quirks
- Parsers handle validation, transformation, and type safety
- Application code works with clean, validated domain models

**Flexibility:**
- Easy to swap between real and mock adapters (both return simple dicts)
- Can handle API changes without touching business logic
- Allows partial parsing (extract just what you need)
- Can store raw JSON for audit trail and re-parse with updated models

**Error Handling:**
- Network errors vs validation errors are clearly separated
- Can gracefully handle malformed API responses
- Better debugging: know immediately if the issue is connectivity or data quality

**Testing:**
- Adapter tests use simple dict fixtures
- Parser tests validate Pydantic models independently
- Integration tests verify end-to-end flow
- Each layer can be tested in isolation

**Alternatives Considered:**

1. **Adapter returns Pydantic models** - Rejected due to tight coupling and harder testing
2. **Everything returns dicts** - Rejected due to no type safety and runtime errors

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
