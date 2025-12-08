<!--
SYNC IMPACT REPORT - Constitution v1.0.0

Version Change: [Template] → 1.0.0 (Initial ratification)

Principles Defined:
- I. Separation of Concerns (Adapter-Parser-Application)
- II. Test-First Development
- III. Secure by Default
- IV. Local-First MVP, Cloud-Ready Architecture
- V. Simplicity & Pragmatism

Sections Added:
- Core Principles (5 principles defined)
- Development Standards
- Quality Gates
- Governance

Templates Requiring Updates:
- ✅ plan-template.md: Constitution Check section aligned
- ✅ spec-template.md: Requirements align with security/testing principles
- ✅ tasks-template.md: Task structure supports parallel execution and test-first
- ⚠️  Command files: Review for agent-specific references if applicable

Follow-up TODOs: None - all placeholders filled

Rationale for v1.0.0:
- First complete constitution for Bellweaver project
- Extracted principles from existing architecture decisions
- No prior version existed
-->

# Bellweaver Constitution

## Core Principles

### I. Separation of Concerns (Adapter-Parser-Application)

**Architecture Pattern**: All external data sources MUST follow the three-layer pattern:

1. **Adapter Layer** - Returns raw dictionaries from HTTP/API calls
2. **Parser Layer** - Transforms raw dicts into validated Pydantic models
3. **Application Layer** - Consumes clean, type-safe domain models

**Rationale**: This separation enables:
- Independent testing of HTTP communication vs. validation logic
- Easy swapping between real and mock adapters (both return dicts)
- Graceful handling of API changes without touching business logic
- Storage of raw JSON for audit trails and re-parsing with updated models
- Clear distinction between network errors and validation errors

**Enforcement**:
- Adapters MUST NOT import Pydantic models
- Parsers MUST provide generic `parse()` methods using TypeVar
- Application code MUST NOT access raw API responses directly

### II. Test-First Development

**Practice**: Tests MUST be written before implementation for all user-facing features.

**Process**:
1. Write tests that encode acceptance criteria
2. Obtain user approval on test scenarios
3. Verify tests fail (RED)
4. Implement feature (GREEN)
5. Refactor for quality (REFACTOR)

**Scope**:
- **Unit tests**: Library functions, parsers, validators
- **Integration tests**: Adapter authentication, database operations, API endpoints
- **Contract tests**: Required for new library contracts and contract changes

**Test Environment**:
- Mock clients (e.g., `compass_mock.py`) MUST be provided for all external adapters
- Integration tests MAY use real credentials via environment variables
- Tests MUST be runnable both with mocks and real services

**NON-NEGOTIABLE**: No feature ships without tests. Tests failing = implementation incomplete.

### III. Secure by Default

**Credentials**:
- All credentials MUST be encrypted at rest using Fernet symmetric encryption
- Encryption keys MUST be stored in environment variables, NEVER in code
- `.env` files containing secrets MUST be gitignored
- `.env.example` templates MUST be provided with placeholder values

**Sensitive Data**:
- User data (calendar events, personal info) MUST be stored in local SQLite with encrypted credentials
- No credentials or user data in logs unless explicitly approved for debugging
- Database files MUST be gitignored

**Environment Security**:
- Production secrets MUST use separate environment files from development
- Docker containers MUST mount `.env` as read-only
- Auto-generated encryption keys MUST be saved to `.env` on first run

**Enforcement**: All credential-handling code MUST pass security review before merge.

### IV. Local-First MVP, Cloud-Ready Architecture

**MVP Principle**: Start simple, local, single-user. Build for cloud migration later.

**Current Phase (MVP)**:
- SQLite database (local file storage)
- Poetry dependency management
- Flask API + React frontend in single Docker container
- Local development with hot reload

**Future-Proofing Requirements**:
- Database access MUST use SQLAlchemy ORM (enables PostgreSQL migration)
- Database sessions MUST use proper session management patterns
- Foreign key constraints MUST be enabled in SQLite
- API design MUST support multi-tenancy patterns (user scoping)
- Avoid SQLite-specific features that don't translate to PostgreSQL

**Migration Path**: When scaling becomes necessary, the architecture MUST support:
- PostgreSQL database
- Multi-container deployment
- Job queues for background sync
- Redis caching layer
- Multi-user authentication

**Constraint**: Do NOT build cloud features before they're needed. Focus on working local MVP first.

### V. Simplicity & Pragmatism

**YAGNI (You Aren't Gonna Need It)**: Only build what's required NOW.

**Prohibited Complexity**:
- ❌ Don't create abstractions for single use cases
- ❌ Don't add features "for future flexibility"
- ❌ Don't build multi-source support until Compass works
- ❌ Don't add observability dashboards until performance issues exist
- ❌ Don't create helpers/utilities for one-time operations

**Encouraged Simplicity**:
- ✅ Use HTTP requests over browser automation
- ✅ Use Flask over FastAPI for smaller projects
- ✅ Use SQLite before PostgreSQL
- ✅ Use Pydantic for validation (simple, effective)
- ✅ Use Typer for CLI (clean, minimal boilerplate)

**Code Style**:
- Prefer readability over cleverness
- Three similar lines are better than premature abstraction
- Direct database access is fine until repository pattern is needed
- Delete unused code completely (no commented-out code, no `_vars`, no `# removed` comments)

**Justification Required**: Any pattern from "Prohibited Complexity" MUST be justified in plan.md Complexity Tracking table before implementation.

## Development Standards

### Technology Stack (Fixed)

**Backend**:
- Language: Python 3.10+
- Framework: Flask
- Database: SQLite (SQLAlchemy ORM)
- CLI: Typer
- Package Manager: Poetry

**Frontend**:
- Framework: React 18
- Build Tool: Vite
- Package Manager: npm

**Testing**:
- Framework: pytest + pytest-cov
- Mocking: Built-in unittest.mock
- Coverage: Aim for 80%+ on critical paths

**Quality Tools**:
- Formatting: black
- Linting: flake8
- Type Checking: mypy

### Working Directory Standards

- Poetry commands: Run from `backend/` directory
- Docker commands: Run from project root
- npm commands: Run from `frontend/` directory
- Git commands: Run from project root

### Commit Standards

**Message Format**:
- Use imperative mood: "Add feature" not "Added feature"
- Prefix with component: `db:`, `api:`, `cli:`, `frontend:`, `docs:`
- Examples:
  - `db: add encrypted credential storage`
  - `api: implement /events endpoint with batch parsing`
  - `cli: add compass sync command with date range`

**Workflow**:
- Create feature branches: `<slug>-YYYYMMDD-HHMMSS`
- Always branch from latest `main`
- Commit changes incrementally as work progresses
- Commit before prompting user for input
- Run tests before creating PR
- Use `gh pr create` for pull requests

## Quality Gates

### Pre-Merge Checklist

Every pull request MUST satisfy:

1. **Tests Pass**: `poetry run pytest` exits 0
2. **Formatting**: Code formatted with `black`
3. **Type Safety**: Critical paths have type hints, `mypy` passes
4. **Security**: No credentials in code, encryption used for sensitive data
5. **Documentation**: User-facing features documented in `docs/`
6. **Constitution Check**: No principle violations, or violations justified in plan.md

### Integration Test Requirements

Integration tests MUST exist for:
- New external adapter methods (Compass API calls)
- Database schema changes
- API endpoint additions
- CLI command additions

### Constitution Compliance

Reviewers MUST verify:
- Adapter-Parser-Application separation maintained
- Tests written before implementation (check git history)
- Credentials encrypted and not committed
- No premature abstractions or cloud features

## Governance

### Amendment Process

1. **Proposal**: Document proposed change with rationale
2. **Review**: Discuss impact on existing codebase
3. **Migration Plan**: If breaking, provide migration strategy
4. **Version Bump**: Follow semantic versioning (MAJOR.MINOR.PATCH)
5. **Template Sync**: Update dependent templates in `.specify/templates/`
6. **Approval**: Merge after review

### Versioning Policy

- **MAJOR**: Backward-incompatible principle removals or redefinitions
- **MINOR**: New principles added or materially expanded guidance
- **PATCH**: Clarifications, wording fixes, non-semantic refinements

### Compliance Review

- All PRs MUST include constitution compliance check
- Architecture decisions MUST reference relevant principles
- Violations MUST be justified in plan.md Complexity Tracking section
- Project lead reviews constitution quarterly for necessary updates

### Runtime Guidance

For interactive development guidance, agents should consult:
- `CLAUDE.md` - Claude Code context and workflow instructions
- `docs/architecture.md` - System design and technical decisions
- `README.md` - Quick start and project overview

**Version**: 1.0.0 | **Ratified**: 2025-12-09 | **Last Amended**: 2025-12-09
