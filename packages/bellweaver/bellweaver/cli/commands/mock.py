"""
CLI commands for managing mock data.
"""

import typer
import json
import os
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

from compass_client.cli.refresh_mock_data import fetch_real_data
from compass_client.mock_validator import load_and_validate_mock_data

app = typer.Typer(help="Manage mock data for development and testing")


@app.command("update")
def update_mock_data(
    days: int = typer.Option(
        30,
        "--days",
        "-d",
        help="Number of days ahead to fetch events for",
    ),
    limit: int = typer.Option(
        100,
        "--limit",
        "-l",
        help="Maximum number of events to fetch",
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Directory to save mock data (default: packages/compass-client/data/mock)",
    ),
):
    """
    Collect real Compass data for use as mock data in development.

    This command:
    1. Authenticates with Compass using credentials from .env
    2. Fetches user details for the authenticated user
    3. Fetches calendar events for the specified date range
    4. Saves all data to data/mock/ directory

    Requires COMPASS_BASE_URL, COMPASS_USERNAME, and COMPASS_PASSWORD
    to be set in your .env file.
    """
    typer.echo("Updating mock data from Compass...")
    typer.echo("")

    try:
        load_dotenv()
        base_url = os.getenv("COMPASS_BASE_URL")
        username = os.getenv("COMPASS_USERNAME")
        password = os.getenv("COMPASS_PASSWORD")

        if not all([base_url, username, password]):
            raise ValueError(
                "COMPASS_BASE_URL, COMPASS_USERNAME, and COMPASS_PASSWORD "
                "must be set in .env file"
            )
            
        # Ensure base_url has https://
        if not base_url.startswith("http"):
            base_url = f"https://{base_url}"

        # Resolve output directory if provided
        if output_dir:
            output_dir = output_dir.resolve()
        else:
            # Default to packages/compass-client/data/mock relative to this file
            # This file is in packages/bellweaver/bellweaver/cli/commands/mock.py
            # We want packages/compass-client/data/mock
            repo_root = Path(__file__).parent.parent.parent.parent.parent
            output_dir = repo_root / "compass-client" / "data" / "mock"

        # Collect all data
        typer.echo("  Authenticating and fetching...")
        user_details, events = fetch_real_data(
            username=username,
            password=password,
            base_url=base_url,
            days=days,
            limit=limit,
        )
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write user details
        user_file = output_dir / "compass_user.json"
        with open(user_file, "w") as f:
            json.dump(user_details, f, indent=2, default=str)

        # Write events
        events_file = output_dir / "compass_events.json"
        with open(events_file, "w") as f:
            json.dump(events, f, indent=2, default=str)

        # Calculate date range for display
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

        # Display success message
        typer.secho("\n✓ Success! Mock data collected.", fg=typer.colors.GREEN, bold=True)
        typer.echo("\nUser Details:")
        typer.echo(f"  Name: {user_details.get('userFullName', 'N/A')}")
        typer.echo(f"  Email: {user_details.get('userEmail', 'N/A')}")
        typer.echo(f"  Output: {user_file}")

        typer.echo("\nCalendar Events:")
        typer.echo(f"  Total events: {len(events)}")
        typer.echo(f"  Date range: {start_date} to {end_date}")
        typer.echo(f"  Output: {events_file}")

    except ValueError as e:
        typer.secho(f"\n✗ Configuration Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.secho(f"\n✗ Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command("validate")
def validate_mock_data():
    """
    Validate mock data schema and structure.

    This command:
    1. Loads mock data files from packages/compass-client/data/mock/
    2. Validates JSON structure against Compass API models
    3. Reports validation errors or success

    Useful after refreshing mock data to ensure it's valid.
    """
    typer.echo("Validating mock data...")
    typer.echo("")

    try:
        user_data, events_data, version_info = load_and_validate_mock_data()

        typer.secho("✓ Mock data is valid!", fg=typer.colors.GREEN, bold=True)
        typer.echo(f"\nUser Data:")
        typer.echo(f"  Fields: {len(user_data)}")

        typer.echo(f"\nCalendar Events:")
        typer.echo(f"  Total events: {len(events_data)}")

        typer.echo(f"\nSchema Version:")
        typer.echo(f"  Last updated: {version_info.get('last_updated', 'N/A')}")
        typer.echo(f"  Compass API version: {version_info.get('compass_api_version', 'N/A')}")

    except Exception as e:
        typer.secho(
            f"✗ Validation failed: {e}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1)
