"""
CLI command for bootstrapping the database with initial data.
"""

import typer
import uuid
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session

from bellweaver.db.database import SessionLocal, init_db
from bellweaver.db.models import (
    Child,
    Organisation,
    ChildOrganisation,
    CommunicationChannel,
    Credential,
)
from bellweaver.models.family import OrganisationType
from bellweaver.cli.commands.compass import sync_calendar_events, process_events

app = typer.Typer(help="Bootstrap database with initial data")


@app.command("run")
def bootstrap(
    with_compass: bool = typer.Option(
        True,
        "--with-compass/--no-compass",
        help="Run Compass sync and process after seeding",
    )
):
    """
    Bootstrap the database with initial data (Children, Organisations) and optionally sync Compass data.
    """
    try:
        run_bootstrap(with_compass=with_compass)
    except Exception:
        raise typer.Exit(1)


def run_bootstrap(with_compass: bool = True):
    """
    Programmatic entry point for bootstrapping.
    """
    typer.echo("Bootstrapping database...")

    # Initialize DB
    init_db()
    db = SessionLocal()

    try:
        # Seed Data
        seed_data(db)

        # Sync Compass
        if with_compass:
            typer.echo("\n--- Running Compass Sync ---")
            try:
                # We catch SystemExit because Typer commands might use it
                # Use full calendar year to include all mock data events
                sync_calendar_events(days=None, limit=100, incremental=False)
                typer.echo("\n--- Processing Compass Events ---")
                process_events()
            except typer.Exit as e:
                if e.exit_code != 0:
                    typer.secho("Compass sync/process failed", fg=typer.colors.RED)
                    raise
            except Exception as e:
                typer.secho(f"Compass sync/process failed: {e}", fg=typer.colors.RED)
                # Don't fail the whole bootstrap if sync fails, just warn

    except Exception as e:
        typer.secho(f"Bootstrap failed: {e}", fg=typer.colors.RED)
        raise
    finally:
        db.close()

    typer.secho("\n✓ Bootstrap complete!", fg=typer.colors.GREEN, bold=True)


def seed_data(db: Session):
    """Seed initial children and organisations if they don't exist."""

    # Check if data exists
    if db.query(Child).first():
        typer.echo("  Data already exists, skipping seed.")
        return

    typer.echo("  Seeding children and organisations...")

    # 1. Create Organisations
    school_primary = Organisation(
        id=str(uuid.uuid4()),
        name="North Primary School",
        type=OrganisationType.SCHOOL.value,
        address="123 Education Lane, Northville",
        contact_info={"email": "admin@northprimary.edu"},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    club_soccer = Organisation(
        id=str(uuid.uuid4()),
        name="Northville Soccer Club",
        type=OrganisationType.SPORTS_TEAM.value,
        address="456 Sport St, Northville",
        contact_info={"email": "info@northvillesoccer.org"},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    db.add(school_primary)
    db.add(club_soccer)

    # 2. Create Children
    child_alice = Child(
        id=str(uuid.uuid4()),
        name="Alice Weaver",
        date_of_birth=date(2015, 3, 15),
        gender="Female",
        interests="Reading, Science",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    child_bob = Child(
        id=str(uuid.uuid4()),
        name="Bob Weaver",
        date_of_birth=date(2017, 7, 20),
        gender="Male",
        interests="Soccer, Lego",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    db.add(child_alice)
    db.add(child_bob)
    db.flush()  # Flush to get IDs if we didn't set them (but we did)

    # 3. Create Associations
    # Alice -> Primary School
    db.add(ChildOrganisation(child_id=child_alice.id, organisation_id=school_primary.id))

    # Bob -> Primary School
    db.add(ChildOrganisation(child_id=child_bob.id, organisation_id=school_primary.id))

    # Bob -> Soccer Club
    db.add(ChildOrganisation(child_id=child_bob.id, organisation_id=club_soccer.id))

    # 4. Create Communication Channel (Mock Compass)
    # Ensure a Credential entry exists for "compass" to satisfy FK
    if not db.query(Credential).filter_by(source="compass").first():
        compass_credential = Credential(
            source="compass",
            username="mock_user",  # Using mock credentials for bootstrapping
            password_encrypted="mock_encrypted_password",  # This will be replaced by CredentialManager if actual login happens
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(compass_credential)

    channel_compass = CommunicationChannel(
        id=str(uuid.uuid4()),
        organisation_id=school_primary.id,
        channel_type="compass",
        credential_source="compass",  # Matches what we expect in the app
        config={"base_url": "https://compass.mock.edu"},
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(channel_compass)

    db.commit()
    typer.secho("  ✓ Seeded 2 children, 2 organisations, and 1 channel.", fg=typer.colors.GREEN)
