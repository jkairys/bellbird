# Bellbird MVP Architecture

## Focus

**One problem**: Fetch Compass calendar events and intelligently filter/summarize them based on relevance to a specific child.

**Key principle**: Build a working, usable tool in Phase 1 that you can actually use immediately. Ship fast, learn domain, iterate.

**Out of scope for MVP**: Scheduling, automation, email digests, multi-source aggregation, reminders, data normalization (defer until Phase 2 multi-source).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Local Development Environment (Single Machine)              │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Python CLI / Flask Backend: main.py                 │   │
│  │                                                      │   │
│  │  ├─ Load credentials from SQLite (encrypted)        │   │
│  │  └─ Call API Layer                                  │   │
│  └──────────┬───────────────────────────────────────────┘   │
│             │                                                 │
│  ┌──────────▼──────────────────────────────────────────┐   │
│  │ API Layer (adapters/compass.py)                     │   │
│  │                                                      │   │
│  │  ├─ Authenticate with Compass                       │   │
│  │  ├─ Fetch calendar events                           │   │
│  │  └─ Return raw event list                           │   │
│  └──────────┬───────────────────────────────────────────┘   │
│             │                                                 │
│  ┌──────────▼──────────────────────────────────────────┐   │
│  │ SQLite Database                                     │   │
│  │                                                      │   │
│  │  ├─ credentials (encrypted: compass_user, password) │   │
│  │  ├─ raw_events_cache                                │   │
│  │  ├─ normalized_events                               │   │
│  │  ├─ filtered_events                                 │   │
│  │  ├─ user_config (child profile, rules)             │   │
│  │  └─ sync_metadata (timestamps, state)               │   │
│  └──────────┬───────────────────────────────────────────┘   │
│             │                                                 │
│  ┌──────────▼──────────────────────────────────────────┐   │
│  │ Normalization Layer (models/event.py)               │   │
│  │                                                      │   │
│  │  ├─ Parse raw Compass events                        │   │
│  │  ├─ Extract title, date, description, etc.         │   │
│  │  └─ Create normalized Event objects                │   │
│  └──────────┬───────────────────────────────────────────┘   │
│             │                                                 │
│  ┌──────────▼──────────────────────────────────────────┐   │
│  │ Filtering & Enrichment Layer (filters/relevance.py) │   │
│  │                                                      │   │
│  │  ├─ Load user config from SQLite                   │   │
│  │  ├─ Call Claude API with:                          │   │
│  │  │   - All normalized events                        │   │
│  │  │   - Child profile & preferences                 │   │
│  │  │   - Filtering rules (free text)                │   │
│  │  └─ Get filtered + summarized events               │   │
│  └──────────┬───────────────────────────────────────────┘   │
│             │                                                 │
│             └─→ Store in SQLite filtered_events table       │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Simple Flask Backend (Phase 2)                      │   │
│  │                                                      │   │
│  │  ├─ GET /api/config → User setup form              │   │
│  │  ├─ POST /api/config → Save credentials/profile    │   │
│  │  ├─ POST /api/sync → Trigger fetch+filter          │   │
│  │  ├─ GET /api/events → Return filtered events       │   │
│  │  └─ GET /api/sync-status → Show last sync time     │   │
│  └──────────┬───────────────────────────────────────────┘   │
│             │                                                 │
│  ┌──────────▼──────────────────────────────────────────┐   │
│  │ Web UI (Phase 2)                                    │   │
│  │                                                      │   │
│  │  ├─ Setup/Onboarding Form                          │   │
│  │  ├─ Credentials input                              │   │
│  │  ├─ Child profile config                           │   │
│  │  ├─ Filter rules editor                            │   │
│  │  └─ Event dashboard (next 2 weeks)                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Data Directory: ./data/                                    │
│  ├─ bellbird.db (SQLite database)                           │
│  └─ .env (environment variables, gitignored)               │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow Example

### Step 1: Fetch & Cache Raw Events
```
CLI Command: python fetch_and_filter.py --fetch-only

├─ Load credentials from GCP Secret Manager
│  (requires local GOOGLE_APPLICATION_CREDENTIALS)
│
├─ Authenticate with Compass API
│
├─ Query Compass calendar endpoint
│  → Returns 15 events (mixed year levels, multiple children)
│
└─ Save to: data/cache/raw_events_cache.json
   (raw Compass response, timestamped)
```

### Step 2: Normalize Events
```
CLI Command: python fetch_and_filter.py --normalize

├─ Load raw_events_cache.json
│
├─ For each event, extract:
│   {
│     "id": "compass_event_123",
│     "source": "compass",
│     "title": "Year 3 Excursion to Zoo",
│     "description": "...",
│     "date": "2024-12-15T09:00:00Z",
│     "year_levels": ["Year 3"],
│     "classes": ["3A"],
│     "location": "Taronga Zoo",
│     "event_type": "excursion",  # auto-detected from title/description
│     "raw_data": {...}  # preserve full original data
│   }
│
└─ Save to: data/cache/normalized_events.json
   (canonical event format, timestamped)
```

### Step 3: Filter & Summarize
```
CLI Command: python fetch_and_filter.py --filter

├─ Load configuration:
│   {
│     "child": {
│       "name": "Sophia",
│       "school": "Primary School",
│       "year_level": "Year 3",
│       "class": "3A",
│       "interests": ["athletics", "music"]
│     },
│     "filter_rules": "Include excursions, sports events, and performances. Exclude general assemblies and events for other year levels.",
│     "date_range": "2024-11-22 to 2024-12-06"
│   }
│
├─ Call Claude API with:
│   Prompt:
│     "Given Sophia's profile (Year 3, 3A, interested in athletics/music),
│      filter these 15 school events and return only relevant ones.
│      Filter rule: [user's free text rule].
│      For each relevant event, provide: title, date, why it's relevant, and any action needed."
│
│   Events: [normalized_events JSON]
│
├─ Receive response:
│   [
│     {
│       "event_id": "compass_event_123",
│       "title": "Year 3 Excursion to Zoo",
│       "date": "2024-12-15",
│       "relevance": "RELEVANT",
│       "reason": "Excursion for Year 3 class, matches user filter",
│       "action": "Permission slip may be required - check description"
│     },
│     ...
│   ]
│
└─ Output to stdout or data/output/filtered_events.json
```

---

## Project Structure

```
bellbird/
├── README.md
├── PLAN.md
├── MVP_ARCHITECTURE.md
│
├── src/
│   ├── __init__.py
│   │
│   ├── app.py                          # Flask backend entry point
│   ├── cli.py                          # CLI entry point for batch operations
│   │
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── compass.py                  # Real Compass API client
│   │   └── compass_mock.py             # Mock Compass (for early testing)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── config.py                   # User config models
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py                 # SQLite connection & schema
│   │   ├── credentials.py              # Encrypted credential storage
│   │   └── models.py                   # SQLAlchemy ORM models
│   │
│   ├── filtering/
│   │   ├── __init__.py
│   │   └── llm_filter.py               # Claude API filtering logic
│   │
│   └── api/
│       ├── __init__.py
│       ├── routes.py                   # Flask routes (config, sync, events)
│       └── schemas.py                  # Request/response schemas
│
├── frontend/                            # Phase 1: Minimal web UI
│   ├── index.html                       # Onboarding form
│   ├── dashboard.html                   # Event dashboard
│   ├── css/
│   │   └── style.css                   # Basic styling
│   └── js/
│       └── app.js                      # Form submission, sync trigger
│
├── data/
│   └── .gitkeep                        # SQLite DB created here at runtime
│
├── tests/
│   ├── __init__.py
│   ├── test_compass_adapter.py
│   ├── test_compass_mock.py
│   └── test_filtering.py
│
├── requirements.txt
├── .env.example
├── .gitignore
└── run.sh                              # Simple startup script
```

---

## Key Design Decisions

### 1. **Credential Storage**
- Credentials encrypted in SQLite using `cryptography` library (Fernet symmetric encryption)
- Encryption key stored in environment variable `.env` (never committed)
- Database file `data/bellbird.db` is gitignored
- Allows local development without external services
- Can be migrated to GCP Secret Manager later if needed

### 2. **Database Schema (SQLite) - Minimal**
```sql
-- Credentials (encrypted)
credentials(id, source, username, password_encrypted, created_at)

-- User Configuration
user_config(id, child_name, school, year_level, class, interests_json, filter_rules, date_range_start, date_range_end)

-- Raw Events Cache (JSON blob - unmodified Compass response)
raw_events_cache(id, source, raw_data_json, fetched_at)

-- Filtered Events (from LLM, with full original event data)
filtered_events(id, source_event_id, is_relevant, reason, action_needed, llm_summary, original_event_json, created_at)

-- Sync Metadata
sync_metadata(id, source, last_sync_time, sync_status, error_message)
```

**Note**: No normalization table. Raw Compass events go directly to LLM filtering. Normalization schema added in Phase 2 when integrating Class Dojo/HubHello/Xplore.

### 3. **Caching & Filtering Strategy**
- **Raw cache**: Compass API responses stored as unmodified JSON blobs
  - Avoids re-fetching on rate limits
  - Preserves original structure for later analysis
  - Timestamp tracks freshness

- **Direct to LLM**: Raw Compass events sent directly to Claude for filtering
  - No intermediate transformation
  - LLM sees the data as-is, can handle quirks
  - Faster iteration on filter logic

- **Filtered results**: LLM outputs stored with reasoning + original event
  - Can re-filter or analyze results without recalling LLM
  - Full event data preserved for UI display
  - Timestamps allow tracking changes

### 4. **Filtering via LLM**
- Claude API handles fuzzy matching and natural language interpretation
- Single API call with all events (volume is small)
- User provides rules in free text (e.g., "Include events for Year 3, exclude assemblies")
- Output is structured but generated by LLM (trade-off: cost vs. flexibility)
- Results cached to avoid repeated LLM calls for same data

### 5. **Dual Interface (Both in Phase 1)**
- **CLI Mode**: For testing and batch operations
  - Commands: `python cli.py --fetch`, `--filter`, `--full`
  - Easy for development and quick testing
  - Debug mode for understanding data flow

- **Web Mode**: Usable UI for actual use
  - Flask backend provides REST API
  - Simple HTML/JS frontend for onboarding + dashboard
  - Both interface the same database and filtering logic
  - Built in parallel with CLI, both ship on Day 10

### 6. **Mock Data (Parallel Work, Days 1-3)**
- `adapters/compass_mock.py` returns synthetic but realistic Compass events
- Used for initial pipeline development while researching real Compass integration
- Same interface as real adapter (swap one import line)
- Allows testing filtering rules immediately without real credentials
- Discovered data quality issues early
- Discarded after real adapter is working

---

## MVP Scope

### Phase 1: Complete (Days 1-10)
- [x] SQLite database with encrypted credential storage
- [x] Mock Compass adapter (for parallel development)
- [x] Real Compass API adapter (using existing JS library or direct auth)
- [x] Raw event caching (SQLite JSON blob)
- [x] Claude API filtering + summarization (raw Compass events → filtered results)
- [x] CLI interface (`--fetch`, `--filter`, `--full`, `--show-filtered`)
- [x] Flask backend with REST API
- [x] Simple HTML/JS onboarding form (config + credentials)
- [x] Dashboard showing next 2 weeks
- [x] Sync trigger button (web and CLI)
- [x] Configuration management (user config in SQLite)
- [x] Unit tests for each layer
- [x] **Deliverable**: Working web + CLI tool you can actually use

### Phase 2: Polish & Multi-Source (Fast Follower)
- [ ] Add normalization layer for multi-source compatibility
- [ ] Integrate Class Dojo
- [ ] Integrate HubHello
- [ ] Integrate Xplore
- [ ] Improved styling ("make it sexy")
- [ ] Advanced filtering UI (tag-based, date range filtering)

### Will NOT Build (Yet)
- [ ] Scheduling / automation (cron/Cloud Scheduler)
- [ ] Email digests / reminders / notifications
- [ ] Google Calendar sync
- [ ] Multi-user support
- [ ] GCP deployment

---

## Development Timeline (10 Days to Working Tool)

### Day 1: Foundation & Mock Data
- [ ] Project scaffold: Python structure, requirements.txt, .env setup
- [ ] Database: Create SQLite schema (credentials, user_config, raw_events_cache, filtered_events, sync_metadata)
- [ ] Encryption: Implement encrypted credential storage (cryptography.fernet)
- [ ] CLI skeleton: Basic argument parser for `--fetch`, `--filter`, `--full`, `--show-filtered`
- [ ] Mock Compass adapter: Create `compass_mock.py` with 15-20 synthetic events (various types, year levels, dates)

### Days 2-3: CLI Pipeline with Mock Data (Parallel: Research Real Compass Integration)
- [ ] Implement filtering layer: Take raw Compass events, send to Claude API
- [ ] Claude integration: Build prompts that take user config + events → filtered results
- [ ] Store filtered results in SQLite (with reasoning + original event)
- [ ] Test CLI pipeline end-to-end: `python cli.py --full` with mock data
- [ ] Iterate on filter rules and prompts based on mock results
- **Parallel**: Research real Compass API (JS library, direct HTTP, reverse-engineer, etc.)

### Days 4-5: Real Compass Integration & Flask Setup
- [ ] Implement real Compass adapter (swap `compass_mock.py` for `compass.py`)
- [ ] Test with real Compass credentials (fetch real calendar)
- [ ] Debug data quirks (missing fields, date formats, etc.)
- [ ] Update filter prompts based on real data characteristics
- [ ] Start Flask app: Basic structure, route skeleton (`/api/config`, `/api/sync`, `/api/events`)

### Days 6-7: Web UI & API Integration
- [ ] Flask routes: `POST /api/config` (save credentials + profile), `POST /api/sync` (trigger fetch+filter), `GET /api/events` (return filtered)
- [ ] Frontend: `index.html` (onboarding form for credentials, child profile, filter rules)
- [ ] Frontend: `dashboard.html` (display filtered events, next 2 weeks, sync button)
- [ ] JavaScript: Form submission, API calls, event display
- [ ] Test web UI with mock data, iterate on UX

### Days 8-9: Integration, Testing & Polish
- [ ] End-to-end testing: Web → Flask → Database → Claude → Results
- [ ] Error handling: Missing credentials, API failures, malformed data
- [ ] CLI testing: All command combinations work
- [ ] Unit tests: For filtering, database operations, credential handling
- [ ] Documentation: README with setup + usage + troubleshooting

### Day 10: Final Testing & Deploy Locally
- [ ] Full workflow test: Fresh database → onboard via web → sync → see filtered events
- [ ] Performance: How fast does sync + filtering take?
- [ ] Edge cases: Empty calendar, all events filtered, invalid credentials
- [ ] Polish: Basic styling, error messages, loading states
- [ ] **Deliverable**: Running locally, ready to use with real data

---

## Configuration & Usage Examples

### Initial Setup (CLI)

**Set Compass credentials** (encrypted in SQLite):
```bash
python src/cli.py --set-credentials compass --username your_email@example.com --password your_compass_password
```

**Configure child profile**:
```bash
python src/cli.py --set-config \
  --child-name "Sophia" \
  --school "St Mary's Primary" \
  --year-level "Year 3" \
  --class "3A" \
  --interests "athletics,music,art" \
  --filter-rules "Include excursions, sports events, music performances. Exclude assemblies and other year levels."
```

### Running the Pipeline

**Full end-to-end sync**:
```bash
python src/cli.py --full
```

**Individual steps**:
```bash
# Just fetch from Compass
python src/cli.py --fetch

# Normalize raw data (without fetching)
python src/cli.py --normalize

# Filter events (without fetching/normalizing)
python src/cli.py --filter

# Show results
python src/cli.py --show-filtered
```

### Output Example

```json
{
  "events": [
    {
      "event_id": "compass_event_123",
      "title": "Year 3 Excursion to Zoo",
      "date": "2024-12-15",
      "relevance": "RELEVANT",
      "reason": "Excursion for Year 3 class, matches user filter",
      "action": "Permission slip may be required - check school portal"
    },
    {
      "event_id": "compass_event_456",
      "title": "Year 3 Music Performance",
      "date": "2024-12-10",
      "relevance": "RELEVANT",
      "reason": "Sophia is in Year 3 and interested in music",
      "action": "Check if tickets needed or permission required"
    }
  ],
  "summary": "2 relevant events in next 2 weeks"
}
```

### Environment Variables

**.env** (never committed):
```bash
CLAUDE_API_KEY=sk-ant-...
BELLBIRD_ENCRYPTION_KEY=base64-encoded-key-here  # Generated on first run
```

**.env.example** (tracked in git):
```bash
CLAUDE_API_KEY=your-anthropic-api-key-here
BELLBIRD_ENCRYPTION_KEY=will-be-auto-generated-on-first-run
```

---

## Technical Decisions

1. **Compass Integration Method**:
   - Use existing `heheleo/compass-education` JS library via Node.js subprocess?
   - Or implement direct HTTP authentication in Python (reverse-engineer if needed)?
   - → **Decision needed before Day 4**

2. **Encryption Library**:
   - Using `cryptography.fernet` (simple, symmetric encryption)
   - Key generated on first run, stored in `.env` (never committed)
   - Good enough for local development

3. **Database Library**:
   - Using SQLAlchemy ORM (type safety, easier testing, better IDE support)
   - SQLite as backing store (simple, no server needed)

4. **Mock Data Realism**:
   - Create synthetic events matching **real Compass structure** (research first)
   - Include various event types: excursions, performances, assemblies, fundraisers, free dress, permissions
   - Include mixed year levels and classes to test filtering
   - Include different date ranges to test date filtering

## Next Steps (Ready to Build)

1. **Confirm technical decisions** above (especially Compass integration method)
2. **Start Day 1**: Project scaffold + mock data + CLI skeleton
3. **Days 2-3**: Build filtering pipeline with mock data (parallel: research real Compass)
4. **Days 4-10**: Swap real Compass adapter, build Flask + web UI, test, polish

**Expected output on Day 10**: A working, locally-running tool you can immediately use with your real Compass account.
