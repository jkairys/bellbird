"""
Pytest configuration and fixtures for Bellbird tests.
"""

import os
import pytest
from pathlib import Path
from dotenv import load_dotenv

# Load .env file automatically
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)


def pytest_addoption(parser):
    """Add custom command-line options for Compass credentials."""
    parser.addoption(
        "--compass-username",
        action="store",
        default=None,
        help="Compass username for integration tests",
    )
    parser.addoption(
        "--compass-password",
        action="store",
        default=None,
        help="Compass password for integration tests",
    )
