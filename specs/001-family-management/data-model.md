# Data Model: Family Management System

**Date**: 2025-12-09
**Feature**: 001-family-management

This document defines the data entities, relationships, and validation rules for the Family Management System.

---

## Entity Relationship Diagram

```
┌─────────────────┐
│     Child       │
├─────────────────┤
│ id (PK)         │
│ name            │
│ date_of_birth   │
│ gender          │
│ interests       │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │ Many-to-Many
         │
         ▼
┌──────────────────────┐         ┌─────────────────────┐
│ ChildOrganisation    │◄────────┤   Organisation      │
├──────────────────────┤         ├─────────────────────┤
│ child_id (PK, FK)    │         │ id (PK)             │
│ organisation_id      │         │ name (UNIQUE)       │
│   (PK, FK)           │         │ type                │
└──────────────────────┘         │ address             │
                                 │ contact_info        │
                                 │ created_at          │
                                 │ updated_at          │
                                 └──────────┬──────────┘
                                            │
                                            │ One-to-Many
                                            │
                                            ▼
                             ┌──────────────────────────┐
                             │ CommunicationChannel     │
                             ├──────────────────────────┤
                             │ id (PK)                  │
                             │ organisation_id (FK)     │
                             │ channel_type             │
                             │ credential_source (FK)   │──┐
                             │ config (JSON)            │  │
                             │ is_active                │  │
                             │ last_sync_at             │  │
                             │ last_sync_status         │  │
                             │ created_at               │  │
                             │ updated_at               │  │
                             └──────────────────────────┘  │
                                                            │
                                                            │ Foreign Key
                                                            │
                                                            ▼
                                             ┌──────────────────────┐
                                             │   Credential         │
                                             │   (EXISTING)         │
                                             ├──────────────────────┤
                                             │ source (PK)          │
                                             │ username             │
                                             │ password_encrypted   │
                                             │ created_at           │
                                             │ updated_at           │
                                             └──────────────────────┘
```

---

## Entity Definitions

### 1. Child

Represents a child in the family.

**Table**: `children`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | String(36) | PRIMARY KEY, NOT NULL | UUID v4 |
| `name` | String(200) | NOT NULL | Child's full name |
| `date_of_birth` | Date | NOT NULL | Child's date of birth |
| `gender` | String(50) | NULLABLE | Free-text gender field |
| `interests` | Text | NULLABLE | Optional interests/hobbies |
| `created_at` | DateTime | NOT NULL | Record creation timestamp (UTC) |
| `updated_at` | DateTime | NOT NULL | Record update timestamp (UTC) |

**Relationships**:
- Many-to-Many with `Organisation` via `ChildOrganisation` table

**Validation Rules**:
- `name`: 1-200 characters, required
- `date_of_birth`: Must not be in the future
- `gender`: Optional, max 50 characters
- `interests`: Optional text field

**Business Rules**:
- When a child is deleted, all `ChildOrganisation` associations must be automatically removed (cascade delete)

**Indexes**:
- Primary key on `id`
- Index on `created_at` for sorting

---

### 2. Organisation

Represents a school, daycare, kindergarten, sports team, or other institution.

**Table**: `organisations`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | String(36) | PRIMARY KEY, NOT NULL | UUID v4 |
| `name` | String(200) | NOT NULL, UNIQUE | Organisation name |
| `type` | String(50) | NOT NULL | Organisation type (school, daycare, kindergarten, sports_team, other) |
| `address` | String(500) | NULLABLE | Physical address |
| `contact_info` | JSON | NULLABLE | Contact details (phone, email, website) |
| `created_at` | DateTime | NOT NULL | Record creation timestamp (UTC) |
| `updated_at` | DateTime | NOT NULL | Record update timestamp (UTC) |

**Relationships**:
- Many-to-Many with `Child` via `ChildOrganisation` table
- One-to-Many with `CommunicationChannel`

**Validation Rules**:
- `name`: 1-200 characters, required, must be unique
- `type`: Must be one of: "school", "daycare", "kindergarten", "sports_team", "other"
- `address`: Optional, max 500 characters
- `contact_info`: Optional JSON object with optional fields: `phone`, `email`, `website`

**Business Rules**:
- Cannot delete organisation if it has associated children (must return 409 Conflict)
- Organisation name must be unique across all organisations
- When organisation is deleted, all associated `CommunicationChannel` records must be deleted (cascade)

**Indexes**:
- Primary key on `id`
- Unique constraint on `name`
- Index on `type` for filtering
- Index on `created_at` for sorting

---

### 3. ChildOrganisation

Association table linking children to organisations (many-to-many).

**Table**: `child_organisations`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `child_id` | String(36) | PRIMARY KEY, FOREIGN KEY → children.id | Child UUID |
| `organisation_id` | String(36) | PRIMARY KEY, FOREIGN KEY → organisations.id | Organisation UUID |

**Relationships**:
- Foreign key to `Child.id` with CASCADE DELETE
- Foreign key to `Organisation.id` with CASCADE DELETE

**Validation Rules**:
- Both `child_id` and `organisation_id` must reference existing records
- Composite primary key prevents duplicate associations

**Business Rules**:
- A child can be associated with multiple organisations
- An organisation can have multiple children
- Deleting a child automatically removes all its organisation associations
- Deleting an organisation fails if it has children (enforced by business logic, not CASCADE)

**Indexes**:
- Composite primary key on `(child_id, organisation_id)`
- Index on `child_id` for lookups
- Index on `organisation_id` for lookups

---

### 4. CommunicationChannel

Represents a communication channel (e.g., Compass, HubHello, ClassDojo) configured for an organisation.

**Table**: `communication_channels`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | String(36) | PRIMARY KEY, NOT NULL | UUID v4 |
| `organisation_id` | String(36) | FOREIGN KEY → organisations.id, NOT NULL | Parent organisation |
| `channel_type` | String(50) | NOT NULL | Channel type identifier (compass, hubhello, classdojo, etc.) |
| `credential_source` | String(50) | FOREIGN KEY → credentials.source, NULLABLE | Reference to encrypted credentials |
| `config` | JSON | NULLABLE | Channel-specific configuration |
| `is_active` | Boolean | NOT NULL, DEFAULT TRUE | Whether channel is actively syncing |
| `last_sync_at` | DateTime | NULLABLE | Timestamp of last successful sync |
| `last_sync_status` | String(50) | NULLABLE | Status of last sync (success, failed, pending) |
| `created_at` | DateTime | NOT NULL | Record creation timestamp (UTC) |
| `updated_at` | DateTime | NOT NULL | Record update timestamp (UTC) |

**Relationships**:
- Many-to-One with `Organisation` (one organisation can have multiple channels)
- Many-to-One with `Credential` (optional, for channels requiring authentication)

**Validation Rules**:
- `channel_type`: Must be one of: "compass", "hubhello", "classdojo", "xplore", "other"
- `config`: JSON object with channel-specific fields
  - For Compass: `{ "base_url": "https://school.compass.education" }`
  - For future channels: TBD based on channel requirements
- `credential_source`: Optional, but recommended for authenticated channels
- `last_sync_status`: If present, must be one of: "success", "failed", "pending"

**Business Rules**:
- An organisation can have multiple communication channels (e.g., Compass + ClassDojo)
- An organisation can have multiple channels of the same type (edge case: different Compass instances)
- If `credential_source` is set, it must reference an existing `Credential` record
- Deleting an organisation cascades to delete all its communication channels
- Deleting a credential should NOT cascade delete channels (set to NULL instead)

**Channel-Specific Config Schemas**:

**Compass**:
```json
{
  "base_url": "https://school-name.compass.education",
  "sync_interval_hours": 24
}
```

**Future channels**: Config schema TBD when implemented

**Indexes**:
- Primary key on `id`
- Foreign key index on `organisation_id`
- Foreign key index on `credential_source`
- Index on `channel_type` for filtering
- Index on `is_active` for filtering active channels

---

## Validation Summary

### Field-Level Validation (Pydantic Models)

Handled by Pydantic models in `backend/bellweaver/models/family.py`:

- **Type validation**: Ensure correct data types (str, date, bool, etc.)
- **Length validation**: String min/max lengths
- **Format validation**: Date formats, email formats (in contact_info)
- **Required vs optional**: Field presence

### Business-Level Validation (API Layer)

Handled in Flask route handlers in `backend/bellweaver/api/routes.py`:

- **Unique organisation names**: Check before INSERT/UPDATE
- **Future date validation**: date_of_birth must not be > today
- **Credential validation**: Verify Compass credentials when adding channel
- **Association validation**: Ensure child/organisation exist before creating association
- **Deletion conflicts**: Check if organisation has children before allowing delete

### Database-Level Validation (SQLAlchemy Constraints)

Enforced by database schema:

- **Primary keys**: UUID uniqueness
- **Foreign keys**: Referential integrity
- **Unique constraints**: Organisation.name uniqueness
- **NOT NULL constraints**: Required fields
- **Cascade rules**: Child deletion cascades to associations

---

## State Transitions

### Child Lifecycle

```
[CREATE] → Active → [UPDATE] → Active → [DELETE] → Removed
                                          ↓
                                    (Cascades to ChildOrganisation)
```

### Organisation Lifecycle

```
[CREATE] → Active → [UPDATE] → Active → [DELETE (if no children)] → Removed
                                          ↓
                                    (Cascades to CommunicationChannel)
```

If organisation has children:
```
[DELETE attempt] → 409 Conflict → (User must remove children first)
```

### Communication Channel Lifecycle

```
[CREATE] → Inactive (is_active=false) → [VALIDATE] → Active (is_active=true) → [SYNC]
    ↓                                                          ↓
last_sync_status=null                              last_sync_status=success/failed
                                                   last_sync_at=timestamp
```

---

## Migration Considerations

### Adding New Communication Channels

When adding support for new channels (e.g., HubHello, ClassDojo):

1. No schema migration required - just add new `channel_type` value
2. Define new config schema in documentation
3. Implement channel-specific adapter in `backend/bellweaver/adapters/`
4. Update validation logic to accept new channel type

### Future Multi-User Support

Current single-user design can be extended to multi-user:

1. Add `user_id` column to `Child` and `Organisation` tables
2. Add `User` table with authentication
3. Update queries to filter by authenticated user
4. No changes needed to relationships or validation logic

**Design Decision**: Deferred per Constitution IV (Local-First MVP) - build multi-user when needed, not before.

---

## Example Data

### Sample Child Record

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Emma Johnson",
  "date_of_birth": "2015-06-15",
  "gender": "female",
  "interests": "Soccer, reading, science experiments",
  "created_at": "2025-12-09T10:00:00Z",
  "updated_at": "2025-12-09T10:00:00Z"
}
```

### Sample Organisation Record

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440111",
  "name": "Springfield Elementary School",
  "type": "school",
  "address": "123 Main St, Springfield, VIC 3000",
  "contact_info": {
    "phone": "+61 3 9876 5432",
    "email": "admin@springfield.edu.au",
    "website": "https://springfield.edu.au"
  },
  "created_at": "2025-12-09T10:00:00Z",
  "updated_at": "2025-12-09T10:00:00Z"
}
```

### Sample Communication Channel Record

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440222",
  "organisation_id": "660e8400-e29b-41d4-a716-446655440111",
  "channel_type": "compass",
  "credential_source": "compass_springfield",
  "config": {
    "base_url": "https://springfield.compass.education",
    "sync_interval_hours": 24
  },
  "is_active": true,
  "last_sync_at": "2025-12-09T09:00:00Z",
  "last_sync_status": "success",
  "created_at": "2025-12-09T08:00:00Z",
  "updated_at": "2025-12-09T09:00:00Z"
}
```

### Sample ChildOrganisation Association

```json
{
  "child_id": "550e8400-e29b-41d4-a716-446655440000",
  "organisation_id": "660e8400-e29b-41d4-a716-446655440111"
}
```

---

## Summary

This data model provides:

1. **Flexibility**: Many-to-many child-organisation relationships, polymorphic channel support
2. **Extensibility**: JSON config fields, association table ready for metadata
3. **Integrity**: Foreign keys, unique constraints, cascade rules
4. **Security**: Credentials separated in existing encrypted storage
5. **Simplicity**: No over-engineering, standard SQLAlchemy patterns

All entities align with Constitution principles and support the functional requirements from spec.md.

**Ready to proceed to Phase 1: Generate API Contracts**
