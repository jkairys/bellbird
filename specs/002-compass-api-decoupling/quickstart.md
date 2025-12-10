# Compass API Decoupling - Developer Quickstart

**Feature**: 002-compass-api-decoupling | **Date**: 2025-12-09

Get started with the decoupled Compass API infrastructure in 10 minutes!

---

## What This Feature Provides

This feature decouples the Compass API integration from the Bellweaver application by introducing:

- **`compass-client` Package**: Standalone, independently testable Compass API library
- **Mock Data Infrastructure**: Realistic sample data for development without Compass credentials
- **Dual Mode Operation**: Seamlessly switch between real Compass API and mock data
- **CI-Friendly Testing**: Run full test suite in geo-blocked environments (GitHub Actions)
- **Monorepo Structure**: Two independent Python packages with separate CI workflows

**Key Benefits**:
- Start development immediately without Compass credentials
- Run tests in CI without geo-blocking issues
- True separation of concerns (Compass logic vs. application logic)
- Future-ready for PyPI publication

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** (check with `python --version`)
- **Poetry 1.5+** (install: `curl -sSL https://install.python-poetry.org | python3 -`)
- **Git** (for cloning and branch management)
- **Optional**: Compass credentials (only needed for real API mode or refreshing mock data)

---

## Quick Setup (5 minutes)

### Step 1: Clone the Repository

```bash
# Clone the repo
git clone https://github.com/jkairys/bellweaver.git
cd bellweaver

# Switch to the feature branch
git checkout 002-compass-api-decoupling
```

### Step 2: Install compass-client Package

```bash
# Navigate to compass-client package
cd packages/compass-client

# Install dependencies (including dev dependencies)
poetry install --with dev

# Verify installation
poetry run python -c "from compass_client import create_client; print('✓ compass-client installed')"
```

**Expected output**: `✓ compass-client installed`

### Step 3: Install Bellweaver Package

```bash
# Navigate to bellweaver package
cd ../bellweaver

# Install dependencies (includes compass-client via path dependency)
poetry install --with dev

# Verify installation
poetry run python -c "from compass_client import create_client; print('✓ compass-client available in bellweaver')"
```

**Expected output**: `✓ compass-client available in bellweaver`

### Step 4: Configure for Mock Mode

```bash
# From project root
cd ../..

# Copy environment template
cp .env.example .env

# Edit .env and set mock mode
echo "COMPASS_MODE=mock" >> .env
echo "COMPASS_BASE_URL=https://dummy.compass.education" >> .env
echo "COMPASS_USERNAME=dummy" >> .env
echo "COMPASS_PASSWORD=dummy" >> .env
```

**Note**: In mock mode, the credential values don't matter (they're not used), but they're required by the interface.

### Step 5: Run Tests to Verify Setup

```bash
# Test compass-client package
cd packages/compass-client
poetry run pytest -v

# Test bellweaver package (with mock compass-client)
cd ../bellweaver
poetry run pytest -v
```

**Expected result**: All tests pass ✓

---

## Usage Examples

### Running in Mock Mode Locally

Mock mode uses realistic sample data without requiring Compass credentials.

#### Start the Application

```bash
# From project root
cd packages/bellweaver

# Set environment to mock mode
export COMPASS_MODE=mock

# Start the API server
poetry run bellweaver api serve
```

**Expected output**:
```
* Serving Flask app 'bellweaver.api'
* Running on http://127.0.0.1:5000
* Using mock Compass data
```

#### Test API Endpoints

```bash
# In a new terminal, test endpoints
curl http://localhost:5000/user
curl http://localhost:5000/events
```

**Expected result**: JSON responses with mock data matching Compass API schema.

#### Use in Python Code

```python
from compass_client import create_client, CompassParser, CompassEvent

# Create mock client (reads from environment or explicit mode)
client = create_client(
    base_url="https://dummy.compass.education",
    username="dummy",
    password="dummy",
    mode="mock"  # Or set COMPASS_MODE=mock in environment
)

# Authenticate (always succeeds in mock mode)
client.login()

# Fetch mock calendar events
raw_events = client.get_calendar_events(
    start_date="2025-12-01",
    end_date="2025-12-31",
    limit=100
)

# Parse into validated Pydantic models
events = CompassParser.parse(CompassEvent, raw_events)

# Type-safe access
for event in events:
    print(f"{event.title} on {event.start.strftime('%Y-%m-%d')}")
```

---

### Running in Real Mode (with Credentials)

Real mode connects to the actual Compass API.

#### Prerequisites

You need valid Compass credentials:
- Compass instance URL (e.g., `https://yourschool.compass.education`)
- Parent/student username
- Password

#### Configure for Real Mode

```bash
# Edit .env file
nano .env
```

Update these values:
```bash
COMPASS_MODE=real
COMPASS_BASE_URL=https://yourschool.compass.education
COMPASS_USERNAME=your_username_here
COMPASS_PASSWORD=your_password_here
```

#### Start the Application

```bash
cd packages/bellweaver
export COMPASS_MODE=real  # Or omit to use .env value
poetry run bellweaver api serve
```

**Expected output**:
```
* Serving Flask app 'bellweaver.api'
* Running on http://127.0.0.1:5000
* Using real Compass API
```

#### Test with Real Data

```bash
curl http://localhost:5000/user
curl http://localhost:5000/events
```

**Expected result**: JSON responses with your actual Compass data.

---

### Refreshing Mock Data

Update mock data with fresh samples from the real Compass API.

#### Prerequisites

- Valid Compass credentials
- Real mode environment variables configured

#### Run the Refresh Command

```bash
cd packages/compass-client

# Refresh mock data from real API
poetry run python -m compass_client.cli refresh-mock-data \
    --base-url "$COMPASS_BASE_URL" \
    --username "$COMPASS_USERNAME" \
    --password "$COMPASS_PASSWORD"
```

**Expected output**:
```
Authenticating with Compass...
Fetching user details...
Fetching calendar events...
Sanitizing PII...
Writing mock data files...
✓ Mock data refreshed successfully
  - compass_user.json
  - compass_events.json
  - schema_version.json updated
```

#### Verify Updated Mock Data

```bash
# Check schema version
cat data/mock/schema_version.json

# Verify data validates
poetry run python -c "
from compass_client import CompassMockClient, CompassParser, CompassEvent
client = CompassMockClient('', '', '')
client.login()
events = client.get_calendar_events('2025-01-01', '2025-12-31', 100)
parsed = CompassParser.parse(CompassEvent, events)
print(f'✓ {len(parsed)} events validate successfully')
"
```

#### Commit Updated Mock Data

```bash
git add data/mock/
git commit -m "chore: refresh mock data with latest API responses"
```

---

### Running Tests

#### Test compass-client Package Only

```bash
cd packages/compass-client
poetry run pytest -v

# With coverage report
poetry run pytest --cov=compass_client --cov-report=term-missing
```

#### Test Bellweaver Package Only

```bash
cd packages/bellweaver
poetry run pytest -v

# With coverage report
poetry run pytest --cov=bellweaver --cov-report=term-missing
```

#### Test Specific Module

```bash
# Test client functionality
poetry run pytest tests/unit/test_client.py -v

# Test parser
poetry run pytest tests/unit/test_parser.py -v

# Test models
poetry run pytest tests/unit/test_models.py -v
```

#### Run Integration Tests

```bash
# Integration tests (may require real API in some cases)
poetry run pytest tests/integration/ -v

# Skip integration tests that require real API
poetry run pytest -m "not integration" -v
```

---

## Common Tasks

### Switching Between Mock and Real Modes

#### Option 1: Environment Variable (Recommended)

```bash
# Use mock mode
export COMPASS_MODE=mock
poetry run bellweaver api serve

# Use real mode
export COMPASS_MODE=real
poetry run bellweaver api serve
```

#### Option 2: Update .env File

```bash
# Edit .env
nano .env

# Change COMPASS_MODE value
COMPASS_MODE=mock  # or "real"
```

#### Option 3: Explicit Parameter in Code

```python
from compass_client import create_client

# Force mock mode regardless of environment
client = create_client(
    base_url=base_url,
    username=username,
    password=password,
    mode="mock"  # Explicit override
)
```

**Configuration Precedence** (highest to lowest):
1. Explicit `mode` parameter in `create_client()`
2. `COMPASS_MODE` environment variable
3. Default value: `"real"`

---

### Running CI Locally

Simulate GitHub Actions CI environment on your local machine.

#### Install Act (GitHub Actions Local Runner)

```bash
# macOS
brew install act

# Linux
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

#### Run Bellweaver Tests Locally

```bash
# From project root
act -j test-bellweaver

# Or use Docker
docker run --rm -it \
    -v $(pwd):/workspace \
    -w /workspace \
    -e COMPASS_MODE=mock \
    python:3.11 \
    bash -c "cd packages/bellweaver && pip install poetry && poetry install --with dev && poetry run pytest"
```

#### Run compass-client Tests Locally

```bash
act -j test-compass

# Or use Docker
docker run --rm -it \
    -v $(pwd):/workspace \
    -w /workspace \
    python:3.11 \
    bash -c "cd packages/compass-client && pip install poetry && poetry install --with dev && poetry run pytest"
```

---

### Debugging Issues

#### Issue: "Module 'compass_client' not found"

**Cause**: compass-client package not installed or not in Python path.

**Solution**:
```bash
cd packages/compass-client
poetry install --with dev

# Verify installation
poetry run python -c "import compass_client; print(compass_client.__file__)"
```

#### Issue: "Authentication failed" in real mode

**Cause**: Invalid Compass credentials or network issues.

**Solution**:
```bash
# Check environment variables
echo $COMPASS_BASE_URL
echo $COMPASS_USERNAME
# Don't echo password in logs!

# Test authentication manually
cd packages/compass-client
poetry run python -c "
from compass_client import CompassClient
client = CompassClient('$COMPASS_BASE_URL', '$COMPASS_USERNAME', '$COMPASS_PASSWORD')
try:
    client.login()
    print('✓ Authentication successful')
except Exception as e:
    print(f'✗ Authentication failed: {e}')
"
```

#### Issue: Mock data files not found

**Cause**: Mock data files missing or in wrong location.

**Solution**:
```bash
# Verify mock data files exist
cd packages/compass-client
ls -la data/mock/

# Expected files:
# - compass_events.json
# - compass_user.json
# - schema_version.json

# If missing, refresh mock data (requires credentials)
poetry run python -m compass_client.cli refresh-mock-data \
    --base-url "$COMPASS_BASE_URL" \
    --username "$COMPASS_USERNAME" \
    --password "$COMPASS_PASSWORD"
```

#### Issue: Tests failing with validation errors

**Cause**: Mock data schema doesn't match Pydantic models.

**Solution**:
```bash
# Validate mock data manually
cd packages/compass-client
poetry run python -c "
from compass_client import CompassParser, CompassEvent, CompassUser
import json

# Validate events
with open('data/mock/compass_events.json') as f:
    events_data = json.load(f)
try:
    events = CompassParser.parse(CompassEvent, events_data)
    print(f'✓ {len(events)} events validate successfully')
except Exception as e:
    print(f'✗ Event validation failed: {e}')

# Validate user
with open('data/mock/compass_user.json') as f:
    user_data = json.load(f)
try:
    user = CompassParser.parse(CompassUser, user_data)
    print(f'✓ User validates successfully')
except Exception as e:
    print(f'✗ User validation failed: {e}')
"
```

#### Issue: "Mode must be 'real' or 'mock'" error

**Cause**: Invalid value for `COMPASS_MODE` environment variable.

**Solution**:
```bash
# Check current value
echo $COMPASS_MODE

# Set valid value (case-insensitive)
export COMPASS_MODE=mock  # or "real", "MOCK", "REAL"
```

#### Enable Debug Logging

```python
import logging

# Enable debug logging for compass_client
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('compass_client')
logger.setLevel(logging.DEBUG)

# Now run your code
from compass_client import create_client
client = create_client(...)
```

---

## Project Structure Quick Reference

```
bellweaver/
├── packages/
│   ├── compass-client/              # Standalone Compass API package
│   │   ├── compass_client/
│   │   │   ├── __init__.py          # Public API exports
│   │   │   ├── client.py            # Real Compass HTTP client
│   │   │   ├── mock_client.py       # Mock client with sample data
│   │   │   ├── models.py            # CompassEvent, CompassUser models
│   │   │   ├── parser.py            # Generic Pydantic parser
│   │   │   ├── factory.py           # create_client() factory
│   │   │   └── exceptions.py        # Compass-specific exceptions
│   │   ├── data/mock/               # Mock data (committed)
│   │   │   ├── compass_events.json
│   │   │   ├── compass_user.json
│   │   │   └── schema_version.json
│   │   ├── tests/                   # compass-client tests
│   │   ├── pyproject.toml           # Package dependencies
│   │   └── README.md                # Package documentation
│   │
│   └── bellweaver/                  # Main application
│       ├── bellweaver/
│       │   ├── db/                  # Database layer
│       │   ├── mappers/             # Domain mappers
│       │   ├── cli/                 # CLI commands
│       │   └── api/                 # Flask REST API
│       ├── tests/                   # Bellweaver tests
│       └── pyproject.toml           # App dependencies (includes compass-client)
│
├── .github/workflows/
│   ├── test-compass.yml             # CI for compass-client only
│   └── test-bellweaver.yml          # CI for bellweaver only
│
├── .env.example                     # Environment template
└── .env                             # Local environment (not committed)
```

---

## Next Steps

Now that you're set up, explore these resources:

### Documentation

- **[spec.md](./spec.md)** - Feature specification and user stories
- **[plan.md](./plan.md)** - Implementation plan and technical decisions
- **[data-model.md](./data-model.md)** - Complete data model reference
- **[contracts/](./contracts/)** - API contracts and schemas
  - [compass-client-api.md](./contracts/compass-client-api.md) - Public API reference
  - [client-interface.md](./contracts/client-interface.md) - Interface protocol
  - [factory-contract.md](./contracts/factory-contract.md) - Factory function spec
  - [mock-data-schema.json](./contracts/mock-data-schema.json) - Data schemas

### Development Workflow

1. **Create Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes** (preferably in mock mode for fast iteration)

3. **Run Tests**:
   ```bash
   poetry run pytest
   ```

4. **Test with Real API** (optional):
   ```bash
   export COMPASS_MODE=real
   poetry run bellweaver api serve
   ```

5. **Commit and Push**:
   ```bash
   git add .
   git commit -m "feat: your feature description"
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request** (CI will run with mock mode automatically)

### Common Development Tasks

- **Add New Compass API Endpoint**:
  1. Add method to `CompassClient` in `compass_client/client.py`
  2. Add corresponding mock in `CompassMockClient` in `compass_client/mock_client.py`
  3. Add mock data to `data/mock/` files
  4. Update tests
  5. Document in contracts

- **Update Mock Data**:
  1. Get Compass credentials
  2. Run refresh command
  3. Review sanitized data
  4. Commit to repository

- **Add New Pydantic Model**:
  1. Define model in `compass_client/models.py`
  2. Add tests in `tests/unit/test_models.py`
  3. Update parser tests
  4. Document in contracts

### Learning Resources

- **Pydantic Documentation**: https://docs.pydantic.dev/
- **Poetry Documentation**: https://python-poetry.org/docs/
- **Flask Documentation**: https://flask.palletsprojects.com/
- **Pytest Documentation**: https://docs.pytest.org/

---

## Getting Help

If you encounter issues:

1. **Check this quickstart** for common tasks and debugging
2. **Review the contracts** for API specifications
3. **Check existing tests** for usage examples
4. **Run in debug mode** with logging enabled
5. **Ask for help** in the project chat/issues

---

## Tips for Success

- **Start in mock mode** for fast development iteration
- **Run tests frequently** to catch issues early
- **Use type hints** and let your IDE help you
- **Validate mock data** after refreshing to catch schema drift
- **Keep mock data realistic** but sanitize PII
- **Test both modes** before committing (if you have credentials)
- **Review contracts** when integrating compass-client

---

## Summary: From Zero to Running in 5 Commands

```bash
# 1. Clone and checkout branch
git clone https://github.com/jkairys/bellweaver.git && cd bellweaver
git checkout 002-compass-api-decoupling

# 2. Install compass-client
cd packages/compass-client && poetry install --with dev

# 3. Install bellweaver
cd ../bellweaver && poetry install --with dev

# 4. Configure mock mode
cd ../.. && cp .env.example .env && echo "COMPASS_MODE=mock" >> .env

# 5. Run tests to verify
cd packages/bellweaver && poetry run pytest -v
```

**Expected result**: All tests pass, you're ready to develop! 🚀

---

## Document Metadata

- **Created**: 2025-12-09
- **Feature**: 002-compass-api-decoupling
- **Author**: Claude Code
- **Related Documents**:
  - [spec.md](./spec.md) - Feature specification
  - [plan.md](./plan.md) - Implementation plan
  - [data-model.md](./data-model.md) - Data model
  - [contracts/](./contracts/) - API contracts
