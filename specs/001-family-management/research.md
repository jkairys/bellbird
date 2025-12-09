# Research: Family Management System

**Date**: 2025-12-09
**Feature**: 001-family-management

## Research Questions

This document consolidates research findings that inform the design decisions for the Family Management System.

---

## 1. Database Schema Design for Many-to-Many Relationships

**Question**: What is the best practice for implementing the Child-Organisation many-to-many relationship in SQLAlchemy 2.0?

**Decision**: Use explicit association table with SQLAlchemy `relationship()` on both sides

**Rationale**:
- SQLAlchemy 2.0 supports both explicit association tables and implicit many-to-many via `secondary` parameter
- Explicit association table provides:
  - Ability to add metadata later (e.g., enrollment_date, graduation_date) without schema migration
  - Clear foreign key constraints
  - Better query performance for complex filters
  - Explicit control over cascade behavior
- Pattern already established in project with `Batch` → `ApiPayload` relationship

**Implementation Pattern**:
```python
class ChildOrganisation(Base):
    __tablename__ = "child_organisations"
    child_id = Column(String(36), ForeignKey("children.id"), primary_key=True)
    organisation_id = Column(String(36), ForeignKey("organisations.id"), primary_key=True)
    # Future: enrollment_date, status, etc.

class Child(Base):
    organisations = relationship("Organisation", secondary="child_organisations", back_populates="children")

class Organisation(Base):
    children = relationship("Child", secondary="child_organisations", back_populates="organisations")
```

**Alternatives Considered**:
- Implicit `secondary` parameter: Rejected because it doesn't allow future metadata additions without migration
- Separate service layer: Rejected per Constitution V (Simplicity & Pragmatism) - YAGNI

**References**:
- SQLAlchemy 2.0 docs: https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#many-to-many
- Existing project pattern: `backend/bellweaver/db/models.py` (Batch/ApiPayload)

---

## 2. Communication Channel Data Model Design

**Question**: How should we model communication channels to support multiple channel types (Compass, future: HubHello, ClassDojo, etc.) with different credential requirements?

**Decision**: Single `CommunicationChannel` table with polymorphic `channel_type` and JSON `config` field

**Rationale**:
- Initially only Compass supported, but spec indicates future multi-channel support
- Polymorphic approach avoids:
  - Multiple tables per channel type (CompassChannel, HubHelloChannel, etc.)
  - Complex joins and queries
  - Schema migrations for each new channel type
- JSON config field allows flexible per-channel configuration
- Existing project already uses JSON columns (`ApiPayload.payload`, `Batch.parameters`)
- Credentials still stored in existing `Credential` table using `source` as key

**Implementation Pattern**:
```python
class CommunicationChannel(Base):
    __tablename__ = "communication_channels"
    id = Column(String(36), primary_key=True)
    organisation_id = Column(String(36), ForeignKey("organisations.id"))
    channel_type = Column(String(50), nullable=False)  # "compass", "hubhello", "classdojo"
    credential_source = Column(String(50), ForeignKey("credentials.source"))  # Links to Credential table
    config = Column(JSON, nullable=True)  # Channel-specific config (e.g., base_url for Compass)
    is_active = Column(Boolean, default=True)
```

**Alternatives Considered**:
- Separate table per channel type: Rejected due to complexity, violates Constitution V (Simplicity)
- Joined table inheritance: Rejected as premature abstraction, only 1 channel type initially
- Store credentials in JSON config: Rejected, violates Constitution III (Secure by Default)

**References**:
- Existing credential storage: `backend/bellweaver/db/credentials.py`
- Constitution principle III: Secure by Default
- Constitution principle V: Simplicity & Pragmatism

---

## 3. Frontend State Management Approach

**Question**: What state management pattern should be used for family data in the React frontend?

**Decision**: React Context API with local component state, no Redux/MobX

**Rationale**:
- Family data is relatively simple: lists of children, organisations, channels
- CRUD operations are straightforward and independent
- Constitution V (Simplicity & Pragmatism) discourages abstractions for single use cases
- React Context sufficient for:
  - Sharing family data across components
  - Avoiding prop drilling
  - Centralized API calls
- Project already uses simple patterns (no existing state management library)

**Implementation Pattern**:
```javascript
// contexts/FamilyContext.jsx
const FamilyContext = createContext();

export function FamilyProvider({ children }) {
  const [children, setChildren] = useState([]);
  const [organisations, setOrganisations] = useState([]);
  const [loading, setLoading] = useState(false);

  // API calls and state updates

  return (
    <FamilyContext.Provider value={{ children, organisations, loading, ... }}>
      {children}
    </FamilyContext.Provider>
  );
}
```

**Alternatives Considered**:
- Redux: Rejected as over-engineering for simple CRUD operations
- MobX: Rejected as unnecessary dependency
- Direct API calls in components: Rejected due to code duplication and inconsistent state

**References**:
- React Context docs: https://react.dev/reference/react/useContext
- Constitution principle V: Simplicity & Pragmatism (no prohibited complexity)

---

## 4. API Design Pattern for Family Management

**Question**: Should family management endpoints follow RESTful resource-based design or action-based design?

**Decision**: RESTful resource-based design with standard HTTP verbs

**Rationale**:
- Existing project uses RESTful patterns (`GET /user`, `GET /events`)
- Standard REST verbs map naturally to CRUD operations:
  - `POST /children` - Create child
  - `GET /children` - List all children
  - `GET /children/:id` - Get single child
  - `PUT /children/:id` - Update child
  - `DELETE /children/:id` - Delete child
  - Similar for `/organisations`, `/channels`
- Association endpoint: `POST /children/:id/organisations` with `organisation_id` in body
- Consistent with Constitution V (Simplicity) - use standard patterns

**Endpoint Structure**:
```
POST   /api/children                    - Create child
GET    /api/children                    - List all children
GET    /api/children/:id                - Get child details
PUT    /api/children/:id                - Update child
DELETE /api/children/:id                - Delete child

POST   /api/children/:id/organisations  - Associate child with organisation
DELETE /api/children/:child_id/organisations/:org_id  - Remove association

POST   /api/organisations               - Create organisation
GET    /api/organisations               - List all organisations
GET    /api/organisations/:id           - Get organisation details
PUT    /api/organisations/:id           - Update organisation
DELETE /api/organisations/:id           - Delete organisation

POST   /api/organisations/:id/channels  - Add communication channel
GET    /api/organisations/:id/channels  - List channels for organisation
PUT    /api/channels/:id                - Update channel config
DELETE /api/channels/:id                - Delete channel
```

**Alternatives Considered**:
- Action-based: `POST /api/associate-child-organisation` - Rejected as non-standard, harder to document
- GraphQL: Rejected as premature, violates Constitution V (don't add features for future flexibility)

**References**:
- REST API best practices: https://restfulapi.net/resource-naming/
- Existing API patterns: `backend/bellweaver/api/routes.py`

---

## 5. Validation Strategy for Business Rules

**Question**: Where should business rule validation be implemented (unique organisation names, future date validation, etc.)?

**Decision**: Multi-layer validation: Pydantic models (format), API layer (business rules), Database (constraints)

**Rationale**:
- Defense in depth approach:
  - **Pydantic layer**: Type validation, format validation (e.g., date format)
  - **API layer**: Business logic validation (e.g., check if organisation name exists, date not in future)
  - **Database layer**: Integrity constraints (e.g., unique constraints, foreign keys)
- Aligns with Constitution I (Separation of Concerns)
- Provides clear error messages at each layer
- Database constraints prevent race conditions

**Implementation Pattern**:
```python
# Pydantic model (format validation)
class ChildCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    date_of_birth: date
    gender: Optional[str] = None

# API layer (business logic validation)
@app.route('/children', methods=['POST'])
def create_child():
    data = ChildCreate(**request.json)  # Pydantic validation

    # Business rule: date of birth not in future
    if data.date_of_birth > date.today():
        return jsonify({"error": "Date of birth cannot be in the future"}), 400

    # Database operation
    child = Child(**data.dict())
    db.session.add(child)
    db.session.commit()

# Database layer (integrity constraints)
class Organisation(Base):
    __tablename__ = "organisations"
    __table_args__ = (UniqueConstraint('name', name='uix_organisation_name'),)
```

**Alternatives Considered**:
- Validation only in frontend: Rejected, violates secure by default principle
- Validation only in database: Rejected, provides poor error messages
- Custom validator service: Rejected as premature abstraction (Constitution V)

**References**:
- Pydantic validation: https://docs.pydantic.dev/latest/concepts/validators/
- Existing validation patterns: `backend/bellweaver/parsers/compass.py`

---

## 6. Error Handling and User Feedback

**Question**: How should deletion conflicts and validation errors be communicated to users?

**Decision**: HTTP status codes with structured JSON error responses, frontend toast notifications

**Rationale**:
- Standard HTTP status codes:
  - `400 Bad Request`: Validation errors (future date, empty name)
  - `409 Conflict`: Business rule violations (organisation has children, duplicate name)
  - `404 Not Found`: Resource doesn't exist
  - `500 Internal Server Error`: Unexpected errors
- JSON error response format:
  ```json
  {
    "error": "Cannot delete organisation",
    "message": "Organisation 'Springfield Elementary' has 2 children associated. Remove all associations first.",
    "code": "ORGANISATION_HAS_CHILDREN"
  }
  ```
- Frontend: Toast/notification component for user-friendly messages

**Implementation Pattern**:
```python
# Backend
class ConflictError(Exception):
    def __init__(self, message, code):
        self.message = message
        self.code = code

@app.errorhandler(ConflictError)
def handle_conflict(error):
    return jsonify({
        "error": "Conflict",
        "message": error.message,
        "code": error.code
    }), 409

# Usage
if organisation.children:
    raise ConflictError(
        f"Organisation '{organisation.name}' has {len(organisation.children)} children associated.",
        "ORGANISATION_HAS_CHILDREN"
    )
```

**Alternatives Considered**:
- Generic error messages: Rejected, poor UX
- Modal dialogs for all errors: Rejected, interrupts workflow unnecessarily
- Custom error codes per error type: Rejected as over-engineering initially

**References**:
- HTTP status codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
- Flask error handling: https://flask.palletsprojects.com/en/3.0.x/errorhandling/

---

## Summary

All research questions have been resolved with concrete decisions. Key takeaways:

1. **Database**: Use explicit association tables, polymorphic channel model with JSON config
2. **API**: RESTful resource-based endpoints with standard HTTP verbs
3. **Validation**: Multi-layer validation (Pydantic + API + Database)
4. **Frontend**: React Context for state management, no Redux
5. **Error Handling**: Structured JSON errors with specific HTTP status codes
6. **Security**: Reuse existing encrypted credential storage

All decisions align with Constitution principles (Separation of Concerns, Secure by Default, Local-First MVP, Simplicity & Pragmatism).

**Ready to proceed to Phase 1: Design & Contracts**
