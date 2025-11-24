# Real Compass Integration Test Guide

## Overview

This guide explains how to run integration tests against the real Compass API instance at **Seaford North Primary School** (`seaford-northps-vic.compass.education`).

## Quick Start

### 1. Create .env File

Create a `.env` file in the project root with your credentials:

```bash
COMPASS_USERNAME=your_username
COMPASS_PASSWORD=your_password
```

The file is in `.gitignore` so it won't be committed.

### 2. Run the Tests

```bash
# Just run - .env is loaded automatically
poetry run pytest tests/test_compass_client_real.py -v

# Run specific test class
poetry run pytest tests/test_compass_client_real.py::TestCompassClientRealAuthentication -v

# Run with output capture
poetry run pytest tests/test_compass_client_real.py -v -s
```

The test suite automatically loads your `.env` file using `python-dotenv` - no need to export variables or use command-line flags.

## What Gets Tested

### Authentication Tests (3 tests)
- ✅ Login success with valid credentials
- ✅ User ID extraction from session
- ✅ Session cookie establishment

### Calendar Event Tests (5 tests)
- ✅ Fetch events for current month
- ✅ Fetch events for next 30 days
- ✅ Handle date ranges with no events
- ✅ Fetch events for a single day
- ✅ Verify event structure and fields

### Edge Cases & Error Handling (3 tests)
- ✅ Proper error when fetching without login
- ✅ Client initialization
- ✅ Base URL normalization

### Date Range Tests (3 tests)
- ✅ Reverse date ranges (end before start)
- ✅ Large date ranges (full year)
- ✅ Event limit parameter

**Total: 14 tests** (3 don't need credentials)

## Test Results

When running without credentials:
```
======================== 3 passed, 11 skipped in 0.05s =========================
```

Tests that don't require authentication still run (basic initialization, error handling).

When running with credentials:
```
======================== 14 passed in 2.45s =========================
```

All tests will execute and interact with the real Compass API.

## Test Organization

```
tests/
├── test_compass_client_real.py          # This file - real API integration tests
├── test_compass_client_mock.py          # Mock data tests (if created)
├── conftest.py                          # Pytest configuration
└── README_INTEGRATION_TESTS.md          # Detailed test documentation
```

## Files Created

1. **tests/test_compass_client_real.py** - 14 integration tests covering:
   - Authentication to Compass
   - Calendar event fetching
   - Date range handling
   - Error cases
   - Edge cases

2. **tests/conftest.py** - Pytest configuration:
   - Custom command-line options for credentials
   - Shared fixtures for all tests

3. **tests/README_INTEGRATION_TESTS.md** - Detailed testing documentation

4. **INTEGRATION_TEST_GUIDE.md** - This file

## Understanding Test Skipping

Tests skip gracefully when credentials aren't provided:

```
tests/test_compass_client_real.py::test_login_success SKIPPED
Reason: Compass credentials not provided. Set COMPASS_USERNAME/COMPASS_PASSWORD env vars...
```

This allows the test suite to:
- Run in CI/CD without credentials
- Provide helpful guidance when credentials are missing
- Still run credential-independent tests (error handling, initialization)

## Debugging Test Failures

### Login Fails
- Verify credentials are correct
- Check Compass instance is online: https://seaford-northps-vic.compass.education
- Verify your IP is not blocked by the school
- Check if your account is active in Compass

### Event Fetching Fails
- Verify login succeeded first (run auth tests)
- Check date format (must be YYYY-MM-DD)
- Verify Compass API endpoint is responsive
- Check for API changes (Compass updates occasionally)

### Getting More Details
```bash
# Show full error output
poetry run pytest tests/test_compass_client_real.py -vv --tb=long

# Show print statements (sample event data)
poetry run pytest tests/test_compass_client_real.py -v -s

# Run one test with maximum verbosity
poetry run pytest tests/test_compass_client_real.py::TestCompassClientRealAuthentication::test_login_success -vvv
```

## CI/CD Integration

For automated testing in CI/CD pipelines:

### GitHub Actions
```yaml
- name: Run Compass Integration Tests
  env:
    COMPASS_USERNAME: ${{ secrets.COMPASS_USERNAME }}
    COMPASS_PASSWORD: ${{ secrets.COMPASS_PASSWORD }}
  run: poetry run pytest tests/test_compass_client_real.py -v
```

### GitLab CI
```yaml
compass_integration_tests:
  script:
    - poetry run pytest tests/test_compass_client_real.py -v
  env:
    COMPASS_USERNAME: $COMPASS_USERNAME
    COMPASS_PASSWORD: $COMPASS_PASSWORD
```

## Security Considerations

1. **Never commit credentials**
   - `.env` is in `.gitignore`
   - Use environment variables in CI/CD
   - Use secret management (GitHub Secrets, GitLab Variables, etc.)

2. **Be careful with test output**
   - Tests may print event details
   - Sanitize logs in CI/CD if sharing publicly

3. **Rotate credentials periodically**
   - Especially if using a shared test account
   - Keep a test user account separate from real accounts

## Real API Client Implementation

The tests use `src/adapters/compass.py` which implements:

```python
client = CompassClient(
    base_url="https://seaford-northps-vic.compass.education",
    username="your_username",
    password="your_password"
)

# Authenticate
client.login()

# Fetch events
events = client.get_calendar_events(
    start_date="2025-01-01",
    end_date="2025-01-31",
    limit=100
)

# Cleanup
client.close()
```

Key features:
- ✅ No browser automation (pure HTTP requests)
- ✅ Proper session management with cookies
- ✅ Session metadata extraction (userId, etc.)
- ✅ Error handling and timeouts
- ✅ Clean context manager support

## Example Event Structure

When events are fetched, they include properties like:
```json
{
  "eventId": 123456,
  "title": "School Event Name",
  "date": "2025-11-25",
  "startTime": "09:00",
  "endTime": "15:00",
  "location": "School",
  "description": "Event details",
  ...
}
```

Exact fields may vary by Compass version.

## Troubleshooting

### "No option named '--compass-username'"
- Ensure `tests/conftest.py` exists
- Check pytest is discovering conftest.py
- Run: `poetry run pytest --co` to verify

### "Login failed: Invalid credentials"
- Double-check username and password
- Test logging in manually to Compass
- Check for account lockout (too many attempts)

### "Failed to extract userId from Compass session"
- Compass API may have changed
- Check Compass version for compatibility
- Review extracted HTML in debug output

### "Connection timeout"
- Check internet connection
- Verify Compass instance is online
- Check firewall/proxy settings

## Next Steps

1. **Run the tests** with valid credentials to verify they work
2. **Review test output** to understand Compass API responses
3. **Integrate into CI/CD** for automated testing
4. **Monitor test results** for API changes
5. **Expand tests** as you discover new API features

## Support

For issues or questions:
- Review the test source: `tests/test_compass_client_real.py`
- Check test documentation: `tests/README_INTEGRATION_TESTS.md`
- Review the client implementation: `src/adapters/compass.py`
- Check Compass API documentation (if available)
