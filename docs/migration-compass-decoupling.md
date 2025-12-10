# Migration Guide: Compass API Decoupling

**Feature**: 002-compass-api-decoupling | **Date**: 2025-12-10

This guide helps developers migrate from the old monolithic structure to the new decoupled multi-package architecture.

---

## Overview of Changes

### What Changed?

The Compass API integration has been **extracted into an independent package** (`compass-client`) with the following benefits:

- **Independent Development**: compass-client can be developed and tested separately
- **Mock Data Support**: Full development without Compass credentials via `COMPASS_MODE=mock`
- **CI-Friendly**: Tests run in mock mode, avoiding geo-blocking issues
- **Cleaner Architecture**: Clear separation between API client and application logic
- **Reusability**: compass-client can be used by other projects

### Architecture Before vs After

#### Before (Monolithic)

```
bellweaver/
└── packages/bellweaver/
    └── bellweaver/
        ├── adapters/
        │   ├── compass.py          # Compass HTTP client
        │   └── compass_mock.py     # Mock client
        ├── parsers/
        │   └── compass.py          # Parser logic
        └── models/
            └── compass.py          # Pydantic models
```

**Issues:**
- Compass logic tightly coupled to Bellweaver
- No way to test Compass integration independently
- Required real credentials for all testing
- CI couldn't run in geo-blocked environments

#### After (Decoupled)

```
bellweaver/
├── packages/compass-client/        # Independent package
│   └── compass_client/
│       ├── client.py               # Real API client
│       ├── mock_client.py          # Mock client
│       ├── models.py               # Pydantic models
│       ├── parser.py               # Generic parser
│       ├── factory.py              # create_client() factory
│       └── data/mock/              # Mock data files
│
└── packages/bellweaver/            # Main application
    └── bellweaver/
        ├── cli/                    # Uses compass_client
        ├── api/                    # Uses compass_client
        └── mappers/
            └── compass.py          # Maps compass_client → bellweaver
```

**Benefits:**
- Compass logic completely decoupled
- Independent testing of each package
- Mock mode for development without credentials
- CI works in any environment

---

## Migration Checklist

- [ ] Update imports from `bellweaver.adapters` to `compass_client`
- [ ] Install compass-client package
- [ ] Update environment variables (add `COMPASS_MODE`)
- [ ] Update test fixtures (set `COMPASS_MODE=mock`)
- [ ] Remove old adapter files (if not already removed)
- [ ] Update documentation references
- [ ] Run tests to verify migration

---

## Code Migration

### 1. Import Changes

#### Before (OLD)

```python
# Importing from bellweaver.adapters (DEPRECATED)
from bellweaver.adapters.compass import CompassClient
from bellweaver.adapters.compass_mock import CompassMockClient
from bellweaver.parsers.compass import CompassParser
from bellweaver.models.compass import CompassEvent, CompassUser
```

#### After (NEW)

```python
# Import from independent compass_client package
from compass_client import (
    create_client,       # Factory function (recommended)
    CompassClient,       # Real API client
    CompassMockClient,   # Mock client
    CompassParser,       # Generic parser
    CompassEvent,        # Event model
    CompassUser,         # User model
)
```

### 2. Client Instantiation Changes

#### Before (Manual Selection)

```python
# Manual selection between real and mock clients
if use_mock:
    from bellweaver.adapters.compass_mock import CompassMockClient
    client = CompassMockClient(base_url, username, password)
else:
    from bellweaver.adapters.compass import CompassClient
    client = CompassClient(base_url, username, password)
```

#### After (Factory Pattern)

```python
# Factory automatically selects based on COMPASS_MODE env var
from compass_client import create_client

client = create_client(
    base_url=os.getenv("COMPASS_BASE_URL"),
    username=os.getenv("COMPASS_USERNAME"),
    password=os.getenv("COMPASS_PASSWORD")
    # mode parameter optional - reads from COMPASS_MODE env var
)

# Or explicit override
client = create_client(..., mode="mock")  # Force mock mode
client = create_client(..., mode="real")  # Force real mode
```

### 3. Parser Usage Changes

#### Before (Instance Methods)

```python
# Old: Parser as instance with model-specific methods
from bellweaver.parsers.compass import CompassParser

parser = CompassParser()
events = parser.parse_events(raw_events)
user = parser.parse_user(raw_user)
```

#### After (Generic Static Methods)

```python
# New: Generic parser with type-safe methods
from compass_client import CompassParser, CompassEvent, CompassUser

# Single generic parse method
events = CompassParser.parse(CompassEvent, raw_events)
user = CompassParser.parse(CompassUser, raw_user)

# Safe parsing with error collection
valid_events, errors = CompassParser.parse_safe(
    CompassEvent,
    raw_events,
    skip_invalid=True
)
```

### 4. Model Access Changes

#### Before

```python
from bellweaver.models.compass import CompassEvent, CompassUser

# Access fields
event.activityId  # camelCase field names
event.startDate
```

#### After

```python
from compass_client import CompassEvent, CompassUser

# Access fields (same names, cleaner imports)
event.activity_id  # snake_case field names (Pythonic)
event.start
```

**Note**: Field names may have been normalized to Python conventions (snake_case).

---

## Installation Changes

### Before

```bash
# Single package installation
cd packages/bellweaver
poetry install --with dev
```

### After

```bash
# Two-package installation

# Option 1: Install both packages explicitly
cd packages/compass-client
poetry install --with dev

cd ../bellweaver
poetry install --with dev

# Option 2: Install bellweaver only (includes compass-client via dependency)
cd packages/bellweaver
poetry install --with dev
```

### Dependency Configuration

Update `packages/bellweaver/pyproject.toml`:

```toml
[tool.poetry.dependencies]
python = "^3.11"
# ... other dependencies ...

# Add compass-client as path dependency
compass-client = {path = "../compass-client", develop = true}
```

---

## Environment Variable Changes

### Before

```bash
# .env file (old)
COMPASS_USERNAME=your_username
COMPASS_PASSWORD=your_password
COMPASS_BASE_URL=https://yourschool.compass.education
```

### After

```bash
# .env file (new)
# Add COMPASS_MODE variable
COMPASS_MODE=mock  # or "real"

# Credentials only required when COMPASS_MODE=real
COMPASS_USERNAME=your_username
COMPASS_PASSWORD=your_password
COMPASS_BASE_URL=https://yourschool.compass.education
```

**Configuration Precedence:**
1. Explicit `mode` parameter in `create_client()`
2. `COMPASS_MODE` environment variable
3. Default: `"real"`

---

## Testing Changes

### Before

```python
# tests/conftest.py (old)
import pytest
from bellweaver.adapters.compass_mock import CompassMockClient

@pytest.fixture
def compass_client():
    return CompassMockClient("", "", "")
```

### After

```python
# tests/conftest.py (new)
import pytest
import os

# Set mock mode for all tests
os.environ["COMPASS_MODE"] = "mock"

from compass_client import create_client

@pytest.fixture
def compass_client():
    # Factory automatically uses mock mode (from env var)
    return create_client(
        base_url="https://dummy.compass.education",
        username="dummy",
        password="dummy"
    )
```

### Test Execution

```bash
# Before: Tests required real credentials or mock flag
poetry run pytest

# After: Tests automatically use mock mode
poetry run pytest  # Uses mock mode via env var

# Explicitly test with real API (optional)
COMPASS_MODE=real poetry run pytest tests/integration/
```

---

## CLI Command Changes

### Before

```bash
# bellweaver CLI with built-in Compass adapter
poetry run bellweaver compass sync  # Always uses real API
```

### After

```bash
# bellweaver CLI uses compass_client package

# Use mock mode (no credentials needed)
export COMPASS_MODE=mock
poetry run bellweaver compass sync

# Use real API
export COMPASS_MODE=real
poetry run bellweaver compass sync
```

---

## Complete Migration Example

### Before: Old Code

```python
# old_app.py
from bellweaver.adapters.compass import CompassClient
from bellweaver.parsers.compass import CompassParser
from bellweaver.models.compass import CompassEvent

# Manual client setup
client = CompassClient(
    base_url="https://school.compass.education",
    username="user",
    password="pass"
)

# Authenticate
client.login()

# Fetch events
raw_events = client.get_calendar_events("2025-01-01", "2025-12-31", 100)

# Parse with instance method
parser = CompassParser()
events = parser.parse_events(raw_events)

# Use events
for event in events:
    print(f"{event.title} on {event.startDate}")
```

### After: New Code

```python
# new_app.py
import os
from compass_client import create_client, CompassParser, CompassEvent

# Factory creates appropriate client based on COMPASS_MODE env var
client = create_client(
    base_url=os.getenv("COMPASS_BASE_URL"),
    username=os.getenv("COMPASS_USERNAME"),
    password=os.getenv("COMPASS_PASSWORD")
)

# Authenticate (works with both real and mock clients)
client.login()

# Fetch events (same interface for both clients)
raw_events = client.get_calendar_events("2025-01-01", "2025-12-31", 100)

# Parse with generic static method
events = CompassParser.parse(CompassEvent, raw_events)

# Use events (same interface)
for event in events:
    print(f"{event.title} on {event.start.strftime('%Y-%m-%d')}")
```

---

## Troubleshooting

### Issue: "Module 'compass_client' not found"

**Solution:**
```bash
cd packages/compass-client
poetry install --with dev

cd ../bellweaver
poetry install --with dev
```

### Issue: "ImportError: cannot import name 'CompassClient'"

**Cause:** Still using old import paths.

**Solution:** Update imports:
```python
# ✗ OLD (remove these)
from bellweaver.adapters.compass import CompassClient

# ✓ NEW (use these)
from compass_client import create_client, CompassClient
```

### Issue: Tests failing with "Authentication failed"

**Cause:** Tests trying to use real API instead of mock mode.

**Solution:** Set `COMPASS_MODE=mock` in test fixtures:
```python
# tests/conftest.py
import os
os.environ["COMPASS_MODE"] = "mock"
```

### Issue: "ValidationError" after migration

**Cause:** Field names may have changed from camelCase to snake_case.

**Solution:** Update field accesses:
```python
# ✗ OLD
event.activityId
event.startDate

# ✓ NEW
event.activity_id
event.start
```

### Issue: Mock data files not found

**Cause:** compass-client package not properly installed.

**Solution:**
```bash
# Verify compass-client installation
cd packages/compass-client
ls -la data/mock/  # Should show compass_events.json, compass_user.json

# If missing, refresh mock data (requires real credentials)
poetry run python -m compass_client.cli refresh-mock-data \
    --base-url "$COMPASS_BASE_URL" \
    --username "$COMPASS_USERNAME" \
    --password "$COMPASS_PASSWORD"
```

---

## CI/CD Changes

### Before: GitHub Actions

```yaml
# .github/workflows/test.yml (old)
name: Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: |
          cd packages/bellweaver
          poetry install --with dev
      - name: Run tests
        run: |
          cd packages/bellweaver
          poetry run pytest
        # Required real Compass credentials as secrets
        env:
          COMPASS_USERNAME: ${{ secrets.COMPASS_USERNAME }}
          COMPASS_PASSWORD: ${{ secrets.COMPASS_PASSWORD }}
```

### After: GitHub Actions (Two Workflows)

```yaml
# .github/workflows/test-compass.yml (new - compass-client only)
name: Test Compass Client
on: [push]
jobs:
  test-compass:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: |
          cd packages/compass-client
          poetry install --with dev
      - name: Run tests (mock mode)
        run: |
          cd packages/compass-client
          poetry run pytest
        env:
          COMPASS_MODE: mock  # No credentials needed!
```

```yaml
# .github/workflows/test-bellweaver.yml (new - bellweaver only)
name: Test Bellweaver
on: [push]
jobs:
  test-bellweaver:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install compass-client
        run: |
          cd packages/compass-client
          poetry install --with dev
      - name: Install bellweaver
        run: |
          cd packages/bellweaver
          poetry install --with dev
      - name: Run tests (mock mode)
        run: |
          cd packages/bellweaver
          poetry run pytest
        env:
          COMPASS_MODE: mock  # No credentials needed!
```

**Benefits:**
- No Compass credentials required in CI
- Tests work in geo-blocked environments (e.g., GitHub Actions outside Australia)
- Independent testing of each package
- Faster CI execution (parallel jobs)

---

## Rollback Plan

If you need to temporarily revert to the old structure:

1. **Use the old branch:**
   ```bash
   git checkout main  # Or the branch before compass decoupling
   ```

2. **Keep old imports working temporarily** (not recommended for production):
   ```python
   # Create compatibility shim in bellweaver/adapters/__init__.py
   from compass_client import (
       CompassClient,
       CompassMockClient,
       CompassParser,
       CompassEvent,
       CompassUser,
   )

   __all__ = ["CompassClient", "CompassMockClient", "CompassParser", "CompassEvent", "CompassUser"]
   ```

---

## Resources

- **[compass-client README](../packages/compass-client/README.md)** - Complete package documentation
- **[bellweaver README](../packages/bellweaver/README.md)** - Integration guide
- **[Architecture Documentation](./architecture.md)** - System design details
- **[Quick Start Guide](./quick-start.md)** - Get started quickly
- **[Contracts](../specs/002-compass-api-decoupling/contracts/)** - API specifications

---

## Summary: Key Takeaways

1. **compass-client is now independent** - Can be developed and tested separately
2. **Use `create_client()` factory** - Automatically selects real vs mock mode
3. **Set `COMPASS_MODE=mock` for development** - No credentials needed
4. **Update imports to `compass_client`** - Remove `bellweaver.adapters` imports
5. **Install both packages** - compass-client first, then bellweaver
6. **CI uses mock mode by default** - No geo-blocking issues

---

**Questions or Issues?**

If you encounter problems during migration:
1. Check the troubleshooting section above
2. Review the package READMEs for detailed documentation
3. Run tests in mock mode first to isolate issues
4. Verify environment variables are set correctly

**Migration Complete?**

Once migrated, you should be able to:
- ✓ Run all tests in mock mode without credentials
- ✓ Develop locally without connecting to real Compass API
- ✓ Switch between mock and real modes via environment variable
- ✓ Use compass-client in other projects if needed
