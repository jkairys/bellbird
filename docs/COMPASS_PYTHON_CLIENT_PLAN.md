# Compass Python Client Implementation Plan

> **⚠️ Historical Document**: This is the original design from November 2025. The actual implementation uses Puppeteer (Node.js) for browser automation instead of pure HTTP requests. See `COMPASS_AUTHENTICATION_STRATEGIES.md` for the current working approach.

## Executive Summary

The `heheleo/compass-education` library uses Puppeteer (browser automation) to handle authentication and make API calls to Compass. **This adds significant complexity**: spinning up a headless browser, managing its lifecycle, and executing code within the browser context.

**Our approach**: Implement a lightweight Python client that mimics the JS library's authentication and API calls **without the browser overhead**. This is feasible because:
1. Compass uses standard HTTP/cookie-based authentication (not OAuth or complex protocols)
2. The API is a simple REST endpoint (POST to `Services/Calendar.svc/GetCalendarEventsByUser`)
3. The `schoolConfigKey` can be extracted from the login response

**Complexity trade-off**: Low-level implementation vs. JS library dependency
- **JS approach**: Depend on heheleo library + Puppeteer + browser management (complex, non-Python)
- **Python approach**: Implement auth + API calls in Python (straightforward, native)

**Recommendation**: Implement native Python client. It's simpler, faster, and more maintainable for this use case.

---

## Compass Authentication Mechanism

### How the JS Library Works

The `compass-education` library uses this flow:

1. **Puppeteer initialization**: Launches headless Chrome with stealth plugin
2. **Navigate to login**: Goes to `https://{baseURL}/login.aspx?sessionstate=disabled`
3. **Fill form**: Enters username/password via CSS selectors
4. **Submit & wait**: Clicks login button, waits for navigation
5. **Extract cookies**: Grabs all cookies from the browser session
6. **Store cookies**: Keeps cookies in the client, uses them for all subsequent API calls
7. **Extract session keys**: Grabs `window.Compass.organisationUserId` and `window.Compass.referenceDataCacheKeys.schoolConfigKey` from the page

### Python Implementation Strategy

Instead of browser automation, we'll use HTTP requests with proper cookie handling:

1. **POST login form** to `https://{baseURL}/login.aspx` with username/password
2. **Capture cookies** from the response (standard HTTP Set-Cookie headers)
3. **Extract session metadata** from the HTML response (parse page for schoolConfigKey if needed)
4. **Reuse cookies** for all subsequent API calls via `requests.Session()`

**Key insight**: The Compass server validates credentials via standard form submission and returns cookies. No JavaScript execution needed.

---

## Implementation Plan

### Part 1: Authentication (`src/adapters/compass.py`)

```python
import requests
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from cryptography.fernet import Fernet

class CompassClient:
    """
    Python client for Compass Education API.

    Handles authentication and calendar event fetching without browser automation.
    """

    def __init__(self, base_url: str, username: str, password: str):
        """
        Initialize Compass client.

        Args:
            base_url: Base URL of Compass instance (e.g., "https://compass.example.com")
            username: Compass username
            password: Compass password
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.user_id: Optional[int] = None
        self.school_config_key: Optional[str] = None
        self._authenticated = False

    def login(self) -> bool:
        """
        Authenticate with Compass by submitting login form.

        Returns:
            True if successful, raises exception otherwise
        """
        login_url = f"{self.base_url}/login.aspx?sessionstate=disabled"

        # Prepare credentials
        data = {
            'username': self.username,
            'password': self.password
        }

        try:
            # POST login form
            response = self.session.post(
                login_url,
                data=data,
                allow_redirects=True,
                timeout=10
            )
            response.raise_for_status()

            # Verify login was successful
            # Compass redirects to home page or returns auth cookie
            if 'Set-Cookie' not in response.headers and response.status_code != 200:
                raise Exception("Login failed: Invalid credentials or server error")

            # Try to extract userId and schoolConfigKey from the response
            # These may be in JavaScript or HTML meta tags
            self._extract_session_metadata(response.text)

            self._authenticated = True
            return True

        except requests.RequestException as e:
            raise Exception(f"Login request failed: {e}")

    def _extract_session_metadata(self, html_content: str) -> None:
        """
        Extract userId and schoolConfigKey from HTML response.

        These are usually embedded in JavaScript or window object.
        We'll look for them in the initial page load response.
        """
        # Look for patterns like: window.Compass.organisationUserId = 12345
        # or data attributes containing session info

        import re

        # Try to find userId in JavaScript
        user_id_match = re.search(r'organisationUserId["\']?\s*[:=]\s*(\d+)', html_content)
        if user_id_match:
            self.user_id = int(user_id_match.group(1))

        # Try to find schoolConfigKey
        key_match = re.search(r'schoolConfigKey["\']?\s*[:=]\s*["\']([^"\']+)["\']', html_content)
        if key_match:
            self.school_config_key = key_match.group(1)

        # If extraction failed, we can fetch these on first API call

    def _ensure_session_metadata(self) -> None:
        """
        Fetch session metadata if not already extracted.

        Makes a request to the home page or an API endpoint to get
        userId and schoolConfigKey if they weren't available after login.
        """
        if self.user_id is None:
            # Fallback: fetch home page and parse again
            response = self.session.get(f"{self.base_url}/home.aspx", timeout=10)
            self._extract_session_metadata(response.text)

        if self.user_id is None:
            raise Exception("Failed to extract userId from Compass session")

    def get_calendar_events(
        self,
        start_date: str,  # YYYY-MM-DD
        end_date: str,    # YYYY-MM-DD
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetch calendar events from Compass for a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Maximum number of events to return (default 100)

        Returns:
            List of calendar event dictionaries
        """
        if not self._authenticated:
            raise Exception("Not authenticated. Call login() first.")

        # Ensure we have the userId
        self._ensure_session_metadata()

        # Build the API request
        api_url = (
            f"{self.base_url}/Services/Calendar.svc/GetCalendarEventsByUser"
            "?sessionstate=readonly&ExcludeNonRelevantPd=true"
        )

        payload = {
            'userId': self.user_id,
            'homePage': True,
            'activityId': None,
            'locationId': None,
            'staffIds': None,
            'startDate': start_date,
            'endDate': end_date,
            'page': 1,
            'start': 0,
            'limit': limit
        }

        try:
            response = self.session.post(
                api_url,
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                timeout=10
            )
            response.raise_for_status()

            # Parse response - Compass wraps result in .d property
            data = response.json()

            # Extract actual events from response
            if isinstance(data, dict) and 'd' in data:
                events = data['d']
            else:
                events = data

            return events if isinstance(events, list) else []

        except requests.RequestException as e:
            raise Exception(f"Failed to fetch calendar events: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response from Compass: {e}")

    def close(self) -> None:
        """Close the session."""
        self.session.close()
```

### Part 2: Database Integration (`src/db/credentials.py`)

Store and retrieve encrypted credentials:

```python
import os
import json
from cryptography.fernet import Fernet
from typing import Optional

class CredentialManager:
    """
    Manage encrypted credential storage in SQLite.
    """

    def __init__(self, db_session, encryption_key: Optional[str] = None):
        self.db_session = db_session
        self.cipher = self._init_cipher(encryption_key)

    def _init_cipher(self, encryption_key: Optional[str]) -> Fernet:
        """Initialize Fernet cipher with key."""
        if encryption_key is None:
            encryption_key = os.getenv('BELLBIRD_ENCRYPTION_KEY')

        if encryption_key is None:
            # Generate new key and save to .env
            key = Fernet.generate_key().decode()
            print(f"Generated encryption key: {key}")
            print("Save this to .env as BELLBIRD_ENCRYPTION_KEY")
            encryption_key = key

        return Fernet(encryption_key.encode())

    def save_compass_credentials(self, username: str, password: str) -> None:
        """Encrypt and store Compass credentials."""
        encrypted_password = self.cipher.encrypt(password.encode()).decode()

        # Store in database (replace if exists)
        from src.db.models import Credential

        cred = self.db_session.query(Credential).filter_by(source='compass').first()
        if cred:
            cred.username = username
            cred.password_encrypted = encrypted_password
        else:
            cred = Credential(
                source='compass',
                username=username,
                password_encrypted=encrypted_password
            )
            self.db_session.add(cred)

        self.db_session.commit()

    def load_compass_credentials(self) -> Optional[tuple[str, str]]:
        """Load and decrypt Compass credentials."""
        from src.db.models import Credential

        cred = self.db_session.query(Credential).filter_by(source='compass').first()
        if not cred:
            return None

        decrypted_password = self.cipher.decrypt(cred.password_encrypted.encode()).decode()
        return (cred.username, decrypted_password)
```

### Part 3: Mock Adapter for Early Testing (`src/adapters/compass_mock.py`)

```python
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json

class CompassMockClient:
    """
    Mock Compass client for testing without real credentials.
    Returns synthetic but realistic calendar events.
    """

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.user_id = 12345
        self._authenticated = False

    def login(self) -> bool:
        """Mock login - always succeeds."""
        self._authenticated = True
        return True

    def get_calendar_events(
        self,
        start_date: str,
        end_date: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Return synthetic calendar events for testing.

        Includes:
        - Excursions
        - Performances
        - Sports days
        - Assemblies
        - Free dress days
        - Permission slips
        - Mixed year levels
        """
        if not self._authenticated:
            raise Exception("Not authenticated")

        # Parse dates
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        # Generate synthetic events
        events = [
            {
                'id': '1',
                'longTitle': 'Year 3 Excursion to Taronga Zoo',
                'longTitleWithoutTime': 'Year 3 Excursion to Taronga Zoo',
                'start': (start + timedelta(days=5)).isoformat(),
                'finish': (start + timedelta(days=5, hours=3)).isoformat(),
                'allDay': False,
                'subjectTitle': 'Excursion',
                'subjectLongName': 'Excursion',
                'locations': [{'name': 'Taronga Zoo'}],
                'managers': [{'name': 'Mrs Smith'}],
                'rollMarked': False,
                'description': 'Permission slip required. Cost: $25'
            },
            {
                'id': '2',
                'longTitle': 'Year 3 Music Performance',
                'longTitleWithoutTime': 'Year 3 Music Performance',
                'start': (start + timedelta(days=10)).isoformat(),
                'finish': (start + timedelta(days=10, hours=1)).isoformat(),
                'allDay': False,
                'subjectTitle': 'Music',
                'subjectLongName': 'Music Performance',
                'locations': [{'name': 'School Hall'}],
                'managers': [{'name': 'Mr Johnson'}],
                'rollMarked': False,
                'description': 'Evening performance. Tickets available online.'
            },
            {
                'id': '3',
                'longTitle': 'Free Dress Day - Community Fund',
                'longTitleWithoutTime': 'Free Dress Day',
                'start': (start + timedelta(days=3)).isoformat(),
                'finish': (start + timedelta(days=3)).isoformat(),
                'allDay': True,
                'subjectTitle': 'Event',
                'subjectLongName': 'Free Dress Day',
                'locations': [{'name': 'School'}],
                'managers': [{'name': 'Principal'}],
                'rollMarked': False,
                'description': 'Wear your favorite outfit. Gold coin donation.'
            },
            {
                'id': '4',
                'longTitle': 'Year 2-3 Sports Carnival',
                'longTitleWithoutTime': 'Year 2-3 Sports Carnival',
                'start': (start + timedelta(days=7)).isoformat(),
                'finish': (start + timedelta(days=7, hours=4)).isoformat(),
                'allDay': False,
                'subjectTitle': 'Sports',
                'subjectLongName': 'Sports Carnival',
                'locations': [{'name': 'School Oval'}],
                'managers': [{'name': 'PE Department'}],
                'rollMarked': True,
                'description': 'House colors provided. Parents welcome to attend.'
            },
            {
                'id': '5',
                'longTitle': 'Whole School Assembly',
                'longTitleWithoutTime': 'Whole School Assembly',
                'start': (start + timedelta(days=2)).isoformat(),
                'finish': (start + timedelta(days=2, hours=1)).isoformat(),
                'allDay': False,
                'subjectTitle': 'Assembly',
                'subjectLongName': 'Whole School Assembly',
                'locations': [{'name': 'School Hall'}],
                'managers': [{'name': 'Principal'}],
                'rollMarked': True,
                'description': 'General announcements and awards.'
            },
            {
                'id': '6',
                'longTitle': 'Year 4 Excursion - Museum Visit',
                'longTitleWithoutTime': 'Year 4 Excursion - Museum Visit',
                'start': (start + timedelta(days=8)).isoformat(),
                'finish': (start + timedelta(days=8, hours=3)).isoformat(),
                'allDay': False,
                'subjectTitle': 'Excursion',
                'subjectLongName': 'Excursion',
                'locations': [{'name': 'State Museum'}],
                'managers': [{'name': 'Mrs Davis'}],
                'rollMarked': False,
                'description': 'Year 4 only. Permission slip due by Friday.'
            },
        ]

        # Filter by date range and limit
        filtered = [e for e in events if start <= datetime.fromisoformat(e['start']) <= end]
        return filtered[:limit]

    def close(self) -> None:
        """Mock close."""
        pass
```

### Part 4: Filtering Logic (`src/filtering/llm_filter.py`)

```python
import json
from typing import List, Dict, Any
import anthropic

class LLMFilter:
    """
    Filter calendar events using Claude API.
    """

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def filter_events(
        self,
        events: List[Dict[str, Any]],
        user_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Filter events based on user configuration using Claude.

        Args:
            events: List of raw calendar events from Compass
            user_config: User configuration (child, school, filter rules)

        Returns:
            Dictionary with filtered events and reasoning
        """

        # Build prompt
        prompt = self._build_prompt(events, user_config)

        # Call Claude
        message = self.client.messages.create(
            model="claude-opus-4-1-20250805",
            max_tokens=2048,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Parse response
        response_text = message.content[0].text

        # Try to parse JSON from response
        try:
            # Look for JSON block in response
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(1))
            else:
                result = json.loads(response_text)
        except json.JSONDecodeError:
            # If parsing fails, return raw response
            result = {"raw_response": response_text, "events": []}

        return result

    def _build_prompt(
        self,
        events: List[Dict[str, Any]],
        user_config: Dict[str, Any]
    ) -> str:
        """Build Claude prompt for filtering events."""

        return f"""
You are helping a parent filter school calendar events to find only the relevant ones for their child.

## Child Profile
- Name: {user_config.get('child_name', 'Unknown')}
- School: {user_config.get('school', 'Unknown')}
- Year Level: {user_config.get('year_level', 'Unknown')}
- Class: {user_config.get('class', 'Unknown')}
- Interests: {', '.join(user_config.get('interests', []))}

## Filtering Rules
{user_config.get('filter_rules', 'No specific rules provided. Include events relevant to the child.')}

## Calendar Events
Below are all calendar events for the next 2 weeks. Evaluate each one and determine if it's relevant to the child based on the profile and rules above.

{json.dumps(events, indent=2, default=str)}

## Task
For each event, provide:
1. Whether it's RELEVANT or NOT_RELEVANT to this child
2. Why (reasoning)
3. Any action needed (e.g., "Permission slip required", "Cost: $25")

Return your response as a JSON array with this structure:
```json
[
  {{
    "event_id": "event_id_from_input",
    "title": "event title",
    "date": "event date",
    "is_relevant": true/false,
    "reason": "explanation of relevance",
    "action_needed": "description of any action or null"
  }}
]
```
"""
```

---

## Implementation Dependencies

### Python Packages

```
requests>=2.31.0          # HTTP requests
cryptography>=41.0.0      # Fernet encryption
anthropic>=0.13.0         # Claude API
sqlalchemy>=2.0.0         # ORM
flask>=3.0.0              # Web framework
```

### No External Services Required

Unlike the JS library, this approach doesn't require:
- Puppeteer/headless browser
- Node.js runtime
- Browser automation complexity
- Stealth plugins or workarounds

---

## Testing Strategy

### Phase 1 (Days 1-2): Mock-Only
- Use `CompassMockClient` exclusively
- Test `LLMFilter` with synthetic events
- Verify CLI pipeline works
- Iterate on filter prompts

### Phase 2 (Days 3-4): Real Compass
- Replace mock with real `CompassClient`
- Test login with real credentials (stored encrypted)
- Fetch real calendar events
- Debug any API quirks or data differences

### Phase 3 (Days 5+): Integration
- Test Flask routes with real Compass
- End-to-end testing: UI → Compass → Claude → Results

---

## Advantages of This Approach

| Aspect | JS Library | Python Native |
|--------|-----------|----------|
| **Dependency Weight** | Puppeteer + Chrome + stealth plugin | `requests` + `cryptography` |
| **Performance** | Browser startup (~3s per session) | HTTP request (~500ms) |
| **Memory Footprint** | High (full browser) | Low (~50MB) |
| **Debuggability** | Browser console logs | Standard Python logging |
| **Python Integration** | Requires subprocess or Node wrapper | Native Python |
| **Maintainability** | Depends on JS library updates | Full control |

---

## Potential Challenges & Solutions

### Challenge 1: Compass may use JavaScript to render session data
**Solution**: Extract `userId` and `schoolConfigKey` from HTML/meta tags. If not available, fetch after login on first API call.

### Challenge 2: Compass might validate User-Agent or Referer headers
**Solution**: Set realistic headers in requests (e.g., `requests` library uses standard browser User-Agent by default). If Compass is strict, we can add headers: `{'User-Agent': 'Mozilla/5.0...', 'Referer': baseURL}`

### Challenge 3: Compass might rate-limit or block repeated requests
**Solution**: Add request delays between calls, cache responses in SQLite, respect any rate-limit headers.

### Challenge 4: Session cookies might expire quickly
**Solution**: Store cookies and refresh/re-login if we get 401/403 responses. For long-running apps, re-login periodically.

---

## Next Steps

1. **Finalize this plan** - Confirm approach with Jethro
2. **Implement `CompassClient`** - Start with mock, then real auth
3. **Build database layer** - Credential encryption and caching
4. **Implement `LLMFilter`** - Test with mock data first
5. **Test real Compass login** - Debug any API differences
6. **Integrate Flask endpoints** - Connect CLI logic to web UI
