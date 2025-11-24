# Compass Integration Tests

This directory contains integration tests for the real Compass API client.

## Real Compass Client Tests

`test_compass_client_real.py` contains tests that interact with a live Compass instance (Seaford North Primary School).

### Prerequisites

You need valid Compass credentials for the Seaford North Primary School instance.

### Running the Tests

#### Recommended: .env File (Automatic)

Create a `.env` file in the project root (it's in `.gitignore`):

```bash
COMPASS_USERNAME=your_username
COMPASS_PASSWORD=your_password
```

Then just run the tests - `.env` is loaded automatically:

```bash
poetry run pytest tests/test_compass_client_real.py -v
```

The test suite automatically loads environment variables from `.env` using `python-dotenv`. No need to `export` variables or use command-line flags.

#### Alternative: Export Environment Variables

If you prefer to set environment variables directly:

```bash
export COMPASS_USERNAME=your_username
export COMPASS_PASSWORD=your_password
poetry run pytest tests/test_compass_client_real.py -v
```

#### Alternative: Command-Line Arguments

Pass credentials via pytest flags:

```bash
poetry run pytest tests/test_compass_client_real.py -v \
  --compass-username=your_username \
  --compass-password=your_password
```

### What Tests Are Included

#### Authentication Tests
- `test_login_success` - Verifies successful login to Compass
- `test_user_id_extracted_after_login` - Checks that userId is extracted from response
- `test_session_established` - Verifies session cookies are created

#### Calendar Event Tests
- `test_fetch_calendar_events_current_month` - Fetches events for current month
- `test_fetch_calendar_events_next_30_days` - Fetches next 30 days of events
- `test_fetch_calendar_events_empty_range` - Handles date ranges with no events
- `test_fetch_calendar_events_single_day` - Fetches events for a specific day
- `test_calendar_events_has_expected_fields` - Inspects event structure

#### Edge Cases & Error Handling
- `test_fetch_events_without_login_fails` - Verifies proper error when not authenticated
- `test_client_initialization` - Tests basic client setup
- `test_base_url_trailing_slash_handling` - Handles URL normalization

#### Date Range Tests
- `test_fetch_events_reverse_date_range` - Tests with end_date before start_date
- `test_fetch_events_large_date_range` - Tests querying a full year
- `test_fetch_events_with_limit` - Tests event limit parameter

### Skipping Tests

If credentials are not provided, tests will skip with a helpful message:

```
tests/test_compass_client_real.py::test_login_success SKIPPED
Compass credentials not provided. Set COMPASS_USERNAME/COMPASS_PASSWORD env vars or use --compass-username and --compass-password flags
```

### Interpreting Results

Tests that pass indicate:
- ✅ Authentication is working
- ✅ The Compass API is responding
- ✅ Calendar events are being returned
- ✅ Date ranges are being handled correctly

If tests fail:
- Check your credentials are correct
- Verify the Compass instance is accessible (https://seaford-northps-vic.compass.education)
- Check for any Compass API changes
- Review the error message for API-specific issues

### Sample Output

When running with credentials, you'll see output like:

```
tests/test_compass_client_real.py::TestCompassClientRealAuthentication::test_login_success PASSED
tests/test_compass_client_real.py::TestCompassClientRealAuthentication::test_user_id_extracted_after_login PASSED
tests/test_compass_client_real.py::TestCompassClientRealCalendarEvents::test_fetch_calendar_events_current_month PASSED

Sample event structure: {'eventId': 123456, 'title': 'School Event', 'date': '2025-11-25', ...}
```

### Running Only Authentication Tests

```bash
poetry run pytest tests/test_compass_client_real.py::TestCompassClientRealAuthentication -v \
  --compass-username=your_username \
  --compass-password=your_password
```

### Running Only Calendar Event Tests

```bash
poetry run pytest tests/test_compass_client_real.py::TestCompassClientRealCalendarEvents -v \
  --compass-username=your_username \
  --compass-password=your_password
```

### Debugging Individual Tests

To get more detail on a specific test:

```bash
poetry run pytest tests/test_compass_client_real.py::TestCompassClientRealCalendarEvents::test_fetch_calendar_events_next_30_days -vv -s \
  --compass-username=your_username \
  --compass-password=your_password
```

The `-s` flag shows print output, which includes event structure details.

## Other Tests

- `test_compass_client_mock.py` - Tests using mock/synthetic Compass data (no credentials needed)
- `test_*.py` - Other unit tests for database, filtering, etc.

## Environment Variables

The test suite respects these environment variables:

- `COMPASS_USERNAME` - Compass login username
- `COMPASS_PASSWORD` - Compass login password
- `COMPASS_BASE_URL` - Override the base URL (defaults to Seaford North)

## Security Note

Never commit your credentials. The `.env` file is in `.gitignore` to prevent accidental credential commits.

If you need to store credentials for CI/CD, use secret management appropriate for your platform (GitHub Secrets, GitLab CI Variables, etc.).
