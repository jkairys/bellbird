# Bellweaver

A unified school calendar event aggregation and filtering tool that consolidates events from multiple sources (Compass, Class Dojo, HubHello, Xplore) and intelligently filters them based on relevance to specific children.

## Documentation

- **[Full Documentation](docs/INDEX.md)** - Complete documentation index
- **[Quick Start](docs/QUICK_START.md)** - Get started in 5 minutes
- **[Next Steps](docs/NEXT_STEPS.md)** - Current development priorities
- **[Implementation Status](docs/IMPLEMENTATION_SUMMARY.md)** - What's working now

## Project Vision

Parents receive overwhelming amounts of communication from multiple school sources. Bellweaver solves this by:
- **Consolidating** events from multiple calendar systems into one place
- **Filtering** for relevant events based on child/year level/event type
- **Providing** advance notifications and a clear "next 2 weeks" view
- **Syncing** to Google Calendar for easy mobile access

## Current Status

✅ **Authentication Working** - Puppeteer-based Compass authentication functional
✅ **Tests Passing** - Integration tests with real credentials working
⚠️ **Performance Issue** - Currently logs in on every request (~10-15s)
🎯 **Next Priority** - Optimize session management (see [docs/NEXT_STEPS.md](docs/NEXT_STEPS.md))

## MVP Scope (Phase 1)

The MVP focuses on **Compass only** for local development:
- Fetch calendar events from Compass
- Filter events intelligently using Claude API
- Provide both CLI and Web UI interfaces
- Store data locally in SQLite with encrypted credentials

## Project Structure

```
bellweaver/
├── backend/                      # Backend Python application
│   ├── src/                      # Main Python package
│   │   ├── __init__.py
│   │   ├── cli.py               # CLI entry point
│   │   ├── app.py               # Flask app entry point
│   │   │
│   │   ├── adapters/            # Calendar source adapters
│   │   │   ├── __init__.py
│   │   │   ├── compass.py       # Real Compass API client
│   │   │   └── compass_mock.py  # Mock Compass for testing
│   │   │
│   │   ├── models/              # Data models
│   │   │   └── config.py        # Configuration models
│   │   │
│   │   ├── db/                  # Database layer
│   │   │   ├── __init__.py
│   │   │   ├── database.py      # SQLite connection & schema
│   │   │   ├── credentials.py   # Encrypted credential storage
│   │   │   └── models.py        # SQLAlchemy ORM models
│   │   │
│   │   ├── filtering/           # Event filtering & enrichment
│   │   │   ├── __init__.py
│   │   │   └── llm_filter.py    # Claude API filtering logic
│   │   │
│   │   └── api/                 # REST API endpoints
│   │       ├── __init__.py
│   │       ├── routes.py        # Flask routes
│   │       └── schemas.py       # Request/response schemas
│   │
│   ├── tests/                    # Unit tests
│   │   ├── __init__.py
│   │   ├── test_compass_adapter.py
│   │   ├── test_compass_mock.py
│   │   └── test_filtering.py
│   │
│   ├── data/                     # Data directory (gitignored)
│   │   └── .gitkeep
│   │
│   ├── pyproject.toml           # Poetry configuration
│   ├── .env.example             # Environment variables template
│   └── README.md                # Backend setup instructions
│
├── frontend/                     # Frontend application (TBD)
│   ├── src/                     # Source files
│   ├── public/                  # Static assets
│   └── README.md                # Frontend setup instructions
│
├── docs/                         # Project documentation
│   ├── INDEX.md                 # Documentation index
│   ├── QUICK_START.md           # Quick start guide
│   └── ...                      # Other docs
│
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## Setup Instructions

### Prerequisites
- Python 3.9+
- Poetry (for dependency management)
- Compass account credentials (for real API testing)
- Claude API key (from Anthropic)

### Installation

1. **Clone the repository**:
```bash
git clone <repo-url>
cd bellweaver
```

2. **Set up the backend**:
```bash
cd backend
poetry install --with dev
```

3. **Set up environment variables**:
```bash
cp .env.example .env
```

Then edit `.env` with your actual values:
```bash
CLAUDE_API_KEY=your-anthropic-api-key-here
BELLWEAVER_ENCRYPTION_KEY=  # Will be auto-generated on first run
```

4. **Verify installation**:
```bash
poetry run pytest
```

## Usage

### CLI Mode

**Full end-to-end sync** (fetch + filter):
```bash
poetry run bellbird --full
```

**Individual steps**:
```bash
# Just fetch from Compass (or mock)
poetry run bellbird --fetch

# Filter cached events
poetry run bellbird --filter

# Show filtered results
poetry run bellbird --show-filtered
```

**Configuration**:
```bash
# Set Compass credentials (encrypted in SQLite)
poetry run bellbird --set-credentials compass --username your@email.com --password yourpassword

# Configure child profile
poetry run bellbird --set-config \
  --child-name "Sophia" \
  --school "St Mary's Primary" \
  --year-level "Year 3" \
  --class "3A" \
  --interests "athletics,music" \
  --filter-rules "Include excursions and sports. Exclude assemblies."
```

### Web UI

**Start the Flask server**:
```bash
poetry run flask run
```

Then open http://localhost:5000 in your browser.

Features:
- Onboarding form for credentials and child profile
- Dashboard showing next 2 weeks of relevant events
- Sync button to fetch & filter new events
- Simple, clean interface

## Development

All development commands should be run from the `backend/` directory:

### Running Tests
```bash
cd backend
poetry run pytest
```

### Code Quality
```bash
cd backend
poetry run black src tests
poetry run flake8 src tests
poetry run mypy src
```

### Development Mode
```bash
cd backend
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

### Phase 1 (MVP - Days 1-10)
- [x] Project scaffold with Poetry
- [ ] Database layer with encryption
- [ ] Mock Compass adapter
- [ ] Real Compass adapter
- [ ] CLI interface
- [ ] Flask backend
- [ ] Web UI
- [ ] Unit tests
- [ ] Documentation

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
rm data/bellweaver.db
```

## Contributing

This is a personal project, but feel free to fork and adapt!

## License

TBD
