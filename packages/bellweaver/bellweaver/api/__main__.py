"""
Entry point for running the Bellweaver API server as a module.

Usage:
    python -m bellweaver.api
"""

import os
from bellweaver.api import create_app


def main():
    """Run the Flask application."""
    app = create_app()
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=5000, use_reloader=debug)


if __name__ == "__main__":
    main()
