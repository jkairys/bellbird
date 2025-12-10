# Compass Client API Contracts

**Feature**: 002-compass-api-decoupling
**Date**: 2025-12-09
**Status**: Draft

## Overview

This directory contains formal API contracts for the `compass-client` package. These contracts define the public API, interfaces, behavior, and data schemas that implementers and consumers can rely on.

## Purpose

These contracts serve multiple purposes:

1. **Implementation Guide**: Reference for developers implementing the compass-client package
2. **Integration Guide**: Reference for consumers integrating the compass-client package into applications
3. **Contract Testing**: Basis for automated contract tests that verify compliance
4. **Documentation**: Comprehensive API documentation for package users
5. **Version Control**: Track API changes and maintain backward compatibility

## Documents

### 1. [compass-client-api.md](./compass-client-api.md)

**Public API Contract**

Complete reference for the compass-client package public API including:

- Exported classes: `CompassClient`, `CompassMockClient`
- Factory function: `create_client()`
- Models: `CompassEvent`, `CompassUser`, nested models
- Parser: `CompassParser` with generic parsing methods
- Exceptions: `CompassClientError`, `CompassAuthenticationError`, `CompassParseError`
- Usage examples for common scenarios
- Migration guide from monolithic structure

**Use this for**:
- Learning how to use the package
- Understanding method signatures and return types
- Reference during implementation
- API documentation generation

---

### 2. [client-interface.md](./client-interface.md)

**Interface Protocol Definition**

Formal specification of the interface that all Compass clients must implement:

- Required methods with exact signatures
- Required attributes and their types
- Pre-conditions and post-conditions for each method
- State machine diagram
- Interface parity requirements between real and mock clients
- Contract compliance tests

**Use this for**:
- Verifying interface compliance
- Understanding behavioral contracts
- Implementing new client types
- Writing contract tests

---

### 3. [factory-contract.md](./factory-contract.md)

**Factory Function Contract**

Detailed specification of the `create_client()` factory function:

- Function signature and parameters
- Configuration mode selection logic
- Environment variable handling
- Configuration precedence (parameter > env var > default)
- Error handling and validation
- Usage examples for all scenarios

**Use this for**:
- Understanding mode selection logic
- Configuring clients in different environments
- Setting up CI/CD pipelines
- Debugging configuration issues

---

### 4. [mock-data-schema.json](./mock-data-schema.json)

**JSON Schema for Mock Data Files**

Formal JSON Schema definitions for mock data files:

- `compass_events.json`: Array of calendar events
- `compass_user.json`: Single user details object
- `schema_version.json`: Mock data version tracking
- Nested object definitions (locations, managers)
- Field-level validation rules
- Complete examples

**Use this for**:
- Validating mock data files
- Generating mock data
- Understanding expected data structures
- Schema evolution and versioning

---

## Contract Relationships

```
┌─────────────────────────┐
│ compass-client-api.md   │  ← Complete API reference
│ (Public API)            │
└───────────┬─────────────┘
            │
            ├──────────────────────────────┐
            │                              │
            ↓                              ↓
┌─────────────────────────┐    ┌─────────────────────────┐
│ client-interface.md     │    │ factory-contract.md     │
│ (Client Protocol)       │    │ (Factory Behavior)      │
└───────────┬─────────────┘    └─────────────────────────┘
            │
            ↓
┌─────────────────────────┐
│ mock-data-schema.json   │
│ (Data Validation)       │
└─────────────────────────┘
```

## Usage Scenarios

### For Package Implementers

1. Read [client-interface.md](./client-interface.md) to understand required behavior
2. Refer to [compass-client-api.md](./compass-client-api.md) for detailed method specifications
3. Use [mock-data-schema.json](./mock-data-schema.json) to validate test data
4. Implement contract tests from interface specification

### For Package Consumers

1. Read [compass-client-api.md](./compass-client-api.md) for usage examples
2. Refer to [factory-contract.md](./factory-contract.md) for configuration
3. Use [mock-data-schema.json](./mock-data-schema.json) to understand data structures

### For Integration Testing

1. Use [client-interface.md](./client-interface.md) for contract tests
2. Validate mock data against [mock-data-schema.json](./mock-data-schema.json)
3. Verify factory behavior using [factory-contract.md](./factory-contract.md)

---

## Contract Versioning

All contracts are versioned together with the compass-client package using semantic versioning:

- **Major version**: Breaking API changes (method signature changes, removed features)
- **Minor version**: Backward-compatible additions (new methods, new optional parameters)
- **Patch version**: Backward-compatible bug fixes (documentation updates, clarifications)

**Current Version**: 1.0.0

## Contract Testing

These contracts should be enforced through automated tests:

### Interface Compliance Tests

```python
import pytest
from compass_client import CompassClient, CompassMockClient

@pytest.mark.parametrize("client_class", [CompassClient, CompassMockClient])
def test_interface_compliance(client_class):
    """Verify both clients implement the same interface."""
    # Test method signatures, attributes, behavior
    # See client-interface.md for complete test cases
```

### Factory Behavior Tests

```python
def test_factory_mode_selection():
    """Verify factory respects configuration precedence."""
    # Test parameter override, env var, defaults
    # See factory-contract.md for complete test cases
```

### Data Schema Tests

```python
def test_mock_data_schema_compliance():
    """Verify mock data files match JSON Schema."""
    # Validate compass_events.json, compass_user.json
    # See mock-data-schema.json for schema
```

---

## Related Documentation

- [../spec.md](../spec.md) - Feature specification
- [../plan.md](../plan.md) - Implementation plan
- [../data-model.md](../data-model.md) - Data model documentation
- [../quickstart.md](../quickstart.md) - Developer quickstart guide

---

## Examples

### Basic Usage Example

```python
from compass_client import create_client, CompassParser, CompassEvent

# Create client in mock mode
client = create_client(
    base_url="https://school.compass.education",
    username="parent@example.com",
    password="password",
    mode="mock"
)

# Authenticate
client.login()

# Fetch raw data
raw_events = client.get_calendar_events("2025-12-01", "2025-12-31")

# Parse into validated models
events = CompassParser.parse(CompassEvent, raw_events)

# Type-safe access
for event in events:
    print(f"{event.title} on {event.start.strftime('%Y-%m-%d')}")
```

See [compass-client-api.md](./compass-client-api.md) for more examples.

---

## Feedback and Changes

If you find issues with these contracts:

1. **Clarifications**: Update the contract documents directly
2. **Breaking Changes**: Increment major version and document migration path
3. **New Features**: Increment minor version and add backward-compatible documentation

---

## Document Metadata

- **Created**: 2025-12-09
- **Feature**: 002-compass-api-decoupling
- **Version**: 1.0.0
- **Author**: Claude Code
