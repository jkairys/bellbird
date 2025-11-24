#!/usr/bin/env python3
"""
Debug script for testing Compass browser-based authentication.

This script tests the Playwright-based Compass client with detailed logging and debugging.
It requires Compass credentials to be set in the environment.

Usage:
    COMPASS_USERNAME=your_username COMPASS_PASSWORD=your_password python debug_browser_login.py

Options:
    --debug: Show browser window and save screenshots
    --headless: Run browser in headless mode (default, use --debug for visible mode)
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('debug_browser_login.log')
    ]
)

logger = logging.getLogger(__name__)

from src.adapters.compass_browser import CompassBrowserClient

# Configuration
COMPASS_BASE_URL = "https://seaford-northps-vic.compass.education"


def main():
    """Main test function."""
    logger.info("=" * 80)
    logger.info("COMPASS BROWSER CLIENT DEBUG TEST")
    logger.info("=" * 80)

    # Check for command-line arguments
    debug_mode = '--debug' in sys.argv
    headless = '--headless' not in sys.argv if '--debug' not in sys.argv else True

    # Get credentials from environment
    username = os.environ.get('COMPASS_USERNAME')
    password = os.environ.get('COMPASS_PASSWORD')

    if not username or not password:
        logger.error("ERROR: Compass credentials not provided!")
        logger.error("Set COMPASS_USERNAME and COMPASS_PASSWORD environment variables")
        sys.exit(1)

    logger.info(f"Username: {username}")
    logger.info(f"Base URL: {COMPASS_BASE_URL}")
    logger.info(f"Debug Mode: {debug_mode}")
    logger.info(f"Headless: {headless}")
    logger.info("")

    client = None
    try:
        # Create client
        logger.info("Step 1: Creating CompassBrowserClient...")
        client = CompassBrowserClient(
            base_url=COMPASS_BASE_URL,
            username=username,
            password=password,
            debug=debug_mode,
            headless=headless
        )
        logger.info("✓ Client created successfully\n")

        # Test login
        logger.info("Step 2: Testing login...")
        result = client.login()
        logger.info(f"✓ Login result: {result}")
        logger.info(f"✓ Authenticated: {client._authenticated}")
        logger.info(f"✓ User ID: {client.user_id}")
        logger.info(f"✓ School Config Key: {client.school_config_key}")
        logger.info("")

        # Get cookies
        logger.info("Step 3: Checking authentication cookies...")
        if client.context:
            cookies = client.context.cookies()
            logger.info(f"Current cookies: {len(cookies)}")
            for cookie in cookies:
                logger.debug(f"  - {cookie['name']}: {cookie['value'][:50]}..." if len(cookie.get('value', '')) > 50 else f"  - {cookie['name']}: {cookie['value']}")
        logger.info("")

        # Test calendar events fetch
        logger.info("Step 4: Testing calendar event fetch...")
        today = datetime.now()
        start_date = today.strftime("%Y-%m-%d")
        end_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")

        logger.info(f"Requesting events from {start_date} to {end_date}...")

        events = client.get_calendar_events(start_date, end_date)
        logger.info(f"✓ Successfully fetched {len(events)} calendar events")

        if events:
            logger.info("\nFirst 3 events:")
            for i, event in enumerate(events[:3], 1):
                logger.info(f"\n  Event {i}:")
                logger.info(f"    Title: {event.get('title', 'N/A')}")
                logger.info(f"    Date: {event.get('startDate', 'N/A')}")
                logger.info(f"    Type: {event.get('type', 'N/A')}")
                logger.info(f"    ID: {event.get('id', 'N/A')}")
        else:
            logger.warning("No events returned for the requested date range")

        logger.info("\n" + "=" * 80)
        logger.info("✓ ALL TESTS PASSED!")
        logger.info("=" * 80)
        return 0

    except Exception as e:
        logger.error("\n" + "=" * 80)
        logger.error(f"✗ TEST FAILED: {e}")
        logger.error("=" * 80, exc_info=True)
        return 1

    finally:
        # Clean up
        if client:
            logger.info("\nCleaning up browser resources...")
            try:
                client.close()
                logger.info("✓ Browser closed successfully")
            except Exception as e:
                logger.warning(f"Warning closing browser: {e}")


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
