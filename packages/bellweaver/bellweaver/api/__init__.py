"""
Flask application factory for Bellweaver API.

Provides REST API endpoints for accessing aggregated school calendar events.
"""

import os
from pathlib import Path
from flask import Flask, send_from_directory, abort

from bellweaver.db.database import init_db
from bellweaver.api.routes import register_routes
from bellweaver.startup import startup_checks, StartupValidationError


def create_app() -> Flask:
    """
    Create and configure the Flask application.

    Returns:
        Configured Flask application instance

    Raises:
        StartupValidationError: If startup validation fails.
    """
    # Determine static folder path (for production Docker build)
    static_folder = Path(__file__).parent.parent / "static"

    # Only set static_folder if it exists (production mode)
    if static_folder.exists():
        app = Flask(__name__, static_folder=str(static_folder), static_url_path="")
    else:
        app = Flask(__name__)

    # Run startup validation checks
    compass_mode = os.getenv("COMPASS_MODE")
    try:
        startup_checks(compass_mode)
    except StartupValidationError as e:
        app.logger.error(f"Startup validation failed: {e}")
        raise

    # Initialize database on startup
    with app.app_context():
        init_db()

    # Register all route blueprints
    register_routes(app)

    # Serve frontend static files in production
    if static_folder.exists():
        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def serve_frontend(path):
            """Serve React frontend static files or index.html for client-side routing."""
            # Don't serve frontend for API routes - let them 404 if not found
            if path.startswith("api/"):
                abort(404)

            if path and (static_folder / path).exists():
                return send_from_directory(static_folder, path)
            return send_from_directory(static_folder, "index.html")

    return app


if __name__ == "__main__":
    import os

    app = create_app()
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=5000, use_reloader=debug)
