# Compass Authentication Strategy

## Current Implementation

We successfully use **Puppeteer (via Node.js)** for browser automation to authenticate with Compass Education. The implementation handles:
- Cloudflare bot detection
- ASP.NET forms-based authentication
- Session management and cookie handling
- Calendar event retrieval

## Implementation: Puppeteer with Stealth Plugin

### Approach
- Uses Puppeteer (Node.js headless browser) with puppeteer-extra-plugin-stealth
- Successfully bypasses Cloudflare bot detection
- Handles JavaScript execution and session management
- Maintains authenticated browser context for API calls

### Key Success Factors
- **Stealth Plugin**: Masks automation characteristics from bot detection
- **Session Initialization**: Calls `getAllLocations()` and `getUserDetails()` after login
- **Browser Context**: Maintains full browser state between requests
- **Proven Working**: Based on heheleo/compass-education reference implementation

### Current Status
✅ **Working** - Successfully authenticates and retrieves calendar events in headless mode

### Trade-offs
**Pros:**
- ✅ Reliable authentication (proven in production use)
- ✅ Handles Cloudflare and JavaScript challenges
- ✅ Same approach as reference implementation
- ✅ Works in headless mode

**Cons:**
- ❌ Requires Node.js runtime alongside Python
- ❌ Higher memory usage (~200MB+ for browser)
- ❌ Slower than pure HTTP (~10-15 seconds for login)
- ❌ More complex deployment

## Alternative Approaches Considered

### Pure HTTP Requests (Not Recommended)
Attempted but blocked by Cloudflare bot detection. While faster and simpler, Compass's security measures prevent reliable automated HTTP-only authentication.

### User-Managed Sessions
Users log in manually and export cookies for the app to use. Viable for production but adds user friction.

## Usage

### Using the CompassClient (Puppeteer-based)

```python
from src.adapters.compass import CompassClient

client = CompassClient(
    base_url="https://seaford-northps-vic.compass.education",
    username="your_username",
    password="your_password"
)

# Authenticate
client.login()

# Fetch calendar events
events = client.get_calendar_events("2025-01-01", "2025-01-31")

# Clean up
client.close()
```

### Using Mock Data for Development

```python
from src.adapters.compass_mock import CompassMockClient

client = CompassMockClient()
events = client.get_calendar_events("2025-01-01", "2025-01-31")
# Returns realistic synthetic test events
```

## Next Steps: Optimizing Authentication

The current implementation works but logs in on every request. **Priority improvements:**

1. **Session Persistence** - Reuse authenticated browser context across requests
2. **Cookie Caching** - Store and reuse session cookies to avoid repeated logins
3. **Session Refresh** - Detect expired sessions and re-authenticate only when needed

These optimizations will reduce login overhead from ~10-15s per request to near-instant for subsequent requests.

## Testing

```bash
# Test with mock data (no credentials needed)
poetry run pytest tests/test_compass_client_mock.py -v

# Test with real Compass (requires .env with credentials)
poetry run pytest tests/test_compass_client_real.py -v
```

## File References

- **Main Implementation:** `src/adapters/compass.py`
- **Mock Client:** `src/adapters/compass_mock.py`
- **Real API Tests:** `tests/test_compass_client_real.py`
- **Mock Tests:** `tests/test_compass_client_mock.py`

## Conclusion

Puppeteer with the stealth plugin successfully authenticates with Compass Education. The next priority is optimizing session management to avoid repetitive logins and improve performance.
