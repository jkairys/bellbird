"""
CLI commands for managing Compass data synchronization.
"""

import os
import json
import typer
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

from bellweaver.adapters.compass import CompassClient
from bellweaver.db.database import SessionLocal, init_db
from bellweaver.db.models import Batch, ApiPayload

# Load environment variables from .env file
load_dotenv()

app = typer.Typer(help="Manage Compass calendar data synchronization")


@app.command("sync")
def sync_calendar_events(
    days: Optional[int] = typer.Option(
        None,
        "--days",
        "-d",
        help="Number of days ahead to fetch events for (defaults to current calendar year)",
    ),
    limit: int = typer.Option(
        100,
        "--limit",
        "-l",
        help="Maximum number of events to fetch",
    ),
):
    """
    Sync calendar events from Compass to the local database.

    This command:
    1. Creates a Batch record to track this sync operation
    2. Authenticates with Compass using credentials from environment variables
    3. Fetches calendar events for the current calendar year (or specified days)
    4. Stores raw API responses in the ApiPayload table
    5. Links all payloads to the Batch record

    Requires COMPASS_BASE_URL, COMPASS_USERNAME, and COMPASS_PASSWORD
    to be set in your .env file or environment variables.
    """
    typer.echo("Syncing calendar events from Compass...")
    typer.echo("")

    # Validate environment variables
    base_url = os.getenv("COMPASS_BASE_URL")
    username = os.getenv("COMPASS_USERNAME")
    password = os.getenv("COMPASS_PASSWORD")

    if not all([base_url, username, password]):
        typer.secho(
            "✗ Missing required environment variables. Please set:",
            fg=typer.colors.RED,
            err=True,
        )
        if not base_url:
            typer.echo("  - COMPASS_BASE_URL")
        if not username:
            typer.echo("  - COMPASS_USERNAME")
        if not password:
            typer.echo("  - COMPASS_PASSWORD")
        raise typer.Exit(1)

    # Ensure base_url has a scheme
    if not base_url.startswith(("http://", "https://")):
        base_url = f"https://{base_url}"

    # Calculate date range
    if days is not None:
        # Use days from now
        from datetime import timedelta

        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
    else:
        # Use current calendar year
        current_year = datetime.now().year
        start_date = datetime(current_year, 1, 1)
        end_date = datetime(current_year, 12, 31)

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    typer.echo(f"  Date range: {start_date_str} to {end_date_str}")
    typer.echo(f"  Limit: {limit} events")
    typer.echo("")

    try:
        # Initialize database
        init_db()

        # Create database session
        db = SessionLocal()

        try:
            # Create Batch record
            typer.echo("  Creating batch record...")
            batch = Batch(
                adapter_id="compass",
                method_name="get_calendar_events",
                parameters={
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                    "limit": limit,
                },
            )
            db.add(batch)
            db.commit()
            db.refresh(batch)

            typer.echo(f"  Batch ID: {batch.id}")
            typer.echo("")

            # Authenticate with Compass
            typer.echo("  Authenticating with Compass...")
            client = CompassClient(base_url, username, password)
            client.login()
            typer.secho("  ✓ Authenticated", fg=typer.colors.GREEN)

            # Fetch calendar events
            typer.echo("  Fetching calendar events...")
            events = client.get_calendar_events(
                start_date=start_date_str,
                end_date=end_date_str,
                limit=limit,
            )

            typer.secho(f"  ✓ Fetched {len(events)} events", fg=typer.colors.GREEN)
            typer.echo("")

            # Store events as API payloads
            typer.echo("  Storing events in database...")
            for event in events:
                payload = ApiPayload(
                    adapter_id="compass",
                    method_name="get_calendar_events",
                    batch_id=batch.id,
                    payload=event,
                )
                db.add(payload)

            db.commit()
            typer.secho(f"  ✓ Stored {len(events)} events", fg=typer.colors.GREEN)

            # Close client connection
            client.close()

            # Display success summary
            typer.echo("")
            typer.secho("✓ Success! Calendar events synced.", fg=typer.colors.GREEN, bold=True)
            typer.echo("")
            typer.echo("Summary:")
            typer.echo(f"  Batch ID: {batch.id}")
            typer.echo(f"  Events stored: {len(events)}")
            typer.echo(f"  Date range: {start_date_str} to {end_date_str}")
            typer.echo(f"  Adapter: compass")
            typer.echo(f"  Method: get_calendar_events")

        finally:
            db.close()

    except ValueError as e:
        typer.secho(f"\n✗ Configuration Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.secho(f"\n✗ Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
