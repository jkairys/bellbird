"""CLI command for refreshing mock data from real Compass API."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import typer
from dotenv import load_dotenv

from compass_client.client import CompassClient
from compass_client.models import CompassEvent, CompassUser

# Load environment variables from .env
load_dotenv()

app = typer.Typer()

# Path to mock data directory
MOCK_DATA_DIR = Path(__file__).parent.parent / "data" / "mock"


def fetch_real_data(
    username: str, password: str, base_url: str
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Fetch user details and events from real Compass API.
    
    Args:
        username: Compass API username
        password: Compass API password
        base_url: Base URL for Compass instance
    
    Returns:
        Tuple of (user_data_dict, events_list_of_dicts)
    
    Raises:
        Exception: If authentication fails or API call fails
    """
    client = CompassClient(username=username, password=password, base_url=base_url)
    
    # Fetch user details
    user_response = client.get_user()
    user_data = user_response
    
    # Fetch events
    events_response = client.get_events()
    events_data = events_response
    
    return user_data, events_data


def sanitize_user_data(user_data: dict[str, Any]) -> dict[str, Any]:
    """Remove PII (Personally Identifiable Information) from user data.
    
    Args:
        user_data: Raw user data from Compass API
    
    Returns:
        Sanitized user data dict with PII removed
    """
    sanitized = user_data.copy()
    
    # Remove/redact sensitive fields
    pii_fields = [
        "email",
        "phone",
        "mobilePhone",
        "address",
        "suburb",
        "postcode",
        "state",
        "country",
    ]
    
    for field in pii_fields:
        if field in sanitized:
            # Keep field structure but redact value
            sanitized[field] = "[REDACTED]"
    
    # Keep essential fields for testing: id, firstName, lastName
    return sanitized


def sanitize_event_data(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove PII from event data.
    
    Args:
        events: List of raw event dicts from Compass API
    
    Returns:
        List of sanitized event dicts
    """
    sanitized_events = []
    
    for event in events:
        sanitized = event.copy()
        
        # Remove/redact sensitive fields
        pii_fields = [
            "createdBy",
            "modifiedBy",
            "location",
            "description",
            "notes",
        ]
        
        for field in pii_fields:
            if field in sanitized:
                sanitized[field] = "[REDACTED]"
        
        sanitized_events.append(sanitized)
    
    return sanitized_events


def write_mock_data(
    user_data: dict[str, Any], events_data: list[dict[str, Any]]
) -> None:
    """Write sanitized mock data to JSON files.
    
    Args:
        user_data: Sanitized user data dict
        events_data: List of sanitized event dicts
    """
    # Ensure directory exists
    MOCK_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Write user data
    user_file = MOCK_DATA_DIR / "compass_user.json"
    with open(user_file, "w") as f:
        json.dump(user_data, f, indent=2)
    typer.echo(f"✓ Wrote user data to {user_file}")
    
    # Write events data
    events_file = MOCK_DATA_DIR / "compass_events.json"
    with open(events_file, "w") as f:
        json.dump(events_data, f, indent=2)
    typer.echo(f"✓ Wrote events data to {events_file}")


def update_schema_version() -> None:
    """Update schema_version.json with current timestamp and package version."""
    schema_file = MOCK_DATA_DIR / "schema_version.json"
    
    schema_data = {
        "last_updated": datetime.now().isoformat(),
        "compass_api_version": "1.0.0",  # Hardcode for now
        "mock_data_version": "1.0.0",
    }
    
    with open(schema_file, "w") as f:
        json.dump(schema_data, f, indent=2)
    typer.echo(f"✓ Updated schema version in {schema_file}")


@app.command()
def refresh_mock_data(
    username: str = typer.Option(
        ..., envvar="COMPASS_USERNAME", help="Compass API username"
    ),
    password: str = typer.Option(
        ..., envvar="COMPASS_PASSWORD", help="Compass API password", prompt=True
    ),
    base_url: str = typer.Option(
        ..., envvar="COMPASS_BASE_URL", help="Compass base URL"
    ),
    skip_sanitize: bool = typer.Option(
        False, "--skip-sanitize", help="Skip PII sanitization (NOT recommended)"
    ),
) -> None:
    """Refresh mock data by fetching fresh samples from real Compass API.
    
    Requires valid Compass credentials via environment variables or CLI options.
    Sanitizes data to remove PII before storing in repository.
    
    Example:
        poetry run compass-client refresh-mock-data \\
            --username myuser \\
            --base-url https://myschool.compass.education
    """
    typer.echo("Refreshing mock data from Compass API...")
    typer.echo(f"Base URL: {base_url}")
    typer.echo(f"Username: {username}")
    
    try:
        # Fetch real data
        typer.echo("\nFetching data from Compass API...")
        user_data, events_data = fetch_real_data(username, password, base_url)
        typer.echo(f"✓ Fetched user data: {len(str(user_data))} bytes")
        typer.echo(f"✓ Fetched {len(events_data)} events")
        
        # Sanitize if not skipped
        if not skip_sanitize:
            typer.echo("\nSanitizing data (removing PII)...")
            user_data = sanitize_user_data(user_data)
            events_data = sanitize_event_data(events_data)
            typer.echo("✓ Data sanitized")
        else:
            typer.echo(
                "⚠️  Skipping sanitization - PII will be included in mock data"
            )
        
        # Write to files
        typer.echo("\nWriting mock data files...")
        write_mock_data(user_data, events_data)
        
        # Update schema version
        typer.echo("\nUpdating schema version...")
        update_schema_version()
        
        typer.echo("\n✅ Mock data refresh completed successfully!")
        typer.echo(f"Mock data location: {MOCK_DATA_DIR}")
        typer.echo(
            "Next steps: Commit the updated mock data files to your repository"
        )
        
    except Exception as e:
        typer.echo(f"\n❌ Error refreshing mock data: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
