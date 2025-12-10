# Mock Data

This directory contains sample data for development and testing without requiring real Compass credentials.

## Files

| File | Description |
|------|-------------|
| `compass_events.json` | Sample calendar events matching the Compass API schema |
| `compass_user.json` | Sample user details matching the Compass API schema |
| `schema_version.json` | Version metadata for mock data compatibility |

## Usage

The `CompassMockClient` automatically loads data from these files when running in mock mode.

Set `COMPASS_MODE=mock` in your environment or pass `mode="mock"` to `create_client()`.

## Updating Mock Data

To refresh mock data from a real Compass instance:

```bash
cd packages/compass-client
poetry run python -m compass_client.cli refresh-mock-data
```

This requires valid Compass credentials (`COMPASS_BASE_URL`, `COMPASS_USERNAME`, `COMPASS_PASSWORD`).

The refresh process:
1. Authenticates with real Compass API
2. Fetches user details and calendar events
3. Sanitizes PII (names, emails, IDs are anonymized)
4. Writes to these JSON files
5. Updates `schema_version.json`

## Schema Version

The `schema_version.json` file tracks:

- `version`: Semantic version of the mock data schema
- `last_updated`: When the data was last refreshed
- `source`: "real" (from API) or "synthetic" (hardcoded fallback)
- `compass_version`: Compass API version if known
- `notes`: Human-readable notes about this data

Version changes:
- **MAJOR**: Breaking schema changes (incompatible with older code)
- **MINOR**: New optional fields (backward compatible)
- **PATCH**: Data updates, no schema change

## Fallback Behavior

If mock data files are missing or invalid, `CompassMockClient` falls back to hardcoded synthetic data built into the package. This ensures the mock client always works, even without these files.

## Data Format

### compass_events.json

Array of calendar event objects matching `CompassEvent` Pydantic model:

```json
[
  {
    "__type": "CalendarTransport:http://jdlf.com.au/ns/data/calendar",
    "activityId": 123456,
    "title": "Example Event",
    "start": "2025-12-15T09:00:00+11:00",
    "finish": "2025-12-15T15:00:00+11:00",
    ...
  }
]
```

### compass_user.json

Single user object matching `CompassUser` Pydantic model:

```json
{
  "__type": "UserDetailsBlob",
  "userId": 12345,
  "userFirstName": "Jane",
  "userLastName": "Smith",
  ...
}
```

## Privacy

All PII in committed mock data should be synthetic or anonymized. Never commit real student/parent data.
