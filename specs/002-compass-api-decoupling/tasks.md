# Tasks: Compass API Decoupling and Mock Data Infrastructure

**Input**: Design documents from `/specs/002-compass-api-decoupling/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Multi-Package Monorepo Structure)

**Purpose**: Initialize monorepo structure with two independent Python packages

- [X] T001 Create `packages/` directory at repository root
- [X] T002 [P] Create `packages/compass-client/` directory structure (compass_client/, data/mock/, tests/, README.md)
- [X] T003 [P] Create `packages/bellweaver/` directory structure (move from backend/)
- [X] T004 [P] Create `packages/compass-client/pyproject.toml` with Poetry configuration for compass-client package
- [X] T005 [P] Create `packages/compass-client/README.md` with package documentation
- [X] T006 [P] Create `.github/workflows/test-compass.yml` for compass-client CI workflow
- [X] T007 [P] Create `.github/workflows/test-bellweaver.yml` for bellweaver CI workflow
- [X] T008 Update root `.env.example` with COMPASS_MODE variable

---

## Phase 2: Foundational (Compass Client Package Core)

**Purpose**: Core compass-client package infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 [P] Move `backend/bellweaver/models/compass.py` to `packages/compass-client/compass_client/models.py`
- [X] T010 [P] Move `backend/bellweaver/parsers/compass.py` to `packages/compass-client/compass_client/parser.py`
- [X] T011 [P] Move `backend/bellweaver/adapters/compass.py` to `packages/compass-client/compass_client/client.py`
- [X] T012 [P] Move `backend/bellweaver/adapters/compass_mock.py` to `packages/compass-client/compass_client/mock_client.py`
- [X] T013 Create `packages/compass-client/compass_client/__init__.py` with public API exports
- [X] T014 Create `packages/compass-client/compass_client/exceptions.py` with CompassClientError, CompassAuthenticationError, CompassParseError
- [X] T015 Create `packages/compass-client/compass_client/factory.py` with create_client() factory function
- [X] T016 [P] Move mock data from `backend/data/mock/` to `packages/compass-client/data/mock/`
- [X] T017 [P] Create `packages/compass-client/data/mock/schema_version.json` with version metadata
- [X] T018 [P] Create `packages/compass-client/data/mock/README.md` with mock data documentation
- [X] T019 Update imports in compass_client package to use relative imports
- [X] T020 Install compass-client package locally with `poetry install` in packages/compass-client/
- [X] T021 Update `packages/bellweaver/pyproject.toml` to add compass-client path dependency
- [X] T022 Install bellweaver package with compass-client dependency using `poetry install` in packages/bellweaver/

**Checkpoint**: Foundation ready - compass-client package is functional, user story implementation can now begin

---

## Phase 3: User Story 1 - Local Development with Sample Data (Priority: P1) 🎯 MVP

**Goal**: Enable developers to start the application locally with realistic sample data without requiring Compass credentials

**Independent Test**: Start application in mock mode, verify sample data loads, confirm all API endpoints return data matching Compass API schema without real credentials

### Implementation for User Story 1

- [X] T023 [P] [US1] Update CompassMockClient in `packages/compass-client/compass_client/mock_client.py` to load from data/mock/ files
- [X] T024 [P] [US1] Implement _load_mock_events() method in CompassMockClient to read compass_events.json
- [X] T025 [P] [US1] Implement _load_mock_user() method in CompassMockClient to read compass_user.json
- [X] T026 [US1] Implement fallback to hardcoded data in CompassMockClient if files missing
- [X] T027 [US1] Implement factory create_client() function in `packages/compass-client/compass_client/factory.py` with mode detection
- [X] T028 [US1] Add COMPASS_MODE environment variable handling in factory.py (reads from os.getenv)
- [X] T029 [US1] Implement configuration precedence in factory: explicit mode > env var > default "real"
- [X] T030 [US1] Add validation in factory.py to ensure mode is "real" or "mock"
- [X] T031 [US1] Update bellweaver CLI commands in `packages/bellweaver/bellweaver/cli/commands/compass.py` to use create_client()
- [X] T032 [US1] Update bellweaver API routes in `packages/bellweaver/bellweaver/api/routes.py` to use create_client()
- [X] T033 [US1] Update all bellweaver imports from `bellweaver.adapters.compass` to `compass_client`
- [X] T034 [US1] Remove old compass code from `packages/bellweaver/bellweaver/adapters/` (compass.py, compass_mock.py)
- [X] T035 [US1] Test local development: Set COMPASS_MODE=mock and start bellweaver API server
- [X] T036 [US1] Verify API endpoints return mock data: curl localhost:5000/user and localhost:5000/events

**Checkpoint**: At this point, User Story 1 should be fully functional - developers can run the app locally with mock data

---

## Phase 4: User Story 2 - CI/CD Pipeline Testing (Priority: P2)

**Goal**: Enable CI/CD pipelines to run tests without being blocked by geo-restrictions on Compass API

**Independent Test**: Run test suite in GitHub runner with mock mode enabled and verify all tests pass without making real Compass API calls

### Implementation for User Story 2

- [X] T037 [P] [US2] Create mock_validator.py in `packages/compass-client/compass_client/mock_validator.py` with load_and_validate_mock_data() function
- [X] T038 [P] [US2] Implement validate_mock_data_schema() function in mock_validator.py to validate all mock files
- [X] T039 [US2] Create MockDataValidationError exception in mock_validator.py
- [X] T040 [US2] Create startup.py in `packages/bellweaver/bellweaver/startup.py` with validate_mock_data_startup() function
- [X] T041 [US2] Implement startup_checks() function in startup.py to run validation based on compass_mode
- [X] T042 [US2] Create StartupValidationError exception in startup.py
- [X] T043 [US2] Integrate startup validation into Flask app factory in `packages/bellweaver/bellweaver/api/__init__.py`
- [X] T044 [US2] Update test fixtures in `packages/bellweaver/tests/conftest.py` to set COMPASS_MODE=mock
- [X] T045 [US2] Update bellweaver test workflow in `.github/workflows/test-bellweaver.yml` to set COMPASS_MODE=mock
- [X] T046 [US2] Configure path filters in test-bellweaver.yml: packages/bellweaver/** and packages/compass-client/**
- [X] T047 [US2] Test CI pipeline: Create PR and verify bellweaver tests run with mock mode in GitHub Actions
- [X] T048 [US2] Verify zero authentication failures in CI logs

**Checkpoint**: ✅ At this point, User Stories 1 AND 2 should both work - local dev uses mock data AND CI runs without geo-blocking

---

## Phase 5: User Story 3 - Mock Data Refresh (Priority: P3)

**Goal**: Enable developers with Compass credentials to refresh committed mock data using real Compass API

**Independent Test**: Run mock data update command with real Compass credentials, verify new sample data is fetched and stored, confirm updated data matches current API schemas

### Implementation for User Story 3

- [ ] T049 [P] [US3] Create cli module in `packages/compass-client/compass_client/cli/__init__.py`
- [ ] T050 [US3] Create refresh_mock_data.py in `packages/compass-client/compass_client/cli/refresh_mock_data.py` with CLI command
- [ ] T051 [US3] Implement fetch_real_data() function in refresh_mock_data.py to authenticate and fetch from real API
- [ ] T052 [US3] Implement sanitize_user_data() function in refresh_mock_data.py to remove PII from user data
- [ ] T053 [US3] Implement sanitize_event_data() function in refresh_mock_data.py to remove PII from event data
- [ ] T054 [US3] Implement write_mock_data() function in refresh_mock_data.py to write sanitized data to JSON files
- [ ] T055 [US3] Implement update_schema_version() function in refresh_mock_data.py to update schema_version.json
- [ ] T056 [US3] Add CLI entry point in `packages/compass-client/pyproject.toml` for refresh-mock-data command
- [ ] T057 [US3] Add mock validate CLI command in `packages/bellweaver/bellweaver/cli/commands/mock.py`
- [ ] T058 [US3] Test mock data refresh: Run `poetry run python -m compass_client.cli refresh-mock-data` with real credentials
- [ ] T059 [US3] Verify sanitized data: Check that PII is removed from updated compass_user.json and compass_events.json
- [ ] T060 [US3] Verify updated data validates: Run CompassParser.parse() on refreshed mock data
- [ ] T061 [US3] Commit updated mock data to repository

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work - mock data can be refreshed when API changes

---

## Phase 6: User Story 4 - Selective CI Workflow Execution (Priority: P4)

**Goal**: Optimize CI workflows to run Compass API library tests only when library code changes

**Independent Test**: Make changes to Bellweaver application code (not Compass library), trigger CI, verify Compass API library tests are skipped while Bellweaver tests run

### Implementation for User Story 4

- [ ] T062 [US4] Configure path-based workflow filters in `.github/workflows/test-compass.yml`
- [ ] T063 [US4] Add paths filter for compass-client in test-compass.yml: packages/compass-client/**
- [ ] T064 [US4] Add dorny/paths-filter@v3 action to detect-changes job in test-compass.yml
- [ ] T065 [US4] Create conditional job execution in test-compass.yml based on paths-filter output
- [ ] T066 [US4] Add compass-library-skipped dummy job in test-compass.yml for required status checks
- [ ] T067 [US4] Update test-compass.yml to run compass-client tests only when compass-client code changes
- [ ] T068 [US4] Configure bellweaver workflow to always run (current behavior maintained)
- [ ] T069 [US4] Test path filtering: Create PR with bellweaver-only changes and verify compass tests are skipped
- [ ] T070 [US4] Test path filtering: Create PR with compass-client changes and verify compass tests run
- [ ] T071 [US4] Configure branch protection rules to accept either test-compass or compass-library-skipped
- [ ] T072 [US4] Measure CI time savings: Compare workflow durations before and after selective execution

**Checkpoint**: All user stories should now be independently functional - CI is optimized to run only necessary tests

---

## Phase 7: Testing & Validation (Cross-Story Quality Assurance)

**Purpose**: Comprehensive testing across all user stories and package integration

- [ ] T073 [P] Write unit tests for CompassClient in `packages/compass-client/tests/unit/test_client.py`
- [ ] T074 [P] Write unit tests for CompassMockClient in `packages/compass-client/tests/unit/test_mock_client.py`
- [ ] T075 [P] Write unit tests for CompassParser in `packages/compass-client/tests/unit/test_parser.py`
- [ ] T076 [P] Write unit tests for CompassEvent and CompassUser models in `packages/compass-client/tests/unit/test_models.py`
- [ ] T077 [P] Write unit tests for create_client() factory in `packages/compass-client/tests/unit/test_factory.py`
- [ ] T078 [P] Write contract compliance tests in `packages/compass-client/tests/integration/test_interface_parity.py`
- [ ] T079 [P] Write mock data validation tests in `packages/compass-client/tests/unit/test_mock_validator.py`
- [ ] T080 Write integration tests for bellweaver with mock compass-client in `packages/bellweaver/tests/integration/test_compass_integration.py`
- [ ] T081 [P] Update existing bellweaver tests to use mock compass-client
- [ ] T082 Run full test suite for compass-client: `cd packages/compass-client && poetry run pytest --cov`
- [ ] T083 Run full test suite for bellweaver: `cd packages/bellweaver && poetry run pytest --cov`
- [ ] T084 Verify test coverage for compass-client package (target: >80%)
- [ ] T085 Verify test coverage for bellweaver package (maintained at current level)

---

## Phase 8: Documentation & Developer Experience

**Purpose**: Complete documentation for developers using the decoupled architecture

- [ ] T086 [P] Update `packages/compass-client/README.md` with installation instructions
- [ ] T087 [P] Add usage examples to compass-client README.md for both real and mock modes
- [ ] T088 [P] Document public API in compass-client README.md (classes, functions, exceptions)
- [ ] T089 [P] Update `packages/bellweaver/README.md` with compass-client integration instructions
- [ ] T090 [P] Update root `README.md` with monorepo structure and package overview
- [ ] T091 [P] Create migration guide in `docs/migration-compass-decoupling.md` for developers
- [ ] T092 Update `docs/architecture.md` with multi-package monorepo structure
- [ ] T093 Update `docs/quick-start.md` with compass-client installation steps
- [ ] T094 Update `CLAUDE.md` with new import patterns and package structure
- [ ] T095 [P] Add troubleshooting section to compass-client README.md
- [ ] T096 [P] Add troubleshooting section to bellweaver README.md for compass integration
- [ ] T097 Validate quickstart.md by following all steps from clean environment

---

## Phase 9: Docker & Deployment

**Purpose**: Update Docker configuration for multi-package monorepo

- [ ] T098 Update `Dockerfile` to build compass-client package first
- [ ] T099 Update Dockerfile to install compass-client in bellweaver build stage
- [ ] T100 Update `docker-compose.yml` to set COMPASS_MODE=mock for development
- [ ] T101 Update docker-compose.yml to mount packages/ directory structure
- [ ] T102 Test Docker build: `docker-compose build`
- [ ] T103 Test Docker run with mock mode: `docker-compose up` and verify COMPASS_MODE=mock
- [ ] T104 Test Docker run with real mode: Set COMPASS_MODE=real and verify real API connection
- [ ] T105 Update Docker documentation in README.md with new environment variables

---

## Phase 10: Polish & Final Validation

**Purpose**: Final cleanup and validation across all user stories

- [ ] T106 [P] Code cleanup: Remove unused imports in compass-client package
- [ ] T107 [P] Code cleanup: Remove unused imports in bellweaver package
- [ ] T108 [P] Code cleanup: Remove deprecated compass adapter files from bellweaver
- [ ] T109 Run linting on compass-client: `cd packages/compass-client && poetry run flake8`
- [ ] T110 Run linting on bellweaver: `cd packages/bellweaver && poetry run flake8`
- [ ] T111 Run type checking on compass-client with mypy: `poetry run mypy compass_client`
- [ ] T112 Run formatting on compass-client: `cd packages/compass-client && poetry run black .`
- [ ] T113 Run formatting on bellweaver: `cd packages/bellweaver && poetry run black .`
- [ ] T114 Validate all user stories work independently: Test US1, US2, US3, US4 in isolation
- [ ] T115 Validate quickstart.md from clean environment
- [ ] T116 Run security scan with safety: `poetry run safety check`
- [ ] T117 Update CHANGELOG.md with feature summary
- [ ] T118 Final end-to-end test: Local development with mock mode
- [ ] T119 Final end-to-end test: CI pipeline with mock mode
- [ ] T120 Final end-to-end test: Mock data refresh with real credentials
- [ ] T121 Final end-to-end test: Selective CI workflow execution

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational (Phase 2) - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational (Phase 2) AND User Story 1 - Depends on US1 for mock mode
  - User Story 3 (P3): Can start after Foundational (Phase 2) AND User Story 1 - Depends on US1 for factory
  - User Story 4 (P4): Can start after Foundational (Phase 2) - Independent CI optimization
- **Testing (Phase 7)**: Depends on all desired user stories being complete
- **Documentation (Phase 8)**: Can proceed in parallel with Testing (Phase 7)
- **Docker (Phase 9)**: Depends on User Stories 1-3 being complete
- **Polish (Phase 10)**: Depends on all previous phases being complete

### User Story Dependencies

- **User Story 1 (P1) - Local Development**: FOUNDATIONAL - All other stories depend on this
  - Provides: create_client() factory, mock mode support, environment configuration
  - Blocks: US2 (needs mock mode), US3 (needs factory)
- **User Story 2 (P2) - CI/CD Pipeline**: Depends on US1 for mock mode functionality
  - Provides: Startup validation, CI configuration
  - Blocks: None (independent after US1)
- **User Story 3 (P3) - Mock Data Refresh**: Depends on US1 for factory and clients
  - Provides: CLI for updating mock data
  - Blocks: None (independent after US1)
- **User Story 4 (P4) - Selective CI**: Independent after Foundational phase
  - Provides: Path-based workflow filtering
  - Blocks: None (pure CI optimization)

### Within Each User Story

- **US1**: Factory → Mock Client Updates → Bellweaver Integration → Remove Old Code
- **US2**: Mock Validation → Startup Checks → CI Configuration
- **US3**: CLI Creation → Data Sanitization → Schema Updates
- **US4**: Path Filters → Conditional Jobs → Status Check Configuration

### Parallel Opportunities

**Setup Phase (T002-T008)**: All package structure tasks can run in parallel
**Foundational Phase (T009-T013, T016-T018)**: All file moves and mock data can run in parallel
**User Story 1 (T023-T025)**: Mock client methods can be implemented in parallel
**User Story 2 (T037-T039, T040-T042)**: Validation and startup modules can be created in parallel
**User Story 3 (T052-T053)**: Sanitization functions can be implemented in parallel
**Testing Phase (T073-T079)**: All unit test files can be written in parallel
**Documentation Phase (T086-T091, T095-T096)**: All documentation updates can be written in parallel

---

## Parallel Example: User Story 1 (Local Development)

```bash
# Launch all mock client methods together:
Task: "Implement _load_mock_events() method in CompassMockClient"
Task: "Implement _load_mock_user() method in CompassMockClient"

# After methods complete, update consumers:
Task: "Update bellweaver CLI commands to use create_client()"
Task: "Update bellweaver API routes to use create_client()"
```

---

## Parallel Example: Testing Phase

```bash
# Launch all unit test files together:
Task: "Write unit tests for CompassClient in packages/compass-client/tests/unit/test_client.py"
Task: "Write unit tests for CompassMockClient in packages/compass-client/tests/unit/test_mock_client.py"
Task: "Write unit tests for CompassParser in packages/compass-client/tests/unit/test_parser.py"
Task: "Write unit tests for models in packages/compass-client/tests/unit/test_models.py"
Task: "Write unit tests for factory in packages/compass-client/tests/unit/test_factory.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T008) - ~2 hours
2. Complete Phase 2: Foundational (T009-T022) - ~4 hours
3. Complete Phase 3: User Story 1 (T023-T036) - ~6 hours
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Can start app locally with COMPASS_MODE=mock
   - Mock data loads successfully
   - All API endpoints return data without credentials
5. Deploy/demo if ready

**Estimated MVP Time**: ~12 hours total

### Incremental Delivery

1. **Foundation** (Phases 1-2): Setup + Core package → Packages installable, tests pass
2. **MVP** (Phase 3): User Story 1 → Local development with mock data works ✅
3. **CI Support** (Phase 4): User Story 2 → CI pipelines work without geo-blocking ✅
4. **Mock Refresh** (Phase 5): User Story 3 → Developers can update mock data ✅
5. **CI Optimization** (Phase 6): User Story 4 → Selective test execution saves time ✅
6. **Quality** (Phases 7-8): Testing + Documentation → Production-ready
7. **Deployment** (Phases 9-10): Docker + Polish → Ready to ship

### Parallel Team Strategy

With multiple developers:

1. **Together**: Complete Setup + Foundational (Phases 1-2)
2. **Once Foundational is done**:
   - **Developer A**: User Story 1 (Phase 3) - CRITICAL PATH
   - **Developer B**: User Story 4 (Phase 6) - Independent CI work
   - **Developer C**: Documentation setup (Phase 8) - Parallel docs
3. **After US1 complete**:
   - **Developer A**: User Story 2 (Phase 4)
   - **Developer B**: User Story 3 (Phase 5)
   - **Developer C**: Testing (Phase 7)
4. **Final Push**: Docker (Phase 9) + Polish (Phase 10) together

---

## Success Criteria Validation

### SC-001: Local Development Speed
- [ ] Verify application starts with mock data in under 30 seconds
- [ ] Test all API endpoints accessible without Compass credentials

### SC-002: CI/CD Pipeline Success
- [ ] Verify Bellweaver test suite completes in GitHub runners without geo-blocking
- [ ] Confirm zero authentication failures in CI logs

### SC-003: Mock Data Refresh
- [ ] Verify mock data can be refreshed using real Compass API
- [ ] Confirm refresh completes in under 5 minutes
- [ ] Validate updated data can be committed to repository

### SC-004: Selective CI Execution
- [ ] Measure CI workflow execution reduction (target: 70%+ reduction in unnecessary runs)
- [ ] Verify Compass library tests only run when Compass code changes

### SC-005: API Endpoint Parity
- [ ] Verify 100% of existing API endpoints function identically in mock and real modes
- [ ] Test that consumers cannot observe differences except data source

### SC-006: Startup Performance
- [ ] Measure application startup time in mock mode
- [ ] Verify startup time is within 10% of real API mode

### SC-007: Authentication Success
- [ ] Verify zero authentication failures occur in CI pipelines with mock mode

---

## Total Task Count: 121 tasks

### Breakdown by Phase:
- Phase 1 (Setup): 8 tasks
- Phase 2 (Foundational): 14 tasks
- Phase 3 (User Story 1): 14 tasks
- Phase 4 (User Story 2): 12 tasks
- Phase 5 (User Story 3): 13 tasks
- Phase 6 (User Story 4): 11 tasks
- Phase 7 (Testing): 13 tasks
- Phase 8 (Documentation): 12 tasks
- Phase 9 (Docker): 8 tasks
- Phase 10 (Polish): 16 tasks

### Breakdown by User Story:
- User Story 1 (Local Development): 14 tasks
- User Story 2 (CI/CD Pipeline): 12 tasks
- User Story 3 (Mock Data Refresh): 13 tasks
- User Story 4 (Selective CI): 11 tasks
- Infrastructure (Setup + Foundational): 22 tasks
- Quality Assurance (Testing + Documentation + Docker + Polish): 49 tasks

### Parallel Opportunities Identified:
- Setup Phase: 6 parallel tasks (T002-T008)
- Foundational Phase: 8 parallel tasks (T009-T013, T016-T018)
- User Story 1: 3 parallel tasks (T023-T025)
- User Story 2: 6 parallel tasks (T037-T039, T040-T042)
- User Story 3: 2 parallel tasks (T049-T050, T052-T053)
- Testing Phase: 7 parallel tasks (T073-T079)
- Documentation Phase: 8 parallel tasks (T086-T091, T095-T096)
- Docker Phase: 2 parallel tasks (T098-T099)
- Polish Phase: 3 parallel tasks (T106-T108)

**Total Parallelizable Tasks**: 45 out of 121 (37%)

---

## MVP Scope (Recommended First Delivery)

**Goal**: Get local development working with mock data

**Phases**: 1 (Setup), 2 (Foundational), 3 (User Story 1)

**Tasks**: T001-T036 (36 tasks)

**Estimated Time**: ~12-16 hours for single developer

**Deliverable**: Developers can run Bellweaver locally with mock Compass data without credentials

---

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **[Story] label** maps task to specific user story (US1, US2, US3, US4) for traceability
- **Each user story** should be independently completable and testable
- **Commit** after each task or logical group
- **Stop at any checkpoint** to validate story independently
- **MVP-first approach**: Focus on User Story 1 (P1) for fastest time-to-value
- **Avoid**: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Document Metadata

- **Created**: 2025-12-09
- **Feature**: 002-compass-api-decoupling
- **Total Tasks**: 121
- **Estimated MVP Time**: 12-16 hours (Phases 1-3)
- **Estimated Full Implementation**: 40-50 hours (all phases)
- **Related Documents**:
  - [spec.md](./spec.md) - Feature specification
  - [plan.md](./plan.md) - Implementation plan
  - [data-model.md](./data-model.md) - Data model
  - [research.md](./research.md) - Technical research
  - [quickstart.md](./quickstart.md) - Developer quickstart
  - [contracts/](./contracts/) - API contracts
