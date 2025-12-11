"""
CLI commands for managing the Bellweaver API server.
"""

import os
import typer
import re
from pathlib import Path

app = typer.Typer(help="Manage the Bellweaver API server")


@app.command()
def serve(
    host: str = typer.Option(
        "0.0.0.0",
        "--host",
        "-h",
        help="Host to bind the server to",
    ),
    port: int = typer.Option(
        5000,
        "--port",
        "-p",
        help="Port to bind the server to",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        envvar="FLASK_DEBUG",
        help="Enable debug mode with auto-reloader",
    ),
):
    """
    Start the Flask API server.

    Examples:
        # Start server on default host and port (0.0.0.0:5000)
        bellweaver api serve

        # Start server with debug mode enabled
        bellweaver api serve --debug

        # Start server on custom host and port
        bellweaver api serve --host localhost --port 8000
    """
    # Check for bootstrap request
    bootstrap_env = os.getenv("BOOTSTRAP_ON_STARTUP", "").lower()
    if bootstrap_env in ("true", "1", "yes"):
        typer.echo("\n⚠️  BOOTSTRAP_ON_STARTUP detected. Resetting database...")
        
        # Determine database path
        db_url = os.getenv("DATABASE_URL", "sqlite:///./data/bellweaver.db")
        if db_url.startswith("sqlite:///"):
            # Extract path from sqlite URL
            db_path_str = db_url.replace("sqlite:///", "")
            db_path = Path(db_path_str).resolve()
            
            if db_path.exists():
                typer.echo(f"  Removing existing database: {db_path}")
                try:
                    os.remove(db_path)
                except OSError as e:
                    typer.secho(f"  ✗ Failed to remove database: {e}", fg=typer.colors.RED)
                    # We might want to stop here, but let's try to proceed, 
                    # init_db handles existing files gracefully usually, 
                    # though bootstrapping might fail on duplicates.
            else:
                typer.echo("  Database file not found, skipping removal.")
        else:
            typer.secho("  Warning: BOOTSTRAP_ON_STARTUP only supports SQLite file removal. Skipping DB deletion.", fg=typer.colors.YELLOW)

        # Run bootstrap
        from bellweaver.cli.commands.bootstrap import run_bootstrap
        try:
            run_bootstrap(with_compass=True)
        except Exception as e:
            typer.secho(f"  ✗ Bootstrap failed: {e}", fg=typer.colors.RED)
            # Depending on policy, might want to exit. 
            # For dev convenience, maybe we crash to alert the user.
            raise typer.Exit(1)
            
        typer.echo("✅ Bootstrap finished. Starting server...\n")

    from bellweaver.api import create_app

    typer.echo(f"Starting Bellweaver API server on {host}:{port}")
    if debug:
        typer.echo("Debug mode: ON (auto-reloader enabled)")
    else:
        typer.echo("Debug mode: OFF")

    flask_app = create_app()
    flask_app.run(debug=debug, host=host, port=port, use_reloader=debug)


if __name__ == "__main__":
    app()
