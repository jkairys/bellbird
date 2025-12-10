"""
Bellweaver CLI - Command-line interface for the Bellweaver application.
"""

import typer
from typing import Optional

from bellweaver.cli.commands import mock, compass, api

app = typer.Typer(
    name="bellweaver",
    help="School calendar event aggregation and filtering tool",
    add_completion=False,
)

# Register command groups
app.add_typer(mock.app, name="mock")
app.add_typer(compass.app, name="compass")
app.add_typer(api.app, name="api")


def version_callback(value: bool):
    """Print version information."""
    if value:
        typer.echo("Bellweaver CLI v0.1.0")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    )
):
    """
    Bellweaver CLI - School calendar event aggregation and filtering tool.
    """
    pass


if __name__ == "__main__":
    app()
