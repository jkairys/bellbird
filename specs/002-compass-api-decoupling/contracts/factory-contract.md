# Compass Client Factory Contract

**Package**: `compass-client`
**Module**: `compass_client.factory`
**Version**: 1.0.0
**Date**: 2025-12-09

## Overview

The `create_client()` factory function provides a unified interface for creating Compass client instances. It automatically selects between real and mock implementations based on configuration, enabling seamless switching between production and development/testing modes.

---

## Function Signature

```python
def create_client(
    base_url: str,
    username: str,
    password: str,
    mode: Optional[str] = None
) -> CompassClient | CompassMockClient
```

---

## Parameters

### `base_url: str` (required)

**Purpose**: Base URL of Compass instance.

**Format**: Full URL including protocol (e.g., `"https://school.compass.education"`)

**Validation**:
- MUST be non-empty string
- SHOULD include protocol (`https://` or `http://`)
- Real client normalizes by stripping trailing slashes
- Mock client stores as-is (not used)

**Examples**:
- Valid: `"https://demo.compass.education"`
- Valid: `"https://school.compass.education/"`
- Invalid: `""` (empty string)
- Invalid: `"school.compass.education"` (missing protocol, but accepted)

---

### `username: str` (required)

**Purpose**: Username for Compass authentication.

**Format**: String (typically email address or user code)

**Validation**:
- MUST be non-empty string
- Real client uses for authentication
- Mock client stores but doesn't use (can be dummy value)

**Examples**:
- Valid: `"parent@example.com"`
- Valid: `"john.smith"`
- Invalid: `""` (empty string)

---

### `password: str` (required)

**Purpose**: Password for Compass authentication.

**Format**: String

**Validation**:
- MUST be non-empty string
- Real client uses for authentication
- Mock client stores but doesn't use (can be dummy value)

**Examples**:
- Valid: `"secure_password_123"`
- Valid: `"dummy"` (acceptable for mock mode)
- Invalid: `""` (empty string)

---

### `mode: Optional[str] = None` (optional)

**Purpose**: Explicitly set client mode (real vs. mock).

**Format**: String literal: `"real"` or `"mock"` (case-insensitive)

**Default**: `None` (reads from environment variable)

**Validation**:
- MUST be `None`, `"real"`, or `"mock"` (case-insensitive)
- Invalid values raise `ValueError`

**Examples**:
- Valid: `None` (use environment variable)
- Valid: `"real"` (explicit real mode)
- Valid: `"MOCK"` (case-insensitive)
- Valid: `"Real"` (case-insensitive)
- Invalid: `"production"` (raises `ValueError`)
- Invalid: `"test"` (raises `ValueError`)

---

## Return Value

### Type: `CompassClient | CompassMockClient`

**Returns**:
- `CompassClient` instance if mode is `"real"`
- `CompassMockClient` instance if mode is `"mock"`

**Post-conditions**:
- Returned client is in **Created** state
- `_authenticated` is `False`
- Client is ready for `login()` call

**Example**:

```python
client = create_client(
    base_url="https://school.compass.education",
    username="parent@example.com",
    password="password",
    mode="mock"
)
assert isinstance(client, CompassMockClient)
assert client._authenticated is False
```

---

## Exceptions

### `ValueError`

**When Raised**:
- `mode` parameter is not `None`, `"real"`, or `"mock"` (case-insensitive)

**Message**: `"Invalid COMPASS_MODE: {mode}. Must be 'real' or 'mock'."`

**Example**:

```python
try:
    client = create_client(..., mode="invalid")
except ValueError as e:
    print(e)  # "Invalid COMPASS_MODE: invalid. Must be 'real' or 'mock'."
```

---

## Configuration Mode Selection

### Priority Order

The factory determines mode using this priority order:

1. **Explicit `mode` parameter** (highest priority)
2. **`COMPASS_MODE` environment variable**
3. **Default value `"real"`** (lowest priority)

### Configuration Precedence Table

| `mode` Parameter | `COMPASS_MODE` Env Var | Effective Mode | Client Type |
|------------------|------------------------|----------------|-------------|
| `"real"` | Any value | `"real"` | `CompassClient` |
| `"mock"` | Any value | `"mock"` | `CompassMockClient` |
| `None` | `"real"` | `"real"` | `CompassClient` |
| `None` | `"mock"` | `"mock"` | `CompassMockClient` |
| `None` | Not set | `"real"` | `CompassClient` |
| `None` | `"REAL"` | `"real"` | `CompassClient` |
| `None` | `"Mock"` | `"mock"` | `CompassMockClient` |

---

## Environment Variable

### `COMPASS_MODE`

**Purpose**: Configure client mode globally via environment.

**Format**: String literal: `"real"` or `"mock"` (case-insensitive)

**Default**: `"real"` (if not set)

**Validation**:
- Case-insensitive (e.g., `"MOCK"`, `"Mock"`, `"mock"` all work)
- Invalid values raise `ValueError`

**Scope**:
- Application-wide configuration
- Typically set in `.env` file or CI environment

**Examples**:

```bash
# .env file
COMPASS_MODE=mock

# CI environment
export COMPASS_MODE=mock

# Docker Compose
environment:
  - COMPASS_MODE=mock
```

---

## Mode Selection Logic

### Pseudo-code

```python
def create_client(base_url, username, password, mode=None):
    # Step 1: Determine effective mode
    if mode is not None:
        effective_mode = mode.lower()
    else:
        effective_mode = os.getenv("COMPASS_MODE", "real").lower()

    # Step 2: Validate mode
    if effective_mode not in ["real", "mock"]:
        raise ValueError(
            f"Invalid COMPASS_MODE: {effective_mode}. Must be 'real' or 'mock'."
        )

    # Step 3: Create appropriate client
    if effective_mode == "mock":
        return CompassMockClient(base_url, username, password)
    else:  # effective_mode == "real"
        return CompassClient(base_url, username, password)
```

---

## Usage Examples

### Example 1: Explicit Mode (Real)

```python
from compass_client import create_client

client = create_client(
    base_url="https://school.compass.education",
    username="parent@example.com",
    password="secure_password",
    mode="real"  # Explicit real mode
)

# client is CompassClient instance
assert client.__class__.__name__ == "CompassClient"
```

---

### Example 2: Explicit Mode (Mock)

```python
from compass_client import create_client

client = create_client(
    base_url="https://school.compass.education",
    username="parent@example.com",
    password="dummy",  # Not used in mock mode
    mode="mock"  # Explicit mock mode
)

# client is CompassMockClient instance
assert client.__class__.__name__ == "CompassMockClient"
```

---

### Example 3: Environment Variable (Mock)

```python
import os
from compass_client import create_client

# Set environment variable
os.environ["COMPASS_MODE"] = "mock"

# Create client (reads from environment)
client = create_client(
    base_url="https://school.compass.education",
    username="parent@example.com",
    password="dummy"
    # mode=None (default) reads COMPASS_MODE env var
)

# client is CompassMockClient instance
assert client.__class__.__name__ == "CompassMockClient"
```

---

### Example 4: Default Mode (Real)

```python
import os
from compass_client import create_client

# Ensure COMPASS_MODE is not set
if "COMPASS_MODE" in os.environ:
    del os.environ["COMPASS_MODE"]

# Create client (defaults to real)
client = create_client(
    base_url="https://school.compass.education",
    username="parent@example.com",
    password="secure_password"
    # mode=None, COMPASS_MODE not set → defaults to "real"
)

# client is CompassClient instance
assert client.__class__.__name__ == "CompassClient"
```

---

### Example 5: Override Environment with Parameter

```python
import os
from compass_client import create_client

# Set environment to mock
os.environ["COMPASS_MODE"] = "mock"

# Override with explicit parameter
client = create_client(
    base_url="https://school.compass.education",
    username="parent@example.com",
    password="secure_password",
    mode="real"  # Overrides COMPASS_MODE env var
)

# client is CompassClient instance (parameter takes precedence)
assert client.__class__.__name__ == "CompassClient"
```

---

### Example 6: Case-Insensitive Mode

```python
from compass_client import create_client

# All of these work (case-insensitive)
client1 = create_client(..., mode="mock")
client2 = create_client(..., mode="MOCK")
client3 = create_client(..., mode="Mock")

# All create CompassMockClient
assert client1.__class__.__name__ == "CompassMockClient"
assert client2.__class__.__name__ == "CompassMockClient"
assert client3.__class__.__name__ == "CompassMockClient"
```

---

### Example 7: Invalid Mode (Error)

```python
from compass_client import create_client

try:
    client = create_client(
        base_url="https://school.compass.education",
        username="parent@example.com",
        password="password",
        mode="invalid"  # Invalid mode
    )
except ValueError as e:
    print(e)  # "Invalid COMPASS_MODE: invalid. Must be 'real' or 'mock'."
```

---

## Integration with Environment Files

### .env File Example

```bash
# Compass Configuration
COMPASS_MODE=mock                              # Use mock data for development
COMPASS_BASE_URL=https://school.compass.education
COMPASS_USERNAME=parent@example.com
COMPASS_PASSWORD=secure_password

# Other application config...
```

### Loading from .env

```python
import os
from dotenv import load_dotenv
from compass_client import create_client

# Load environment variables from .env file
load_dotenv()

# Create client (reads all config from environment)
client = create_client(
    base_url=os.getenv("COMPASS_BASE_URL"),
    username=os.getenv("COMPASS_USERNAME"),
    password=os.getenv("COMPASS_PASSWORD")
    # mode reads from COMPASS_MODE env var
)
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run tests with mock mode
        env:
          COMPASS_MODE: mock  # Use mock mode in CI
        run: |
          pytest tests/
```

---

### Docker Compose Example

```yaml
# docker-compose.yml
services:
  bellweaver:
    build: .
    environment:
      - COMPASS_MODE=mock  # Use mock mode in Docker
      - COMPASS_BASE_URL=https://school.compass.education
      - COMPASS_USERNAME=dummy
      - COMPASS_PASSWORD=dummy
    volumes:
      - ./data:/app/data
```

---

## Design Rationale

### Why Factory Pattern?

1. **Abstraction**: Consumers don't need to know which client to use
2. **Configuration**: Centralized mode selection logic
3. **Flexibility**: Easy to add new client types in future
4. **Testing**: Simplifies test setup (just set environment variable)

### Why Environment Variable?

1. **12-Factor App**: Configuration via environment (industry best practice)
2. **Deployment Flexibility**: Different modes per environment (dev/staging/prod)
3. **CI/CD**: Easy to set in pipelines without code changes
4. **Security**: Credentials stay in environment, not hardcoded

### Why Allow Parameter Override?

1. **Explicit Control**: Tests can force specific mode regardless of environment
2. **Debugging**: Developers can override for local testing
3. **Flexibility**: Supports both config-driven and explicit usage patterns

---

## Contract Guarantees

### What the Factory Guarantees

1. **Type Safety**: Returns `CompassClient` or `CompassMockClient` (both implement same interface)
2. **Configuration Priority**: Parameter > Environment > Default (documented order)
3. **Validation**: Raises `ValueError` for invalid modes (fail-fast)
4. **Initialization**: Returned client is in **Created** state, ready for `login()`
5. **Case Insensitivity**: Mode strings are case-insensitive

### What the Factory Does NOT Guarantee

1. **Authentication**: Does not call `login()` (consumer must call it)
2. **Credential Validation**: Does not validate credentials (deferred to `login()`)
3. **Network Access**: Does not test connectivity to Compass API
4. **Environment Variable Presence**: Uses default if `COMPASS_MODE` not set

---

## Testing Strategies

### Unit Test: Factory Logic

```python
import pytest
import os
from compass_client import create_client, CompassClient, CompassMockClient

def test_factory_explicit_real_mode():
    """Test explicit real mode parameter."""
    client = create_client("https://example.com", "user", "pass", mode="real")
    assert isinstance(client, CompassClient)

def test_factory_explicit_mock_mode():
    """Test explicit mock mode parameter."""
    client = create_client("https://example.com", "user", "pass", mode="mock")
    assert isinstance(client, CompassMockClient)

def test_factory_env_var_mock():
    """Test mock mode from environment variable."""
    os.environ["COMPASS_MODE"] = "mock"
    client = create_client("https://example.com", "user", "pass")
    assert isinstance(client, CompassMockClient)

def test_factory_default_real():
    """Test default real mode when no config provided."""
    if "COMPASS_MODE" in os.environ:
        del os.environ["COMPASS_MODE"]
    client = create_client("https://example.com", "user", "pass")
    assert isinstance(client, CompassClient)

def test_factory_parameter_overrides_env():
    """Test explicit parameter overrides environment variable."""
    os.environ["COMPASS_MODE"] = "mock"
    client = create_client("https://example.com", "user", "pass", mode="real")
    assert isinstance(client, CompassClient)

def test_factory_case_insensitive():
    """Test case-insensitive mode strings."""
    client1 = create_client(..., mode="MOCK")
    client2 = create_client(..., mode="Mock")
    client3 = create_client(..., mode="mock")
    assert all(isinstance(c, CompassMockClient) for c in [client1, client2, client3])

def test_factory_invalid_mode():
    """Test invalid mode raises ValueError."""
    with pytest.raises(ValueError, match="Invalid COMPASS_MODE"):
        create_client("https://example.com", "user", "pass", mode="invalid")
```

---

### Integration Test: Factory with Clients

```python
def test_factory_creates_functional_clients():
    """Test that factory-created clients are fully functional."""
    # Test real client (may fail in CI without credentials)
    real_client = create_client(
        base_url=os.getenv("COMPASS_BASE_URL"),
        username=os.getenv("COMPASS_USERNAME"),
        password=os.getenv("COMPASS_PASSWORD"),
        mode="real"
    )
    # (Skip login test if credentials not available)

    # Test mock client (always works)
    mock_client = create_client(
        base_url="",
        username="",
        password="",
        mode="mock"
    )
    assert mock_client.login() is True
    user_data = mock_client.get_user_details()
    assert isinstance(user_data, dict)
```

---

## Future Enhancements

### Planned for v2.0

#### 1. Client Registry

```python
# Allow registering custom client types
from compass_client import register_client_type

register_client_type("cached", CachedCompassClient)

# Factory automatically uses registered types
client = create_client(..., mode="cached")
```

#### 2. Configuration Objects

```python
from compass_client import ClientConfig, create_client

config = ClientConfig(
    base_url="https://school.compass.education",
    username="parent@example.com",
    password="secure_password",
    mode="mock"
)

client = create_client(config=config)
```

#### 3. Async Support

```python
from compass_client import create_async_client

async_client = create_async_client(..., mode="real")
await async_client.login()
events = await async_client.get_calendar_events(...)
```

---

## Document Metadata

- **Created**: 2025-12-09
- **Feature**: 002-compass-api-decoupling
- **Version**: 1.0.0
- **Related Documents**:
  - [compass-client-api.md](./compass-client-api.md) - Full API documentation
  - [client-interface.md](./client-interface.md) - Interface protocol
  - [mock-data-schema.json](./mock-data-schema.json) - Mock data schema
