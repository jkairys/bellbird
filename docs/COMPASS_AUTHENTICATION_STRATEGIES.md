# Compass Authentication Strategy

> **Project**: Bellweaver

## Current Implementation

We successfully use **Pure Python HTTP Requests** to authenticate with Compass Education. The implementation handles:
- ASP.NET forms-based authentication with ViewState
- Session management via `requests.Session()` with cookie handling
- Realistic browser headers to avoid blocking
- Calendar event retrieval via JSON API

## Implementation: Python requests + BeautifulSoup

### Approach
- Uses Python `requests` library with persistent session
- Parses ASP.NET login form to extract ViewState and hidden fields
- Submits form-based authentication with proper headers
- Extracts session metadata (userId, schoolConfigKey) from response HTML
- Maintains authenticated session for subsequent API calls

### Key Success Factors
- **Form Parsing**: Extracts all ASP.NET hidden fields (`__VIEWSTATE`, `__VIEWSTATEGENERATOR`, etc.)
- **Realistic Headers**: Mimics Chrome browser to avoid bot detection
- **Session Persistence**: Reuses `requests.Session()` to maintain cookies
- **Metadata Extraction**: Parses `organisationUserId` and `schoolConfigKey` from JavaScript in HTML
- **Error Handling**: Detects failed login by checking if redirected away from `login.aspx`

### Current Status
✅ **Working** - Successfully authenticates and retrieves calendar events without browser automation

### Trade-offs
**Pros:**
- ✅ Pure Python - no Node.js dependency
- ✅ Low memory footprint (~10-20MB)
- ✅ Fast authentication (~1-2 seconds for login)
- ✅ Simple deployment (single runtime)
- ✅ Easy to debug with standard HTTP tools

**Cons:**
- ⚠️ May be blocked if Cloudflare bot detection is enabled
- ⚠️ Relies on parsing HTML structure (may break with UI changes)
- ⚠️ Requires realistic browser headers

## Alternative Approaches Considered

### Puppeteer with Stealth Plugin (Fallback Option)
Browser automation approach using Node.js and Puppeteer. More robust against Cloudflare but requires additional runtime and higher resource usage. Can be implemented if HTTP approach is blocked.

### User-Managed Sessions
Users log in manually and export cookies for the app to use. Viable for production but adds user friction.

## Usage Examples

### Basic Usage - Real Compass Client

```python
from src.adapters.compass import CompassClient
from datetime import datetime, timedelta

# Initialize with your Compass instance
client = CompassClient(
    base_url="https://seaford-northps-vic.compass.education",
    username="your_username",
    password="your_password"
)

try:
    # Authenticate
    client.login()
    print("✓ Authenticated with Compass")

    # Fetch events for next 2 weeks
    start = datetime.now().strftime("%Y-%m-%d")
    end = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

    events = client.get_calendar_events(start, end)
    print(f"Retrieved {len(events)} events")

    # Process events
    for event in events:
        print(f"  • {event['longTitle']}")
        print(f"    Start: {event['start']}")

finally:
    client.close()
```

### Using Mock Data for Development

```python
from src.adapters.compass_mock import CompassMockClient
from datetime import datetime, timedelta

# Initialize with mock credentials (not validated)
client = CompassMockClient(
    base_url="https://example.compass.education",
    username="mock_user",
    password="mock_pass"
)

# Login always succeeds
client.login()

# Fetch synthetic events
start = datetime.now().strftime("%Y-%m-%d")
end = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
events = client.get_calendar_events(start, end)

# Process events (same interface as real client)
for event in events:
    print(f"{event['longTitle']} on {event['start']}")

client.close()
```

### Complete Pipeline Example

```python
from src.adapters.compass import CompassClient
from src.filtering.llm_filter import LLMFilter
from datetime import datetime, timedelta
import os

# 1. Fetch events from Compass
client = CompassClient(
    base_url="https://your-compass.edu.au",
    username="your_username",
    password="your_password"
)
client.login()

start = datetime.now().strftime("%Y-%m-%d")
end = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
raw_events = client.get_calendar_events(start, end)
client.close()

print(f"Fetched {len(raw_events)} raw events")

# 2. Filter with Claude
llm_filter = LLMFilter(api_key=os.getenv('CLAUDE_API_KEY'))

user_config = {
    'child_name': 'Emma',
    'year_level': 'Year 3',
    'interests': ['music', 'sports'],
    'filter_rules': 'Include Year 3 events and whole-school events.'
}

filtered = llm_filter.filter_events(raw_events, user_config)

# 3. Display relevant events
for result in filtered:
    if result.get('is_relevant'):
        print(f"\n✓ {result['title']}")
        print(f"  {result['reason']}")
```

## Implementation Details

### Authentication Flow

1. **GET `/login.aspx`**: Retrieve login form HTML
2. **Parse Form**: Extract ASP.NET ViewState and all hidden fields using BeautifulSoup
3. **POST `/login.aspx`**: Submit credentials with all form fields
4. **Verify Success**: Check that response URL is not `login.aspx` (successful login redirects)
5. **Extract Metadata**: Parse `organisationUserId` and `schoolConfigKey` from response HTML
6. **Fallback Fetch**: If metadata not found, GET `/home.aspx` and parse again

### API Request Flow

1. **Ensure Metadata**: Call `_ensure_session_metadata()` to get `userId` if needed
2. **POST `/Services/Calendar.svc/GetCalendarEventsByUser`**: Request calendar events
3. **Headers**: Include `Content-Type: application/json` and `X-Requested-With: XMLHttpRequest`
4. **Parse Response**: Extract events from `.d` property in JSON response

### Session Management

The current implementation uses `requests.Session()` which:
- Automatically handles cookies between requests
- Maintains session state for the lifetime of the client object
- Closes cleanly with `client.close()`

**Future Optimization**: Session persistence across client instances (pickle cookies to disk) could eliminate repeated logins when reusing credentials.

## Next Steps: Potential Improvements

1. **Cookie Persistence** - Save session cookies to disk to reuse across program runs
2. **Session Validation** - Check if existing session is still valid before re-authenticating
3. **Cloudflare Handling** - Implement fallback to browser automation if HTTP requests are blocked
4. **Rate Limiting** - Add exponential backoff for failed requests

## Testing

### Using Test Fixtures

For unit tests that need sample Compass data without making API calls:

```python
from tests.fixtures import load_compass_sample_events

# Load sanitized sample events (safe for version control)
sample_events = load_compass_sample_events()

# Use in tests
assert len(sample_events) == 5
assert sample_events[0]['longTitle'] == "10:00: Year 1 Generalist"
```

### Collecting Fresh Mock Data

To collect new mock data from a live Compass instance (requires credentials):

```bash
# Collect real events and save to data/mock/ (git-ignored)
poetry run python scripts/collect_mock_data.py
```

This script:
1. Authenticates with Compass using `.env` credentials
2. Fetches calendar events for the next 30 days
3. Saves raw response to `data/mock/compass_events_raw.json`
4. Saves sanitized version to `data/mock/compass_events_sanitized.json`
5. Creates metadata file with collection details

**Note**: Files in `data/mock/` are git-ignored. Only curated fixtures in `tests/fixtures/` should be committed.

### Running Tests

```bash
# Test with mock data (no credentials needed)
poetry run pytest tests/test_compass_client_mock.py -v

# Test with real Compass (requires .env with credentials)
poetry run pytest tests/test_compass_client_real.py -v
```

## File References

- **Main Implementation:** `src/adapters/compass.py`
- **Mock Client:** `src/adapters/compass_mock.py`
- **Real API Tests:** `tests/test_compass_client_real.py` (if exists)
- **Mock Tests:** `tests/test_compass_client_mock.py` (if exists)

## API Reference

### `CompassClient` (src/adapters/compass.py)

**Constructor:**
```python
CompassClient(base_url: str, username: str, password: str)
```

**Public Methods:**
- `login() -> bool`: Authenticate with Compass (raises exception on failure)
- `get_calendar_events(start_date: str, end_date: str, limit: int = 100) -> List[Dict[str, Any]]`: Fetch calendar events
- `close() -> None`: Close the session

**Private Methods:**
- `_setup_session_headers() -> None`: Configure realistic browser headers
- `_extract_form_fields(html_content: str) -> Dict[str, str]`: Parse ASP.NET form fields
- `_extract_session_metadata(html_content: str) -> None`: Parse userId and schoolConfigKey from HTML
- `_ensure_session_metadata() -> None`: Fetch metadata if not already available

**Attributes:**
- `base_url`: Compass instance URL
- `session`: `requests.Session()` object with cookies
- `user_id`: Extracted organisation user ID (needed for API calls)
- `school_config_key`: School configuration key (optional)
- `_authenticated`: Boolean flag indicating login status

### `CompassMockClient` (src/adapters/compass_mock.py)

**Constructor:**
```python
CompassMockClient(base_url: str, username: str, password: str)
```

**Public Methods:**
- `login() -> bool`: Always returns True
- `get_calendar_events(start_date: str, end_date: str, limit: int = 100) -> List[Dict[str, Any]]`: Returns synthetic events
- `close() -> None`: No-op

**Mock Data:**
Returns 6 synthetic events including:
- Year 3 Excursion to Taronga Zoo
- Year 3 Music Performance
- Free Dress Day
- Year 2-3 Sports Carnival
- Whole School Assembly
- Year 4 Museum Excursion

## Conclusion

Pure Python HTTP authentication successfully works with Compass Education using form-based login and session management. The implementation is fast, lightweight, and doesn't require browser automation. If Cloudflare bot detection becomes an issue in production, the architecture supports adding a Puppeteer fallback without changing the interface.
