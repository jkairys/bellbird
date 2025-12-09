# Feature Specification: Family Management System

**Feature Branch**: `001-family-management`
**Created**: 2025-12-09
**Status**: Draft
**Input**: User description: "child, school and portal management - users of bellweaver need to be able to customise it to suit their family. They can describe their children including name, gender, date of birth and interests. They can define organisations (which could be a school, a daycare centre, a kindergarten or a sports team). Children may be members / attend one or more of these organisations. Organisations communicate with parents via one or more communication channels (such as Compass, Xplore, HubHello, Class Dojo, or a facebook messenger group chat). As a parent, I want to define my children, the organisations they attend, and provide details about how those organisations communicate with me. Initially, the system will only support Compass as a communication channel, noting that a parent probably only has one login to compass for a school, which multiple children attend. Ultimately, we'll use this information to fetch information via communication channels and to filter it prior to display."

## Clarifications

### Session 2025-12-09

- Q: Child Profile Deletion - Should parents be able to delete child profiles, and if so, with what constraints? → A: Allow deletion with confirmation dialog (similar to organisation deletion with associations)
- Q: Child Gender Field Format - How should the gender field be structured for child profiles? → A: Free-text field with optional predefined suggestions
- Q: Duplicate Organisation Name Handling - Should the system allow multiple organisations with the same name? → A: Block duplicate names entirely - enforce unique organisation names
- Q: Date of Birth Validation - What validation should be applied to child date of birth? → A: Block future dates only - allow any past date
- Q: Multi-Parent/User Support - Should the system support multiple parents/users sharing access to the same family data? → A: Single-user initially, design for future multi-user expansion

## User Scenarios & Testing

### User Story 1 - Add First Child Profile (Priority: P1)

As a parent using Bellweaver for the first time, I want to create a profile for my first child so that I can start receiving filtered and relevant information about their activities.

**Why this priority**: This is the foundational user journey that enables all other functionality. Without the ability to add children, the system cannot filter or display relevant information. This represents the minimum viable product.

**Independent Test**: Can be fully tested by creating a child profile with name, date of birth, and gender, then verifying the profile is saved and can be retrieved. Delivers immediate value by establishing the parent's family structure in the system.

**Acceptance Scenarios**:

1. **Given** I am a logged-in parent with no existing children, **When** I navigate to add a child and enter required information (name, date of birth, gender), **Then** the child profile is created and appears in my family overview
2. **Given** I am creating a child profile, **When** I provide optional information like interests, **Then** this information is saved with the child profile for future filtering
3. **Given** I am creating a child profile, **When** I try to save without required fields (name, date of birth), **Then** I receive clear validation messages indicating which fields are required
4. **Given** I have created a child profile, **When** I view my family dashboard, **Then** I see the child's name and key details displayed

---

### User Story 2 - Manage Multiple Children (Priority: P1)

As a parent with multiple children, I want to add, view, and edit profiles for all my children so that I can manage information for my entire family in one place.

**Why this priority**: Most families have multiple children, making this essential for real-world usage. Without this, the system only works for single-child families, severely limiting its value.

**Independent Test**: Can be tested by adding multiple child profiles, editing existing profiles, and verifying each child's information is independently maintained. Delivers value by supporting realistic family structures.

**Acceptance Scenarios**:

1. **Given** I already have one child profile, **When** I add a second child, **Then** both children appear in my family overview with distinct profiles
2. **Given** I have multiple children, **When** I edit one child's profile, **Then** only that child's information changes and other profiles remain unchanged
3. **Given** I have multiple children, **When** I view my family overview, **Then** I can clearly distinguish between each child's information
4. **Given** I have a child profile with outdated information, **When** I update their interests or other details, **Then** the changes are saved and reflected immediately

---

### User Story 3 - Define Organisation (Priority: P2)

As a parent, I want to define an organisation (school, daycare, sports team) that my children attend so that I can later connect communication channels and associate children with these organisations.

**Why this priority**: Organisations are the context in which children receive communications. This is required before communications can be properly filtered, but the system can still function with just child profiles.

**Independent Test**: Can be tested by creating an organisation record with name and type, verifying it's saved and retrievable. Delivers value by establishing the organizational context for future communication filtering.

**Acceptance Scenarios**:

1. **Given** I am a logged-in parent, **When** I create a new organisation with a name and type (school/daycare/sports team/other), **Then** the organisation is saved and appears in my organisations list
2. **Given** I am creating an organisation, **When** I provide additional details like address or contact information, **Then** this optional information is saved with the organisation
3. **Given** I have multiple organisations, **When** I view my organisations list, **Then** I can see all organisations with their names and types clearly displayed

---

### User Story 4 - Associate Children with Organisations (Priority: P2)

As a parent, I want to specify which organisations each of my children attends so that communications can be filtered appropriately for each child.

**Why this priority**: This creates the link between children and organisations, which is essential for filtering. However, it depends on both child profiles and organisations existing first.

**Independent Test**: Can be tested by assigning a child to one or more organisations and verifying the associations are maintained. Delivers value by establishing which communications are relevant to which children.

**Acceptance Scenarios**:

1. **Given** I have at least one child and one organisation defined, **When** I associate my child with an organisation, **Then** the association is saved and visible when viewing either the child or organisation
2. **Given** I have a child attending multiple organisations, **When** I add multiple organisation associations for that child, **Then** all associations are maintained and displayed
3. **Given** I have multiple children, **When** I associate each child with their respective organisations, **Then** each child maintains their own independent set of organisation associations
4. **Given** A child has graduated or left an organisation, **When** I remove the association, **Then** the child is no longer associated with that organisation

---

### User Story 5 - Connect Compass Communication Channel (Priority: P2)

As a parent whose child's school uses Compass, I want to provide my Compass login credentials for an organisation so that the system can fetch events and communications from Compass on my behalf.

**Why this priority**: This is the first communication channel integration and enables the system to actually fetch real data. However, it requires organisations to be defined first. Since only Compass is initially supported, this is essential for the feature to deliver end-to-end value.

**Independent Test**: Can be tested by adding Compass credentials for an organisation, verifying credentials are securely stored, and confirming the system can authenticate with Compass. Delivers value by enabling automated data retrieval.

**Acceptance Scenarios**:

1. **Given** I have defined an organisation, **When** I add Compass as a communication channel with my username, password, and base URL, **Then** the credentials are securely stored and associated with the organisation
2. **Given** I have entered Compass credentials, **When** the system attempts to authenticate, **Then** I receive feedback on whether the credentials are valid
3. **Given** I have invalid Compass credentials saved, **When** I update them with correct credentials, **Then** the new credentials replace the old ones and authentication succeeds
4. **Given** Multiple children attend the same school using Compass, **When** I configure Compass once for the school organisation, **Then** all children associated with that school can use the same Compass connection

---

### User Story 6 - View Channel Configuration Status (Priority: P3)

As a parent who has configured communication channels, I want to see which organisations have channels configured and their status so that I know whether the system can fetch data for each organisation.

**Why this priority**: This provides visibility and helps parents troubleshoot configuration issues, but the core functionality can work without this dashboard view.

**Independent Test**: Can be tested by configuring channels for various organisations and verifying the status display accurately reflects which are configured and which are not. Delivers value through transparency and configuration management.

**Acceptance Scenarios**:

1. **Given** I have multiple organisations, **When** I view my communication channels overview, **Then** I see which organisations have channels configured and which do not
2. **Given** I have configured Compass for an organisation, **When** I view the channel status, **Then** I see whether the last connection attempt was successful or failed
3. **Given** An organisation has no communication channels configured, **When** I view its status, **Then** I see an indicator that setup is needed with guidance on how to add a channel

---

### Edge Cases

**Handled**:
- When a duplicate organisation name is entered, the system blocks creation and displays an error message requiring a unique name (FR-010a)
- When a child's date of birth is set to a future date, the system blocks creation and displays an error message (FR-010b)
- When a parent deletes a child who has organisation associations, the system automatically removes all child-organisation associations after confirmation (FR-017)
- When a parent tries to delete an organisation that has children associated with it, the system blocks deletion and displays an error message indicating that all child associations must be removed first (FR-011)
- When multiple children attend the same school, the Compass credential is configured once at the organisation level and shared across all children via their organisation associations (FR-009)
- When Compass credentials change (password reset), the parent uses PUT /api/channels/:id to update credentials, which re-validates before saving (FR-016)

**API Error Responses** (Testable):
- When a parent tries to associate a child with an organisation that doesn't exist, API returns 404 Not Found with error message "Child or organisation not found"
- When a parent enters invalid Compass credentials, API returns 400 Bad Request with error message "Compass authentication failed - please check username, password, and base URL"
- When creating a duplicate child-organisation association, API returns 409 Conflict with error message "Child is already associated with this organisation"

## Requirements

### Scope & Constraints

- **Scope-001**: Initial implementation supports single-user access only (one parent/user per family)
- **Scope-002**: Data model and architecture should be designed to allow future expansion to multi-user/multi-parent access without major refactoring

### Functional Requirements

- **FR-001**: System MUST allow parents to create child profiles with required fields: name, date of birth, and gender (free-text field with optional predefined suggestions for common values)
- **FR-002**: System MUST allow parents to optionally add interests or other descriptive information to child profiles
- **FR-003**: System MUST allow parents to edit existing child profiles at any time
- **FR-004**: System MUST allow parents to create organisation records with required fields: name and type (school, daycare, kindergarten, sports team, other)
- **FR-005**: System MUST allow parents to associate children with one or more organisations
- **FR-006**: System MUST allow parents to remove associations between children and organisations
- **FR-007**: System MUST allow parents to configure Compass as a communication channel for an organisation by providing username, password, and base URL
- **FR-008**: System MUST securely store Compass credentials using encryption (leveraging existing Fernet-based credential storage)
- **FR-009**: System MUST support multiple children being associated with the same organisation while sharing a single Compass credential
- **FR-010**: System MUST validate that required fields are provided when creating child profiles and organisations
- **FR-010a**: System MUST enforce unique organisation names and display an error message if a duplicate name is entered
- **FR-010b**: System MUST validate that child date of birth is not in the future and display an error message if a future date is provided
- **FR-011**: System MUST prevent deletion of organisations that have active child associations and display an error message indicating that all child associations must be removed first
- **FR-012**: System MUST allow parents to view all child profiles in a family overview
- **FR-013**: System MUST allow parents to view all defined organisations
- **FR-014**: System MUST allow parents to view which communication channels are configured for each organisation
- **FR-015**: System MUST validate Compass credentials when they are added or updated
- **FR-016**: System MUST allow parents to update Compass credentials for an organisation
- **FR-017**: System MUST allow parents to delete child profiles after confirming deletion through a confirmation dialog, and automatically remove all associated child-organisation associations

### Key Entities

- **Child**: Represents a child in the family with attributes including name, date of birth, gender, and optional interests. A child can be associated with multiple organisations.

- **Organisation**: Represents a school, daycare, kindergarten, sports team, or other institution. Has attributes including name and type. Can have multiple children associated with it and multiple communication channels configured for it.

- **Communication Channel**: Represents a way that an organisation communicates with parents (initially only Compass supported). Linked to a specific organisation and stores channel-specific credentials and configuration. Multiple children may use the same channel if they attend the same organisation.

- **Child-Organisation Association**: Links a child to an organisation they attend. This many-to-many relationship allows children to attend multiple organisations and organisations to have multiple children.

## Success Criteria

### Measurable Outcomes

#### API Performance (Testable via Integration Tests)

- **SC-001**: POST /api/children endpoint responds in <200ms with valid child data
- **SC-002**: POST /api/children/:id/organisations endpoint responds in <200ms when creating association
- **SC-003**: POST /api/organisations/:id/channels endpoint validates Compass credentials and responds in <5 seconds
- **SC-004**: 100% of Compass credentials are stored securely using encryption (verified via database inspection)
- **SC-005**: GET /api/children and GET /api/organisations endpoints return complete family structure in <200ms
- **SC-006**: System correctly handles families with up to 10 children and 20 organisations without performance degradation (all API endpoints maintain <200ms response time)
- **SC-007**: PUT /api/channels/:id endpoint re-validates credentials and responds in <5 seconds when credentials change

#### User Experience (Manual Testing)

- **SC-008**: Parents can create a complete child profile via UI in under 1 minute (form interaction + validation feedback)
- **SC-009**: Parents can associate a child with an organisation via UI in under 30 seconds
- **SC-010**: 95% of parents successfully configure their first communication channel without assistance (UX testing)
