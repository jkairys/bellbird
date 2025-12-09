# Implementation Plan: Family Management System

**Branch**: `001-family-management` | **Date**: 2025-12-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-family-management/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature enables parents to define their family structure (children, organisations, and communication channels) to enable personalized event filtering. Parents can create child profiles, define organisations (schools, daycares, sports teams), associate children with organisations, and configure communication channels (initially Compass only). This provides the foundational data model for intelligent event filtering and aggregation.

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: Flask (web framework), SQLAlchemy 2.0 (ORM), Typer (CLI), Pydantic (validation), React 18 (frontend), Vite (build tool)
**Storage**: SQLite with SQLAlchemy ORM (local-first, PostgreSQL-ready patterns)
**Testing**: pytest + pytest-cov (backend), React Testing Library (frontend)
**Target Platform**: Local development (macOS/Linux/Windows), Docker container deployment
**Project Type**: Web application (Flask backend + React frontend)
**Performance Goals**: <200ms API response time, <2s page load, handle 10 children + 20 organisations without degradation
**Constraints**: Single-user MVP, local SQLite database, must maintain existing Adapter-Parser-Application separation, all credentials encrypted at rest
**Scale/Scope**: 10 children max per family, 20 organisations, 4 new database models, 6-8 new API endpoints, 3-5 new React components

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with `.specify/memory/constitution.md` principles:

- [x] **Separation of Concerns**: Feature does NOT involve new external APIs - it extends the existing database models and API endpoints. Existing Compass adapter integration remains unchanged. ✅
- [x] **Test-First**: Tests will be written before implementation for all new models, API endpoints, and UI components. Acceptance criteria from spec.md will be encoded in tests. ✅
- [x] **Secure by Default**: Compass credentials will use existing encrypted credential storage (Fernet-based). Child and organisation data is non-sensitive metadata stored in local SQLite. ✅
- [x] **Local-First MVP**: Design uses local SQLite database with single-user access. No cloud features, authentication, or multi-tenancy in this phase. Data model designed to allow future multi-user expansion. ✅
- [x] **Simplicity & Pragmatism**: No new abstractions beyond standard ORM models. Using direct SQLAlchemy access (no repository pattern). Standard REST API patterns. No premature optimization. ✅

**Violations Requiring Justification**: None

## Project Structure

### Documentation (this feature)

```text
specs/001-family-management/
├── spec.md              # Feature specification (already exists)
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── openapi.yaml     # REST API contract
│   └── schemas/         # Request/response schemas
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── bellweaver/
│   ├── db/
│   │   ├── models.py              # ORM models (NEW: Child, Organisation, CommunicationChannel, ChildOrganisation)
│   │   ├── database.py            # Database connection and session management (EXISTING)
│   │   └── credentials.py         # Encrypted credential storage (EXISTING, REUSE)
│   ├── models/
│   │   └── family.py              # Pydantic models for validation (NEW)
│   ├── api/
│   │   ├── __init__.py            # Flask app factory (EXISTING)
│   │   └── routes.py              # API route blueprints (EXTEND: add family routes)
│   └── cli/
│       ├── main.py                # CLI entry point (EXISTING)
│       └── commands/
│           └── family.py          # Family management CLI commands (NEW, OPTIONAL)
└── tests/
    ├── unit/
    │   ├── test_family_models.py  # Test Pydantic models (NEW)
    │   └── test_db_models.py      # Test ORM models (EXTEND)
    ├── integration/
    │   ├── test_family_api.py     # Test family API endpoints (NEW)
    │   └── test_database.py       # Test database operations (EXTEND)
    └── fixtures/
        └── family_data.py         # Test data fixtures (NEW)

frontend/
├── src/
│   ├── components/
│   │   ├── family/                # Family management UI components (NEW)
│   │   │   ├── ChildList.jsx
│   │   │   ├── ChildForm.jsx
│   │   │   ├── OrganisationList.jsx
│   │   │   ├── OrganisationForm.jsx
│   │   │   └── ChannelConfig.jsx
│   │   └── Dashboard.jsx          # Main dashboard (EXISTING, may need updates)
│   ├── services/
│   │   ├── api.js                 # API client (EXTEND: add family endpoints)
│   │   └── familyApi.js           # Family-specific API calls (NEW)
│   └── pages/
│       └── FamilyManagement.jsx   # Family management page (NEW)
└── tests/
    └── components/
        └── family/                # Component tests (NEW)
```

**Structure Decision**: Web application structure (Option 2). Backend extends existing Flask API and SQLAlchemy models. Frontend adds new React components for family management UI. This feature primarily adds new database models, API endpoints, and UI components without modifying the existing Compass adapter/parser architecture.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations - table remains empty.

## Post-Design Constitution Re-Check

*Re-evaluated after Phase 1 design completion (research.md, data-model.md, contracts/)*

- [x] **Separation of Concerns**: ✅ PASS
  - No new adapters created - feature is purely data model + API + UI
  - Existing Compass adapter remains unchanged
  - Clear separation: Database (ORM) → Validation (Pydantic) → API (Flask routes) → UI (React)

- [x] **Test-First**: ✅ PASS
  - quickstart.md outlines test-first workflow
  - Tests planned for: Pydantic models, ORM models, API endpoints, React components
  - Acceptance criteria from spec.md will be encoded in tests

- [x] **Secure by Default**: ✅ PASS
  - Communication channel credentials will use existing encrypted `Credential` table
  - No new credential storage mechanism needed
  - Child/organisation data is non-sensitive metadata (names, dates, types)
  - All API endpoints will validate input before database operations

- [x] **Local-First MVP**: ✅ PASS
  - SQLite database with SQLAlchemy ORM
  - Single-user design (no authentication/multi-tenancy in this phase)
  - Data model includes `created_at`/`updated_at` fields to support future audit trails
  - Foreign keys and relationships designed to scale to PostgreSQL when needed
  - No cloud features, job queues, or caching introduced

- [x] **Simplicity & Pragmatism**: ✅ PASS
  - Direct SQLAlchemy queries (no repository pattern)
  - React Context for state management (no Redux)
  - Standard REST API patterns (no GraphQL)
  - Polymorphic channel table with JSON config (flexible, no per-channel tables)
  - Explicit association table for many-to-many (allows future metadata without migration)
  - All complexity justified in research.md

**Design Validation**: All constitution principles satisfied. No violations requiring justification.

---

## Phase Summary

### Phase 0: Research (COMPLETE)
- ✅ `research.md` - 6 research questions resolved with decisions and rationale
- Key decisions: Explicit association table, polymorphic channel model, multi-layer validation, REST API, React Context

### Phase 1: Design & Contracts (COMPLETE)
- ✅ `data-model.md` - 4 entities defined with relationships, validation rules, state transitions
- ✅ `contracts/openapi.yaml` - Complete REST API specification with 14 endpoints, schemas, error responses
- ✅ `quickstart.md` - Developer quick reference with architecture, examples, checklists
- ✅ Agent context updated (CLAUDE.md)

### Phase 2: Implementation Planning (NEXT)
- ⏭️ Run `/speckit.tasks` to generate `tasks.md` with dependency-ordered implementation tasks
- Tasks will cover: Backend (ORM, Pydantic, API, tests), Frontend (components, services, tests)

---

## Artifacts Generated

All design artifacts have been created in `specs/001-family-management/`:

1. **plan.md** (this file) - Implementation plan with technical context and constitution compliance
2. **research.md** - Research findings and design decisions
3. **data-model.md** - Entity definitions, relationships, validation rules
4. **contracts/openapi.yaml** - Complete OpenAPI 3.0 specification
5. **quickstart.md** - Developer quick reference guide

**Branch**: `001-family-management` (current)
**Status**: Ready for Phase 2 (task generation via `/speckit.tasks`)

---

## Ready for Implementation

The design phase is complete. All NEEDS CLARIFICATION items from Technical Context have been resolved through research. The design satisfies all Constitution principles.

**Next Step**: User should review these artifacts and then run `/speckit.tasks` to generate the implementation task list.
