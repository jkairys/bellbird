"""
Test fixtures for Bellbird.

Provides easy access to sample data for testing.
"""

import json
from pathlib import Path
from typing import List, Dict, Any


_FIXTURES_DIR = Path(__file__).parent


def load_compass_sample_events() -> List[Dict[str, Any]]:
    """
    Load sample Compass calendar events from fixtures.

    Returns:
        List of calendar event dictionaries matching Compass API response format
    """
    fixture_file = _FIXTURES_DIR / 'compass_sample_response.json'
    with open(fixture_file) as f:
        return json.load(f)


def get_fixtures_dir() -> Path:
    """
    Get the path to the fixtures directory.

    Returns:
        Path object for the fixtures directory
    """
    return _FIXTURES_DIR
