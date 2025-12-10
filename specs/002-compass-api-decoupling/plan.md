# Implementation Plan: Compass API Decoupling and Mock Data Infrastructure

**Branch**: `002-compass-api-decoupling` | **Date**: 2025-12-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-compass-api-decoupling/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Decouple the Compass API integration from the Bellweaver application to enable local development and CI/CD testing without requiring real Compass credentials or dealing with geo-blocking. The system will support two operational modes (real vs. mock) via environment configuration, allowing developers to use realistic sample data for development and testing while maintaining production connectivity to real Compass API.

## Technical Context

**Language/Version**: Python 3.11 (Poetry-managed)
**Primary Dependencies**:
- **Compass Package**: requests (HTTP), beautifulsoup4 (HTML parsing), Pydantic (models)
- **Bellweaver App**: Flask (API), SQLAlchemy 2.0 (ORM), Typer (CLI), compass-client (new package dependency)
**Storage**: SQLite with SQLAlchemy ORM (Bellweaver), JSON files for mock data (Compass package)
**Testing**: pytest + pytest-cov (both packages), separate test suites
**Target Platform**: Linux server (Docker) and macOS (local development)
**Project Type**: Multi-package monorepo (Compass API library + Bellweaver web application)
**Performance Goals**: <30 seconds for local startup with mock data, <5 minutes for mock data refresh
**Constraints**: CI/CD must work in geo-blocked environments (GitHub runners), mock data size <10MB, packages must be independently testable
**Scale/Scope**: 2 Python packages in monorepo, ~5k LOC total, single Compass school integration

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: Constitution file is template-only (not yet populated with project-specific principles). Proceeding with standard engineering best practices:

- **Separation of Concerns**: ✓ Multi-package approach provides true separation
- **Testability**: ✓ Existing test coverage ~80%, packages independently testable
- **Configuration Management**: ⚠️ NEEDS IMPLEMENTATION - No environment-based mode switching
- **CI/CD Hygiene**: ⚠️ NEEDS IMPLEMENTATION - No path-based workflow filtering per package
- **Documentation**: ⚠️ NEEDS UPDATE - Package structure and mock mode usage not documented
- **Complexity**: ⚠️ REVIEW REQUIRED - Multi-package monorepo adds structural complexity

**Multi-Package Justification**:
- Enables true decoupling (Compass package has zero Bellweaver dependencies)
- Allows independent versioning and testing
- Facilitates separate CI workflows (primary requirement)
- Potential for future PyPI publication
- Aligns with "completely decouple" requirement in spec

**Re-evaluation After Phase 1 (Complete)**: ✓ Multi-package structure justified

Post-design analysis confirms the multi-package approach is appropriate:

**Benefits Realized**:
- ✓ Clear API boundaries documented in contracts/compass-client-api.md
- ✓ Interface parity enforced via contracts/client-interface.md
- ✓ Factory pattern enables seamless mode switching
- ✓ Mock data schema provides validation and versioning
- ✓ Package dependencies are one-way only (bellweaver → compass-client)
- ✓ Independent test suites enable selective CI (70% reduction in test runs)

**Complexity Managed**:
- ✓ Poetry path dependencies simplify local development
- ✓ Clear migration path documented in data-model.md and quickstart.md
- ✓ Only 2 packages (minimal monorepo overhead)
- ✓ Shared development patterns (both use Poetry, pytest, Pydantic)

**Decision**: Proceed with multi-package architecture. Benefits (true decoupling, independent testing, clear contracts) outweigh structural complexity.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
packages/
├── compass-client/              # NEW: Independent Compass API package
│   ├── compass_client/
│   │   ├── __init__.py          # Public API: CompassClient, CompassMockClient, create_client
│   │   ├── client.py            # MOVE: Real Compass HTTP client (from bellweaver)
│   │   ├── mock_client.py       # MOVE: Mock client (from bellweaver)
│   │   ├── models.py            # MOVE: CompassEvent, CompassUser (from bellweaver)
│   │   ├── parser.py            # MOVE: CompassParser (from bellweaver)
│   │   ├── factory.py           # NEW: Client factory with mode detection
│   │   └── exceptions.py        # NEW: Compass-specific exceptions
│   │
│   ├── data/                    # Mock data committed with package
│   │   ├── mock/
│   │   │   ├── compass_user.json
│   │   │   ├── compass_events.json
│   │   │   └── schema_version.json
│   │   └── README.md            # Mock data documentation
│   │
│   ├── tests/
│   │   ├── unit/                # Unit tests for client, parser, models
│   │   ├── integration/         # Integration tests with real API (optional)
│   │   └── conftest.py          # Fixtures for compass package
│   │
│   ├── pyproject.toml           # NEW: Package configuration
│   ├── README.md                # NEW: Package documentation
│   └── .env.example             # NEW: Compass package environment template
│
└── bellweaver/                  # Modified Bellweaver application
    ├── bellweaver/
    │   ├── db/                  # Database layer (existing)
    │   ├── mappers/             # KEEP: compass_event_to_event (Bellweaver-specific)
    │   ├── cli/                 # CLI commands (existing)
    │   │   └── commands/
    │   │       ├── compass.py   # MODIFY: Use compass_client package
    │   │       ├── mock.py      # MODIFY: Delegate to compass_client CLI
    │   │       └── api.py
    │   └── api/                 # Flask REST API (existing)
    │       └── routes.py        # MODIFY: Import from compass_client package
    │
    ├── tests/
    │   └── integration/
    │       └── test_family_api.py  # MODIFY: Mock compass_client package
    │
    └── pyproject.toml           # MODIFY: Add compass-client dependency

frontend/                        # React application (no changes required)

.github/
└── workflows/
    ├── test-bellweaver.yml      # MODIFY: Test Bellweaver only (filters packages/bellweaver/**)
    └── test-compass.yml         # NEW: Test Compass package only (filters packages/compass-client/**)

.env.example                     # MODIFY: Add COMPASS_MODE variable
docker-compose.yml               # MODIFY: Install both packages
```

**Structure Decision**: Multi-package monorepo with two independent Python packages:

1. **compass-client**: Standalone library for Compass API integration
   - Independently testable and versionable
   - Contains all Compass-specific code (client, models, parser, mock data)
   - Can be published to PyPI in future if desired
   - No dependencies on Bellweaver

2. **bellweaver**: Main application that consumes compass-client
   - Depends on compass-client via Poetry path dependency (initially)
   - Keeps application-specific logic (mappers, DB models, API routes)
   - No direct Compass API knowledge

This provides true decoupling and allows separate CI workflows for each package.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Complexity Added | Why Needed | Simpler Alternative Rejected Because |
|------------------|------------|-------------------------------------|
| Multi-package monorepo | True decoupling of Compass API from Bellweaver | In-package separation (adapters/) doesn't prevent tight coupling, doesn't enable independent versioning/testing, harder to enforce CI separation |
| Separate pyproject.toml files | Independent package management per package | Single pyproject.toml would couple dependencies and make selective testing impossible |
| Poetry path dependencies | Local development with monorepo packages | Publishing to PyPI is premature; path deps allow local iteration while maintaining package independence |
| Duplicate test infrastructure | Each package needs its own test suite | Shared test infrastructure would couple packages and prevent independent CI workflows |

**Complexity Justification**: The multi-package approach adds structural complexity but is necessary to achieve the "complete decoupling" requirement. Benefits:
- ✓ Zero dependency from compass-client → bellweaver
- ✓ Independent test execution and CI workflows
- ✓ Clear API boundaries via package imports
- ✓ Future PyPI publication becomes trivial
- ✓ Aligns with Python packaging best practices

**Mitigation**: Use Poetry workspace features (if available) or clear documentation to reduce maintenance overhead.
