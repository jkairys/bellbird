"""
Pytest configuration and fixtures for Bellweaver tests.
"""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Load .env file automatically
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

# Set COMPASS_MODE to mock for all tests (unless explicitly overridden)
if "COMPASS_MODE" not in os.environ:
    os.environ["COMPASS_MODE"] = "mock"


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
