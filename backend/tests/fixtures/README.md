# Test Fixtures

This directory contains sample data for testing without requiring live API credentials.

## Files

### `compass_sample_response.json`

Sample Compass API response data for calendar events. This is a sanitized subset of real Compass data that can be safely committed to version control.

**Structure**: Array of calendar event objects returned by `GetCalendarEventsByUser` API endpoint.

**Key Fields**:
- `activityId`: Unique identifier for the activity
- `longTitle`: Full event title with time
- `longTitleWithoutTime`: Event title without time prefix
- `start`/`finish`: ISO 8601 timestamps (UTC)
- `allDay`: Boolean indicating all-day events
- `description`: Event description (may include permission slip info, costs, requirements)
- `locations`: Array of location objects with `locationName`
- `managers`: Array of manager/teacher objects
- `subjectLongName`: Subject or event type
- `targetStudentId`: Student ID (0 for whole-school events)
- `rollMarked`: Whether attendance has been recorded

**Sample Events Included**:
1. Regular class session (Year 1 Generalist)
2. Excursion requiring permission slip (Zoo trip)
3. Whole school assembly
4. Multi-year sports carnival (Year 2-3)
5. Year-specific excursion (Year 4, not relevant to Year 1)

**Usage in Tests**:
```python
import json
from pathlib import Path

fixtures_dir = Path(__file__).parent / 'fixtures'
with open(fixtures_dir / 'compass_sample_response.json') as f:
    sample_events = json.load(f)
```

## Generating Fresh Mock Data

To collect new mock data from a real Compass instance (stored in `data/mock/`, git-ignored):

```bash
poetry run python scripts/collect_mock_data.py
```

This requires:
- `COMPASS_BASE_URL` in `.env`
- `COMPASS_USERNAME` in `.env`
- `COMPASS_PASSWORD` in `.env`

The script will:
1. Authenticate with Compass
2. Fetch events for the next 30 days
3. Save raw response to `data/mock/compass_events_raw.json`
4. Save sanitized version to `data/mock/compass_events_sanitized.json`
5. Create metadata file with collection timestamp

**Note**: Raw mock data in `data/mock/` is git-ignored and should NOT be committed as it may contain sensitive information. Only the curated, sanitized fixtures in this directory should be committed.
