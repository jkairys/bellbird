# Compass Python Client - Architecture Overview

> **✅ Current Status**: Successfully implemented using pure Python HTTP requests. See `COMPASS_AUTHENTICATION_STRATEGIES.md` for implementation details and usage examples.

## Executive Summary

Bellbird uses a **lightweight Python client** to authenticate with Compass Education and fetch calendar events without browser automation. This approach is:
- **Fast**: ~1-2s for authentication vs ~3s for browser startup
- **Simple**: Pure Python with `requests` library
- **Low overhead**: ~10-20MB memory vs full browser footprint

## Architecture Overview

### Authentication Mechanism

Compass uses **ASP.NET forms-based authentication** with cookies for session management:

1. **GET `/login.aspx`** - Retrieve login form with ViewState
2. **Parse form** - Extract hidden fields (`__VIEWSTATE`, `__VIEWSTATEGENERATOR`, etc.)
3. **POST `/login.aspx`** - Submit credentials with all form fields
4. **Extract metadata** - Parse `organisationUserId` and `schoolConfigKey` from response HTML
5. **Maintain session** - Reuse `requests.Session()` to persist cookies

**Key insight**: Standard form-based authentication with cookie handling. No JavaScript execution required.

### Calendar API Endpoint

**Endpoint**: `POST /Services/Calendar.svc/GetCalendarEventsByUser`

**Headers**:
- `Content-Type: application/json`
- `X-Requested-With: XMLHttpRequest`

**Payload Structure**:
```json
{
  "userId": <extracted_from_session>,
  "homePage": true,
  "activityId": null,
  "locationId": null,
  "staffIds": null,
  "startDate": "YYYY-MM-DD",
  "endDate": "YYYY-MM-DD",
  "page": 1,
  "start": 0,
  "limit": 100
}
```

**Response Format**: JSON with events wrapped in `.d` property

---

## Implementation Files

All components have been implemented. See:
- **Compass Client**: `src/adapters/compass.py`
- **Mock Client**: `src/adapters/compass_mock.py`
- **Credential Manager**: `src/db/credentials.py`
- **LLM Filter**: `src/filtering/llm_filter.py`
- **Usage Guide**: `docs/COMPASS_AUTHENTICATION_STRATEGIES.md`

---

## Dependencies

```toml
requests>=2.31.0          # HTTP client with session management
beautifulsoup4>=4.12.0    # HTML parsing for form fields
cryptography>=41.0.0      # Fernet encryption for credentials
anthropic>=0.13.0         # Claude API client
sqlalchemy>=2.0.0         # ORM for database
```

---

## Advantages vs Browser Automation

| Aspect | Browser (Puppeteer) | Pure Python HTTP |
|--------|---------------------|------------------|
| **Performance** | ~3s startup | ~1-2s auth |
| **Memory** | ~200MB+ | ~10-20MB |
| **Dependencies** | Node.js + Chrome | `requests` + `beautifulsoup4` |
| **Debuggability** | Browser console | Standard HTTP logging |
| **Integration** | Subprocess/wrapper | Native Python |

---

## Known Limitations & Mitigations

### Potential Cloudflare Blocking
If Compass enables aggressive bot detection, HTTP requests may be blocked.
**Mitigation**: Realistic browser headers are used. Fallback to Puppeteer is possible if needed.

### HTML Structure Changes
Form parsing relies on ASP.NET form structure and JavaScript variable names.
**Mitigation**: Multiple extraction methods with fallback to home page fetch.

### Session Expiration
Cookies may expire during long-running sessions.
**Mitigation**: Detect 401/403 responses and re-authenticate automatically.

---

## Future Enhancements

**Not yet implemented** - potential improvements for Phase 2:

1. **Cookie Persistence** - Save session to disk to avoid re-login on restart
2. **Session Validation** - Check if session is still valid before making requests
3. **Rate Limiting** - Implement exponential backoff for failed requests
4. **Multi-user Support** - Handle multiple Compass credentials for different children/schools
