# Quickstart Guide: Family Management System

**Feature**: 001-family-management
**Date**: 2025-12-09

This guide provides a quick reference for developers implementing the Family Management System.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                      React Frontend                           │
│  ┌────────────────┐  ┌─────────────────┐  ┌───────────────┐ │
│  │ ChildForm.jsx  │  │ OrgForm.jsx     │  │ ChannelCfg... │ │
│  └────────┬───────┘  └────────┬────────┘  └───────┬───────┘ │
│           └──────────┬─────────┘                   │          │
│                      ▼                             ▼          │
│            ┌──────────────────┐         ┌──────────────────┐ │
│            │  familyApi.js    │         │    api.js        │ │
│            └────────┬─────────┘         └────────┬─────────┘ │
└─────────────────────┼──────────────────────────┼─────────────┘
                      │                          │
                      │  HTTP REST API           │
                      ▼                          ▼
┌──────────────────────────────────────────────────────────────┐
│                    Flask Backend                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │           api/routes.py (family_bp blueprint)            ││
│  │  /children, /organisations, /channels, /associations     ││
│  └────────┬─────────────────────────────────────────────────┘│
│           │                                                    │
│           ▼                                                    │
│  ┌────────────────────────┐     ┌─────────────────────────┐  │
│  │ models/family.py       │     │  db/models.py          │  │
│  │ (Pydantic validation)  │────▶│  (SQLAlchemy ORM)      │  │
│  └────────────────────────┘     └──────────┬──────────────┘  │
│                                             │                 │
│                                             ▼                 │
│                                  ┌──────────────────────┐    │
│                                  │  db/credentials.py   │    │
│                                  │  (Fernet encryption) │    │
│                                  └──────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                          ┌──────────────────┐
                          │  SQLite Database │
                          │  bellweaver.db   │
                          └──────────────────┘
```

---

## Database Schema Quick Reference

### Tables

1. **children**: Child profiles
   - Primary key: `id` (UUID)
   - Required: `name`, `date_of_birth`
   - Optional: `gender`, `interests`

2. **organisations**: Schools, daycares, sports teams
   - Primary key: `id` (UUID)
   - Required: `name` (UNIQUE), `type`
   - Optional: `address`, `contact_info` (JSON)

3. **child_organisations**: Many-to-many association
   - Composite primary key: `(child_id, organisation_id)`
   - Both columns are foreign keys with CASCADE DELETE

4. **communication_channels**: Channel configs (Compass, etc.)
   - Primary key: `id` (UUID)
   - Required: `organisation_id`, `channel_type`
   - Optional: `credential_source` (FK to credentials), `config` (JSON)
   - Foreign key: `organisation_id` → `organisations.id` (CASCADE DELETE)

5. **credentials**: Encrypted credentials (EXISTING)
   - Primary key: `source`
   - Stores encrypted passwords using Fernet

### Relationships

```
Child (1) ←→ (N) ChildOrganisation (N) ←→ (1) Organisation
                                                    ↓ (1:N)
                                          CommunicationChannel
                                                    ↓ (N:1)
                                                Credential
```

---

## API Endpoints Quick Reference

### Children
- `GET /api/children` - List all children
- `POST /api/children` - Create child
- `GET /api/children/:id` - Get child (with organisations)
- `PUT /api/children/:id` - Update child
- `DELETE /api/children/:id` - Delete child

### Organisations
- `GET /api/organisations` - List all organisations (optional `?type=school` filter)
- `POST /api/organisations` - Create organisation
- `GET /api/organisations/:id` - Get organisation (with children and channels)
- `PUT /api/organisations/:id` - Update organisation
- `DELETE /api/organisations/:id` - Delete organisation (fails if has children)

### Associations
- `GET /api/children/:id/organisations` - List child's organisations
- `POST /api/children/:id/organisations` - Associate child with org (body: `{organisation_id}`)
- `DELETE /api/children/:child_id/organisations/:org_id` - Remove association

### Channels
- `GET /api/organisations/:id/channels` - List org's channels
- `POST /api/organisations/:id/channels` - Add channel (body includes credentials if needed)
- `GET /api/channels/:id` - Get channel details
- `PUT /api/channels/:id` - Update channel config/credentials
- `DELETE /api/channels/:id` - Delete channel

---

## Implementation Checklist

### Backend Tasks

#### Database Layer (`backend/bellweaver/db/models.py`)
- [ ] Add `Child` ORM model
- [ ] Add `Organisation` ORM model
- [ ] Add `ChildOrganisation` association table
- [ ] Add `CommunicationChannel` ORM model
- [ ] Set up relationships (many-to-many for Child ↔ Organisation)
- [ ] Add database migration/initialization in `database.py`

#### Validation Layer (`backend/bellweaver/models/family.py`)
- [ ] Add `ChildCreate`, `ChildUpdate` Pydantic models
- [ ] Add `OrganisationCreate`, `OrganisationUpdate` Pydantic models
- [ ] Add `ChannelCreate`, `ChannelUpdate` Pydantic models
- [ ] Add validators (date_of_birth not in future, etc.)

#### API Layer (`backend/bellweaver/api/routes.py`)
- [ ] Create `family_bp` blueprint
- [ ] Implement child CRUD endpoints
- [ ] Implement organisation CRUD endpoints
- [ ] Implement association endpoints
- [ ] Implement channel CRUD endpoints
- [ ] Add business logic validation (unique org names, deletion conflicts)
- [ ] Add error handlers (ValidationError, ConflictError)
- [ ] Register blueprint in `__init__.py`

#### Testing (`backend/tests/`)
- [ ] Unit tests for Pydantic models (`test_family_models.py`)
- [ ] Unit tests for ORM models (`test_db_models.py` - extend existing)
- [ ] Integration tests for API endpoints (`test_family_api.py`)
- [ ] Test fixtures for family data (`fixtures/family_data.py`)

### Frontend Tasks

#### API Service Layer (`frontend/src/services/`)
- [ ] Create `familyApi.js` with API client functions
- [ ] Extend `api.js` with family endpoints

#### Components (`frontend/src/components/family/`)
- [ ] `ChildList.jsx` - Display list of children
- [ ] `ChildForm.jsx` - Create/edit child profile
- [ ] `OrganisationList.jsx` - Display list of organisations
- [ ] `OrganisationForm.jsx` - Create/edit organisation
- [ ] `ChannelConfig.jsx` - Configure communication channels

#### Pages (`frontend/src/pages/`)
- [ ] `FamilyManagement.jsx` - Main family management page

#### State Management
- [ ] Create `FamilyContext.jsx` (React Context for family data)
- [ ] Implement CRUD operations in context

#### Testing (`frontend/tests/components/family/`)
- [ ] Component tests for each family component

---

## Key Design Decisions

### 1. Many-to-Many Relationship
- **Pattern**: Explicit `ChildOrganisation` association table
- **Rationale**: Allows future metadata (enrollment_date, etc.) without migration
- **Cascade**: DELETE child → removes associations; DELETE org → blocked if has children

### 2. Channel Configuration
- **Pattern**: Polymorphic single table with `channel_type` + JSON `config`
- **Rationale**: Flexible for multiple channel types without schema migrations
- **Security**: Credentials stored in separate encrypted `Credential` table

### 3. Validation Strategy
- **Multi-layer**: Pydantic (format) → API (business rules) → Database (constraints)
- **Example**: Date validation in Pydantic, unique name check in API, unique constraint in DB

### 4. State Management
- **Pattern**: React Context API, no Redux
- **Rationale**: Simple CRUD operations don't need heavy state management (Constitution V)

### 5. Error Handling
- **HTTP Status Codes**:
  - `400` - Validation errors (future date, missing fields)
  - `404` - Resource not found
  - `409` - Conflicts (duplicate name, org has children)
  - `500` - Internal errors
- **Response Format**: `{error, message, code}` for structured errors

---

## Example Requests

### Create a Child

```bash
curl -X POST http://localhost:5000/api/children \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Emma Johnson",
    "date_of_birth": "2015-06-15",
    "gender": "female",
    "interests": "Soccer, reading"
  }'
```

### Create an Organisation

```bash
curl -X POST http://localhost:5000/api/organisations \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Springfield Elementary",
    "type": "school",
    "address": "123 Main St",
    "contact_info": {
      "phone": "+61 3 9876 5432",
      "email": "admin@springfield.edu.au"
    }
  }'
```

### Associate Child with Organisation

```bash
curl -X POST http://localhost:5000/api/children/{child_id}/organisations \
  -H "Content-Type: application/json" \
  -d '{
    "organisation_id": "{org_id}"
  }'
```

### Add Compass Channel

```bash
curl -X POST http://localhost:5000/api/organisations/{org_id}/channels \
  -H "Content-Type: application/json" \
  -d '{
    "channel_type": "compass",
    "config": {
      "base_url": "https://springfield.compass.education"
    },
    "credentials": {
      "username": "parent@example.com",
      "password": "password123"
    }
  }'
```

---

## Development Workflow

### 1. Setup

```bash
# Backend
cd backend
poetry install
poetry run pytest  # Ensure existing tests pass

# Frontend
cd frontend
npm install
```

### 2. Development Process (Per Constitution)

1. **Write tests first** (test-first development)
   - Write unit tests for models
   - Write integration tests for API endpoints
   - Verify tests FAIL (RED)

2. **Implement feature**
   - Backend: ORM models → Pydantic models → API routes
   - Frontend: API service → Components → Pages
   - Verify tests PASS (GREEN)

3. **Refactor** (if needed)
   - Keep it simple (Constitution V)
   - No premature abstractions

4. **Commit incrementally**
   - Commit as you complete each component
   - Format: `<component>: <description>`
   - Example: `db: add Child and Organisation ORM models`

### 3. Testing

```bash
# Backend tests
cd backend
poetry run pytest                     # All tests
poetry run pytest tests/unit/         # Unit tests only
poetry run pytest tests/integration/  # Integration tests only
poetry run pytest --cov               # With coverage

# Frontend tests
cd frontend
npm test
```

### 4. Running the Application

```bash
# Backend API
cd backend
poetry run bellweaver api serve --debug

# Frontend dev server
cd frontend
npm run dev

# Access at:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:5000/api
```

---

## Common Pitfalls

### ❌ Don't Do This
1. Skip tests - Constitution II requires test-first
2. Store credentials in `config` JSON - Use `Credential` table
3. Allow organisation deletion with children - Return 409 Conflict
4. Use implicit many-to-many (secondary parameter) - Use explicit table
5. Add premature abstractions - Keep it simple (Constitution V)

### ✅ Do This
1. Write tests before implementation
2. Use existing `credentials.py` for encryption
3. Check business rules in API layer before DB operations
4. Use explicit `ChildOrganisation` table
5. Use direct SQLAlchemy queries (no repository pattern needed yet)

---

## File Paths Reference

### Backend
- ORM Models: `backend/bellweaver/db/models.py`
- Pydantic Models: `backend/bellweaver/models/family.py` (NEW)
- API Routes: `backend/bellweaver/api/routes.py`
- Credentials: `backend/bellweaver/db/credentials.py` (EXISTING)
- Tests: `backend/tests/`

### Frontend
- Components: `frontend/src/components/family/`
- API Service: `frontend/src/services/familyApi.js` (NEW)
- Pages: `frontend/src/pages/FamilyManagement.jsx` (NEW)
- Tests: `frontend/tests/components/family/`

### Documentation
- Spec: `specs/001-family-management/spec.md`
- Plan: `specs/001-family-management/plan.md`
- Research: `specs/001-family-management/research.md`
- Data Model: `specs/001-family-management/data-model.md`
- API Contract: `specs/001-family-management/contracts/openapi.yaml`
- This file: `specs/001-family-management/quickstart.md`

---

## Next Steps

After planning is complete (`/speckit.plan`):

1. Run `/speckit.tasks` to generate `tasks.md` with dependency-ordered implementation tasks
2. Review tasks with user for approval
3. Begin implementation following test-first workflow
4. Run tests and build before creating PR
5. Create PR using `gh pr create`

---

## Questions?

- See `research.md` for design decisions and rationale
- See `data-model.md` for detailed entity definitions
- See `contracts/openapi.yaml` for complete API specification
- See Constitution (`.specify/memory/constitution.md`) for architectural principles
- See `CLAUDE.md` for project context and workflow
