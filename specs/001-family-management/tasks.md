# Tasks: Family Management System

**Feature**: 001-family-management
**Input**: Design documents from `/specs/001-family-management/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Testing Strategy**:
- **Backend API**: Integration tests written test-first for all API endpoints (constitution principle II)
- **Frontend UI**: Manual testing initially (T092-T098), automated tests deferred to post-MVP
- **Test Location**: backend/tests/integration/test_family_api.py

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create Pydantic models directory at backend/bellweaver/models/family.py
- [x] T002 Verify existing encrypted credential storage is functional at backend/bellweaver/db/credentials.py
- [x] T003 [P] Create test fixtures directory at backend/tests/fixtures/family_data.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add Child ORM model to backend/bellweaver/db/models.py with UUID, name, date_of_birth, gender, interests, timestamps
- [X] T005 Add Organisation ORM model to backend/bellweaver/db/models.py with UUID, name (UNIQUE), type, address, contact_info (JSON), timestamps
- [X] T006 Add ChildOrganisation association table to backend/bellweaver/db/models.py with composite PK (child_id, organisation_id), CASCADE DELETE
- [X] T007 Add CommunicationChannel ORM model to backend/bellweaver/db/models.py with UUID, organisation_id (FK), channel_type, credential_source (FK), config (JSON), is_active, sync status fields, timestamps
- [X] T008 Add SQLAlchemy relationships for Child ↔ Organisation many-to-many in backend/bellweaver/db/models.py
- [X] T009 Add SQLAlchemy relationships for Organisation → CommunicationChannel one-to-many in backend/bellweaver/db/models.py
- [X] T010 Add database initialization code to create new tables in backend/bellweaver/db/database.py
- [X] T011 Create base Pydantic models in backend/bellweaver/models/family.py for ChildBase, OrganisationBase, ChannelBase
- [X] T012 Add validation logic to Pydantic models: date_of_birth not in future, organisation type enum, channel type enum
- [X] T013 [P] Create family_bp blueprint in backend/bellweaver/api/routes.py
- [X] T014 [P] Add error handler classes (ValidationError, ConflictError) in backend/bellweaver/api/routes.py
- [X] T015 [P] Register family_bp blueprint in backend/bellweaver/api/routes.py (registered in register_routes())

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add First Child Profile (Priority: P1) 🎯 MVP

**Goal**: Enable parents to create their first child profile with required information (name, date_of_birth, gender) and optional interests

**Independent Test**: Create a child profile via POST /api/children, verify it's saved and retrievable via GET /api/children/:id, verify it appears in GET /api/children list

### Tests for User Story 1 (Test-First)

- [X] T016 [P] [US1] Write integration test for POST /api/children with valid data in backend/tests/integration/test_family_api.py - expect 201, verify response matches ChildCreate schema, verify SC-001 (<200ms)
- [X] T017 [P] [US1] Write integration test for POST /api/children with missing required fields in backend/tests/integration/test_family_api.py - expect 400 with validation errors
- [X] T018 [P] [US1] Write integration test for POST /api/children with future date_of_birth in backend/tests/integration/test_family_api.py - expect 400 with error message per FR-010b
- [X] T019 [P] [US1] Write integration test for GET /api/children/:id with valid ID in backend/tests/integration/test_family_api.py - expect 200, verify child data returned
- [X] T020 [P] [US1] Write integration test for GET /api/children/:id with invalid ID in backend/tests/integration/test_family_api.py - expect 404
- [X] T021 [P] [US1] Write integration test for GET /api/children in backend/tests/integration/test_family_api.py - expect 200, verify list contains created children, verify SC-005 (<200ms)

### Implementation for User Story 1

- [X] T022 [P] [US1] Create ChildCreate Pydantic model in backend/bellweaver/models/family.py with required fields (name, date_of_birth) and optional fields (gender, interests)
- [X] T023 [P] [US1] Create Child response Pydantic model in backend/bellweaver/models/family.py with id, timestamps, all base fields
- [X] T024 [US1] Implement POST /api/children endpoint in backend/bellweaver/api/routes.py to create child, validate date_of_birth not in future, return 201 with created child - verify tests T016-T018 pass
- [X] T025 [US1] Implement GET /api/children/:id endpoint in backend/bellweaver/api/routes.py to retrieve single child, return 404 if not found - verify tests T019-T020 pass
- [X] T026 [US1] Implement GET /api/children endpoint in backend/bellweaver/api/routes.py to list all children - verify test T021 passes

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Parents can create and view child profiles. All US1 integration tests pass.

---

## Phase 4: User Story 2 - Manage Multiple Children (Priority: P1)

**Goal**: Enable parents to add multiple children, edit existing profiles, and view all children distinctly

**Independent Test**: Create multiple child profiles, edit one child's profile (PUT /api/children/:id), verify only that child's data changed, verify all children appear in list with correct information

### Tests for User Story 2 (Test-First)

- [X] T027 [P] [US2] Write integration test for PUT /api/children/:id with valid data in backend/tests/integration/test_family_api.py - expect 200, verify updated fields only
- [X] T028 [P] [US2] Write integration test for PUT /api/children/:id with invalid ID in backend/tests/integration/test_family_api.py - expect 404
- [X] T029 [P] [US2] Write integration test for PUT /api/children/:id with future date_of_birth in backend/tests/integration/test_family_api.py - expect 400
- [X] T030 [P] [US2] Write integration test for DELETE /api/children/:id in backend/tests/integration/test_family_api.py - expect 204, verify child removed and associations cascade deleted (FR-017)
- [X] T031 [P] [US2] Write integration test for DELETE /api/children/:id with invalid ID in backend/tests/integration/test_family_api.py - expect 404

### Implementation for User Story 2

- [X] T032 [P] [US2] Create ChildUpdate Pydantic model in backend/bellweaver/models/family.py (same fields as ChildCreate)
- [X] T033 [US2] Implement PUT /api/children/:id endpoint in backend/bellweaver/api/routes.py to update child profile, validate date_of_birth not in future, return 404 if child not found - verify tests T027-T029 pass
- [X] T034 [US2] Implement DELETE /api/children/:id endpoint in backend/bellweaver/api/routes.py with CASCADE delete of ChildOrganisation associations, return 204 on success - verify tests T030-T031 pass

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Parents can fully manage multiple child profiles. All US1+US2 integration tests pass.

---

## Phase 5: User Story 3 - Define Organisation (Priority: P2)

**Goal**: Enable parents to create organisation records (school, daycare, sports team) with name, type, and optional details

**Independent Test**: Create an organisation via POST /api/organisations, verify unique name constraint, verify it's retrievable and appears in list with correct type filtering

### Tests for User Story 3 (Test-First)

- [X] T035 [P] [US3] Write integration test for POST /api/organisations with valid data in backend/tests/integration/test_family_api.py - expect 201, verify organisation created
- [X] T036 [P] [US3] Write integration test for POST /api/organisations with duplicate name in backend/tests/integration/test_family_api.py - expect 409 with error per FR-010a
- [X] T037 [P] [US3] Write integration test for POST /api/organisations with invalid type in backend/tests/integration/test_family_api.py - expect 400
- [X] T038 [P] [US3] Write integration test for GET /api/organisations/:id in backend/tests/integration/test_family_api.py - expect 200 with organisation data
- [X] T039 [P] [US3] Write integration test for GET /api/organisations with type filter in backend/tests/integration/test_family_api.py - expect 200, verify filtering works, verify SC-005 (<200ms)

### Implementation for User Story 3

- [X] T040 [P] [US3] Create OrganisationCreate Pydantic model in backend/bellweaver/models/family.py with required (name, type) and optional (address, contact_info) fields
- [X] T041 [P] [US3] Create Organisation response Pydantic model in backend/bellweather/models/family.py with id, timestamps, all base fields
- [X] T042 [US3] Implement POST /api/organisations endpoint in backend/bellweaver/api/routes.py to create organisation, enforce unique name constraint, return 409 if duplicate name - verify tests T035-T037 pass
- [X] T043 [US3] Implement GET /api/organisations/:id endpoint in backend/bellweaver/api/routes.py to retrieve single organisation, return 404 if not found - verify test T038 passes
- [X] T044 [US3] Implement GET /api/organisations endpoint in backend/bellweaver/api/routes.py with optional type filter query parameter - verify test T039 passes

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently. Parents can manage children and organisations separately. All US1+US2+US3 integration tests pass.

---

## Phase 6: User Story 4 - Associate Children with Organisations (Priority: P2)

**Goal**: Enable parents to link children with organisations they attend, supporting multiple organisations per child

**Independent Test**: Create child-organisation associations via POST /api/children/:id/organisations, verify associations appear in GET /api/children/:id/organisations, verify removal via DELETE works correctly

### Tests for User Story 4 (Test-First)

- [X] T045 [P] [US4] Write integration test for POST /api/children/:id/organisations with valid IDs in backend/tests/integration/test_family_api.py - expect 201, verify association created, verify SC-002 (<200ms)
- [X] T046 [P] [US4] Write integration test for POST /api/children/:id/organisations with non-existent child/org in backend/tests/integration/test_family_api.py - expect 404 per edge case spec
- [X] T047 [P] [US4] Write integration test for POST /api/children/:id/organisations with duplicate association in backend/tests/integration/test_family_api.py - expect 409 per edge case spec
- [X] T048 [P] [US4] Write integration test for GET /api/children/:id/organisations in backend/tests/integration/test_family_api.py - expect 200 with organisations list
- [X] T049 [P] [US4] Write integration test for DELETE /api/children/:child_id/organisations/:org_id in backend/tests/integration/test_family_api.py - expect 204, verify association removed
- [X] T050 [P] [US4] Write integration test verifying GET /api/children/:id returns ChildDetail with organisations in backend/tests/integration/test_family_api.py

### Implementation for User Story 4

- [X] T051 [P] [US4] Create ChildDetail Pydantic model in backend/bellweaver/models/family.py with organisations list
- [X] T052 [P] [US4] Create OrganisationDetail Pydantic model in backend/bellweaver/models/family.py with children list
- [X] T053 [US4] Implement POST /api/children/:id/organisations endpoint in backend/bellweaver/api/routes.py to create association, validate both IDs exist, return 409 if already associated - verify tests T045-T047 pass
- [X] T054 [US4] Implement GET /api/children/:id/organisations endpoint in backend/bellweaver/api/routes.py to list child's organisations - verify test T048 passes
- [X] T055 [US4] Implement DELETE /api/children/:child_id/organisations/:org_id endpoint in backend/bellweaver/api/routes.py to remove association, return 404 if association doesn't exist - verify test T049 passes
- [X] T056 [US4] Update GET /api/children/:id endpoint to return ChildDetail with organisations list in backend/bellweaver/api/routes.py - verify test T050 passes
- [X] T057 [US4] Update GET /api/organisations/:id endpoint to return OrganisationDetail with children and channels lists in backend/bellweaver/api/routes.py

**Checkpoint**: At this point, all foundational user stories work together. Parents can create children, organisations, and link them. All US1-US4 integration tests pass.

---

## Phase 7: User Story 5 - Connect Compass Communication Channel (Priority: P2)

**Goal**: Enable parents to configure Compass credentials for an organisation, securely store credentials, and validate authentication

**Independent Test**: Add Compass channel via POST /api/organisations/:id/channels with credentials, verify credentials stored in Credential table encrypted, verify channel appears in GET /api/organisations/:id/channels with credential_source reference

### Tests for User Story 5 (Test-First)

- [ ] T058 [P] [US5] Write integration test for POST /api/organisations/:id/channels with valid Compass credentials in backend/tests/integration/test_family_api.py - expect 201, verify SC-003 (<5s), verify credentials encrypted in DB per SC-004
- [ ] T059 [P] [US5] Write integration test for POST /api/organisations/:id/channels with invalid Compass credentials in backend/tests/integration/test_family_api.py - expect 400 per edge case spec
- [ ] T060 [P] [US5] Write integration test for GET /api/organisations/:id/channels in backend/tests/integration/test_family_api.py - expect 200, verify credentials NOT exposed in response
- [ ] T061 [P] [US5] Write integration test for PUT /api/channels/:id with updated credentials in backend/tests/integration/test_family_api.py - expect 200, verify SC-007 (<5s), verify re-validation per FR-016
- [ ] T062 [P] [US5] Write integration test for DELETE /api/channels/:id in backend/tests/integration/test_family_api.py - expect 204

### Implementation for User Story 5

- [ ] T063 [P] [US5] Create ChannelCreate Pydantic model in backend/bellweaver/models/family.py with channel_type, config, optional credentials (username, password)
- [ ] T064 [P] [US5] Create ChannelUpdate Pydantic model in backend/bellweaver/models/family.py with same fields as ChannelCreate
- [ ] T065 [P] [US5] Create CommunicationChannel response Pydantic model in backend/bellweaver/models/family.py with all fields including credential_source, sync status
- [ ] T066 [US5] Implement POST /api/organisations/:id/channels endpoint in backend/bellweaver/api/routes.py to create channel, validate organisation exists, encrypt and store credentials using existing backend/bellweaver/db/credentials.py - verify tests T058-T059 pass
- [ ] T067 [US5] Add Compass credential validation logic in backend/bellweaver/api/routes.py using existing Compass adapter at backend/bellweaver/adapters/compass.py
- [ ] T068 [US5] Implement GET /api/organisations/:id/channels endpoint in backend/bellweaver/api/routes.py to list channels for organisation (exclude decrypted credentials in response) - verify test T060 passes
- [ ] T069 [US5] Implement GET /api/channels/:id endpoint in backend/bellweaver/api/routes.py to retrieve single channel details (exclude decrypted credentials)
- [ ] T070 [US5] Implement PUT /api/channels/:id endpoint in backend/bellweaver/api/routes.py to update channel config/credentials, re-validate if credentials changed - verify test T061 passes
- [ ] T071 [US5] Implement DELETE /api/channels/:id endpoint in backend/bellweaver/api/routes.py to remove channel, return 204 on success - verify test T062 passes

**Checkpoint**: At this point, complete backend for all P1 and P2 user stories is functional. Parents can manage family structure and Compass channels. All US1-US5 integration tests pass.

---

## Phase 8: User Story 3 (Extended) - Update/Delete Organisations (Priority: P2)

**Goal**: Enable parents to update organisation details and delete organisations (with constraint checking)

**Independent Test**: Update organisation via PUT /api/organisations/:id, attempt to delete organisation with children (should fail with 409), remove all children then delete successfully

### Tests for User Story 3 Extended (Test-First)

- [ ] T072 [P] [US3] Write integration test for PUT /api/organisations/:id with valid data in backend/tests/integration/test_family_api.py - expect 200
- [ ] T073 [P] [US3] Write integration test for PUT /api/organisations/:id with duplicate name in backend/tests/integration/test_family_api.py - expect 409
- [ ] T074 [P] [US3] Write integration test for DELETE /api/organisations/:id with associated children in backend/tests/integration/test_family_api.py - expect 409 per FR-011
- [ ] T075 [P] [US3] Write integration test for DELETE /api/organisations/:id without children in backend/tests/integration/test_family_api.py - expect 204, verify CASCADE delete of channels

### Implementation for User Story 3 Extended

- [ ] T076 [P] [US3] Create OrganisationUpdate Pydantic model in backend/bellweaver/models/family.py (same fields as OrganisationCreate)
- [ ] T077 [US3] Implement PUT /api/organisations/:id endpoint in backend/bellweaver/api/routes.py to update organisation, enforce unique name on update, return 409 if duplicate - verify tests T072-T073 pass
- [ ] T078 [US3] Implement DELETE /api/organisations/:id endpoint in backend/bellweaver/api/routes.py with check for associated children, return 409 if children exist, CASCADE delete channels if no children - verify tests T074-T075 pass

**Checkpoint**: Organisation management is now fully complete with all CRUD operations and business rule enforcement. All API integration tests pass for US1-US5 + US3 extended.

---

## Phase 9: User Story 6 - View Channel Configuration Status (Priority: P3)

**Goal**: Provide visibility into which organisations have channels configured and their sync status

**Independent Test**: Verify GET /api/organisations/:id returns channels list with last_sync_status and last_sync_at fields, verify organisations without channels show empty channels array

### Implementation for User Story 6

- [ ] T052 [US6] Verify OrganisationDetail model includes channels list (already implemented in T033)
- [ ] T053 [US6] Ensure GET /api/organisations/:id endpoint returns full channel details including sync status (already implemented in T038, verify it includes last_sync_at, last_sync_status, is_active)
- [ ] T054 [US6] Add helper method in backend/bellweaver/api/routes.py to determine if organisation needs channel setup (has no active channels)

**Checkpoint**: Backend API for all 6 user stories (P1, P2, P3) is now complete. All endpoints functional with proper validation and error handling.

---

## Phase 10: Frontend - User Story 1 & 2 (Child Management UI)

**Goal**: Build React UI for creating, viewing, editing, and deleting child profiles

**Independent Test**: Use frontend to create multiple children, edit a child, delete a child, verify all operations call correct API endpoints and display results

### Implementation

- [X] T055 [P] [US1] Create API service functions for children in frontend/src/services/familyApi.js (createChild, getChildren, getChild, updateChild, deleteChild)
- [X] T056 [P] [US1] Create ChildList component in frontend/src/components/family/ChildList.jsx to display all children with edit/delete buttons
- [X] T057 [P] [US2] Create ChildForm component in frontend/src/components/family/ChildForm.jsx for create/edit with validation (required fields, date picker, gender field, interests textarea)
- [X] T058 [US1] Integrate ChildList and ChildForm into FamilyManagement page at frontend/src/pages/FamilyManagement.jsx
- [X] T059 [US2] Add confirmation dialog for child deletion in ChildList component
- [X] T060 [US1] Add error handling and toast notifications for API errors in frontend components

**Checkpoint**: Frontend for child management (US1, US2) is complete. Parents can manage children via UI.

---

## Phase 11: Frontend - User Story 3 (Organisation Management UI)

**Goal**: Build React UI for creating, viewing, editing, and deleting organisations

**Independent Test**: Use frontend to create organisations, verify unique name validation, filter by type, edit organisation, attempt to delete organisation with children (should show error)

### Implementation

- [ ] T061 [P] [US3] Create API service functions for organisations in frontend/src/services/familyApi.js (createOrganisation, getOrganisations, getOrganisation, updateOrganisation, deleteOrganisation)
- [ ] T062 [P] [US3] Create OrganisationList component in frontend/src/components/family/OrganisationList.jsx with type filter dropdown, edit/delete buttons
- [ ] T063 [P] [US3] Create OrganisationForm component in frontend/src/components/family/OrganisationForm.jsx with name, type dropdown, optional address, contact_info fields (phone, email, website)
- [ ] T064 [US3] Integrate OrganisationList and OrganisationForm into FamilyManagement page at frontend/src/pages/FamilyManagement.jsx
- [ ] T065 [US3] Add validation error display for duplicate organisation names (409 conflict)
- [ ] T066 [US3] Add confirmation dialog for organisation deletion with error handling for organisations with children

**Checkpoint**: Frontend for organisation management (US3) is complete. Parents can manage organisations via UI.

---

## Phase 12: Frontend - User Story 4 (Child-Organisation Associations UI)

**Goal**: Build React UI for associating children with organisations and viewing associations

**Independent Test**: Use frontend to assign a child to multiple organisations, view child's organisations, view organisation's children, remove association

### Implementation

- [ ] T067 [P] [US4] Create API service functions for associations in frontend/src/services/familyApi.js (addChildOrganisation, getChildOrganisations, removeChildOrganisation)
- [ ] T068 [US4] Add organisation selector to ChildForm component in frontend/src/components/family/ChildForm.jsx to display and manage child's organisations
- [ ] T069 [US4] Add children list display to OrganisationForm component showing which children attend this organisation
- [ ] T070 [US4] Add "Add Association" UI flow (dropdown to select organisation from child view, add button, remove button)
- [ ] T071 [US4] Update ChildList to show organisation badges/tags for each child

**Checkpoint**: Frontend for child-organisation associations (US4) is complete. Parents can link children to organisations via UI.

---

## Phase 13: Frontend - User Story 5 & 6 (Channel Configuration UI)

**Goal**: Build React UI for configuring Compass channels and viewing sync status

**Independent Test**: Use frontend to add Compass credentials for an organisation, view channel status, edit credentials, verify validation feedback for invalid credentials

### Implementation

- [ ] T072 [P] [US5] Create API service functions for channels in frontend/src/services/familyApi.js (createChannel, getOrganisationChannels, getChannel, updateChannel, deleteChannel)
- [ ] T073 [P] [US5] Create ChannelConfig component in frontend/src/components/family/ChannelConfig.jsx with channel type dropdown, Compass credential inputs (username, password, base_url), is_active toggle
- [ ] T074 [US5] Add channel configuration section to OrganisationForm component showing existing channels with edit/delete buttons
- [ ] T075 [US6] Add channel status indicators (success/failed/pending badges) with last_sync_at timestamp display in ChannelConfig component
- [ ] T076 [US5] Add credential validation feedback (show success/error after API validates Compass credentials)
- [ ] T077 [US6] Add "Needs Setup" indicator for organisations without active channels in OrganisationList

**Checkpoint**: Frontend for channel configuration (US5, US6) is complete. All user stories have functional UI.

---

## Phase 14: Frontend - State Management & Integration

**Goal**: Implement React Context for centralized family data management and integrate all components

**Independent Test**: Verify all components use FamilyContext, data refreshes after mutations, no prop drilling, consistent error handling

### Implementation

- [ ] T078 Create FamilyContext provider in frontend/src/contexts/FamilyContext.jsx with state for children, organisations, channels
- [ ] T079 Add CRUD operations to FamilyContext using familyApi service functions
- [ ] T080 Wrap FamilyManagement page with FamilyProvider in frontend/src/App.jsx or FamilyManagement.jsx
- [ ] T081 Update all family components to use FamilyContext instead of direct API calls
- [ ] T082 Add loading states and error states to FamilyContext
- [ ] T083 Implement optimistic updates for better UX (update UI before API response, rollback on error)

**Checkpoint**: Frontend state management is complete. All components integrated with centralized state.

---

## Phase 15: Frontend - Styling & UX Polish

**Goal**: Apply consistent styling, responsive design, and UX improvements

**Independent Test**: View family management on mobile/tablet/desktop, verify forms are usable, verify error messages are clear, verify loading states work

### Implementation

- [ ] T084 [P] Add CSS styling for ChildList and ChildForm components in frontend/src/components/family/
- [ ] T085 [P] Add CSS styling for OrganisationList and OrganisationForm components in frontend/src/components/family/
- [ ] T086 [P] Add CSS styling for ChannelConfig component in frontend/src/components/family/
- [ ] T087 Implement responsive layout for FamilyManagement page (grid/flex layout for desktop, stack for mobile)
- [ ] T088 Add loading spinners/skeletons for API calls
- [ ] T089 Add toast notification system for success/error messages
- [ ] T090 Add form validation UI feedback (inline errors, required field indicators)
- [ ] T091 Test accessibility (keyboard navigation, screen reader labels, ARIA attributes)

**Checkpoint**: Frontend UI is polished, responsive, and accessible. Ready for user testing.

---

## Phase 16: Integration Testing & Documentation

**Goal**: Validate end-to-end workflows and update documentation

**Independent Test**: Run through all user stories end-to-end using both API and UI, verify quickstart.md scenarios work, verify CLAUDE.md is updated

### Implementation

- [ ] T092 [P] Manually test User Story 1 acceptance scenarios from spec.md using frontend UI
- [ ] T093 [P] Manually test User Story 2 acceptance scenarios from spec.md using frontend UI
- [ ] T094 [P] Manually test User Story 3 acceptance scenarios from spec.md using frontend UI
- [ ] T095 [P] Manually test User Story 4 acceptance scenarios from spec.md using frontend UI
- [ ] T096 [P] Manually test User Story 5 acceptance scenarios from spec.md using frontend UI
- [ ] T097 [P] Manually test User Story 6 acceptance scenarios from spec.md using frontend UI
- [ ] T098 Test edge cases from spec.md (duplicate org names, future dates, delete org with children, etc.)
- [ ] T099 Run backend test suite with poetry run pytest to ensure existing tests pass
- [ ] T100 Update CLAUDE.md with new models, endpoints, and frontend components added
- [ ] T101 [P] Verify Docker build and deployment still works with new changes
- [ ] T102 [P] Test database migration from scratch (create new DB, verify all tables created correctly)

**Checkpoint**: Feature fully tested and documented. Ready for PR creation.

---

## Phase 17: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements that affect multiple user stories

- [ ] T103 [P] Review all API error responses for consistency (400, 404, 409 status codes with proper error format)
- [ ] T104 Add database indexes for performance (child.created_at, organisation.type, organisation.name, communication_channels.organisation_id)
- [ ] T105 Review and optimize SQLAlchemy queries (use joins where needed, avoid N+1 queries)
- [ ] T106 [P] Add API request logging for family endpoints in backend/bellweaver/api/routes.py
- [ ] T107 Security review: verify credentials never exposed in API responses, verify CSRF protection if needed
- [ ] T108 Performance testing: verify system handles 10 children, 20 organisations without degradation (per success criteria SC-006)
- [ ] T109 Run full test suite and build: poetry run pytest --cov && npm run build

**Checkpoint**: Feature complete, polished, and ready for production. All success criteria met.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **Backend User Stories (Phases 3-9)**: All depend on Foundational phase completion
  - US1 (Phase 3): Can start immediately after Foundational
  - US2 (Phase 4): Extends US1, can run in parallel or immediately after US1
  - US3 (Phase 5): Independent, can run in parallel with US1/US2
  - US4 (Phase 6): Depends on US1 and US3 (needs children and organisations)
  - US5 (Phase 7): Depends on US3 (needs organisations)
  - US3 Extended (Phase 8): Depends on US3 and US4 (needs organisations and associations for delete constraint)
  - US6 (Phase 9): Depends on US5 (needs channels)
- **Frontend Phases (10-15)**: Depend on corresponding backend phases
  - Phase 10 (Child UI): Depends on Phase 4 (US1+US2 backend complete)
  - Phase 11 (Org UI): Depends on Phase 8 (US3 backend complete)
  - Phase 12 (Association UI): Depends on Phase 6 (US4 backend complete)
  - Phase 13 (Channel UI): Depends on Phases 7 & 9 (US5+US6 backend complete)
  - Phase 14 (State Management): Depends on Phases 10-13 (all components exist)
  - Phase 15 (Styling): Depends on Phase 14 (all components integrated)
- **Integration & Polish (Phases 16-17)**: Depend on all implementation phases

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Extends US1 - Adds edit/delete to child management
- **User Story 3 (P2)**: Independent - Can run in parallel with US1/US2
- **User Story 4 (P2)**: Requires US1 (children) and US3 (organisations) exist
- **User Story 5 (P2)**: Requires US3 (organisations) exist
- **User Story 6 (P3)**: Requires US5 (channels) exist

### Parallel Opportunities

**Backend**:
- Phase 2: Tasks T004-T007 (ORM models) can run in parallel
- Phase 2: Tasks T011-T015 (Pydantic models, blueprint setup) can run in parallel
- Phase 3-5: US1, US2, US3 can run in parallel (different entities)
- Within each phase: [P] marked tasks can run in parallel

**Frontend**:
- Phase 10-13: Component development can run in parallel if backend is ready
- Within each phase: [P] marked tasks (API services, components) can run in parallel
- Phase 16: All manual testing tasks (T092-T098, T101-T102) can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# Launch all ORM models together:
Task T004: "Add Child ORM model"
Task T005: "Add Organisation ORM model"
Task T006: "Add ChildOrganisation table"
Task T007: "Add CommunicationChannel ORM model"

# Then launch validation and setup together:
Task T011: "Create base Pydantic models"
Task T013: "Create family_bp blueprint"
Task T014: "Add error handlers"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only - Child Management)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1 (Create first child)
4. Complete Phase 4: User Story 2 (Manage multiple children)
5. Complete Phase 10: Frontend for Child Management
6. **STOP and VALIDATE**: Test child management end-to-end
7. Deploy/demo if ready - parents can now manage children!

### Incremental Delivery

1. **MVP**: Setup + Foundational + US1 + US2 + Child UI → Child management working
2. **Increment 2**: Add US3 + US3 Extended + Org UI → Organisation management working
3. **Increment 3**: Add US4 + Association UI → Link children to organisations
4. **Increment 4**: Add US5 + US6 + Channel UI → Compass integration working
5. **Polish**: State management, styling, testing, documentation

Each increment delivers testable value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers (after Foundational phase complete):

- **Developer A**: Backend US1+US2 (Child management) → Frontend Child UI
- **Developer B**: Backend US3+US3Ext (Organisation management) → Frontend Org UI
- **Developer C**: Backend US5+US6 (Channels) → Frontend Channel UI
- **Developer D**: Backend US4 (Associations) → Frontend Association UI → State Management

Stories can complete independently and integrate at the end.

---

## Summary

**Total Tasks**: 140+ (updated with API integration tests)
- Phase 1 (Setup): 3 tasks
- Phase 2 (Foundational): 12 tasks (BLOCKING)
- Phase 3 (US1): 6 tests + 5 implementation = 11 tasks
- Phase 4 (US2): 5 tests + 3 implementation = 8 tasks
- Phase 5 (US3): 5 tests + 5 implementation = 10 tasks
- Phase 6 (US4): 6 tests + 7 implementation = 13 tasks
- Phase 7 (US5): 5 tests + 9 implementation = 14 tasks
- Phase 8 (US3 Extended): 4 tests + 3 implementation = 7 tasks
- Phase 9 (US6): 3 tasks (view-only, minimal testing)
- Phase 10-17 (Frontend): ~70 tasks (manual testing only, per strategy)

**Test-First Compliance**: 31 API integration tests written before implementation (constitution principle II satisfied)

**Parallel Opportunities**: 50+ tasks marked [P] can run in parallel within their phase

**MVP Scope**: Phases 1-4 = Child management (15 backend + 11 tests + 3 setup + 12 foundational = 41 tasks)

**Full Backend API**: Phases 1-9 = All API endpoints with comprehensive integration tests

**Full Feature**: All phases = Complete family management system with all 6 user stories

---

## Notes

- All tasks follow strict checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
- [P] = Parallelizable (different files, no dependencies within phase)
- [Story] label (US1-US6) maps task to specific user story for traceability
- Each phase builds on previous phases
- **Test-First Workflow**: API integration tests MUST be written before implementation (constitution principle II)
  - Tests verify API contracts, status codes, validation rules, edge cases, and success criteria
  - Implementation tasks reference which tests they must pass (e.g., "verify tests T016-T018 pass")
  - All tests in backend/tests/integration/test_family_api.py
- **Frontend Testing**: Manual testing via UI (T092-T098), automated frontend tests deferred to post-MVP
- Backend phases (3-9) should complete before corresponding frontend phases
- Foundational phase (Phase 2) must complete before ANY user story work
- Stop at any phase checkpoint to validate independently
- Each user story delivers independent value
