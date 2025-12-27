"""Browser-based data fetcher using Playwright to bypass Cloudflare protection."""

import json
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright_stealth import Stealth


def log(msg: str) -> None:
    """Print message and flush immediately."""
    print(msg, flush=True)


class BrowserFetcher:
    """Fetches data from Compass using a real browser to bypass Cloudflare."""

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        headless: bool = True,
    ):
        """
        Initialize browser fetcher.

        Args:
            base_url: Base URL of Compass instance
            username: Compass username
            password: Compass password
            headless: Whether to run browser in headless mode
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.headless = headless
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._playwright = None
        self.user_id: Optional[int] = None

        # Use persistent user data directory to maintain session
        self._user_data_dir = Path.home() / ".compass-client" / "browser-data"

    def __enter__(self):
        """Context manager entry."""
        self._playwright = sync_playwright().start()

        # Use persistent context to maintain cookies/session across runs
        self._user_data_dir.mkdir(parents=True, exist_ok=True)

        self._context = self._playwright.chromium.launch_persistent_context(
            user_data_dir=str(self._user_data_dir),
            headless=self.headless,
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            # Additional args to appear more like a real browser
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
            ],
            # Try using Chrome instead of Chromium for better compatibility
            channel="chrome" if not self.headless else None,
        )
        self._page = self._context.pages[0] if self._context.pages else self._context.new_page()

        # Apply stealth to avoid bot detection
        stealth = Stealth(
            navigator_platform_override="MacIntel",
            navigator_vendor_override="Google Inc.",
        )
        stealth.apply_stealth_sync(self._page)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._context:
            self._context.close()
        if self._playwright:
            self._playwright.stop()

    def _wait_for_cloudflare(self, max_wait: int = 60) -> None:
        """Wait for Cloudflare/verification challenges to complete."""
        if not self._page:
            return

        log("  Checking for verification challenges...")
        start_time = time.time()

        while time.time() - start_time < max_wait:
            # Check if we're past the challenge
            try:
                page_content = self._page.content().lower()
            except Exception as e:
                log(f"  Error getting page content: {e}")
                time.sleep(2)
                continue

            # Challenge/verification indicators
            challenge_indicators = [
                "checking your browser",
                "just a moment",
                "verify you are human",
                "challenge-running",
                "verifying your connection",  # Compass-specific
                "please wait",
            ]

            is_challenge_page = any(ind in page_content for ind in challenge_indicators)

            # Check for login form as a sign we're past the challenge
            has_login_form = (
                'id="username"' in page_content or
                'name="username"' in page_content or
                'id="password"' in page_content
            )

            if has_login_form:
                log("  Login form detected - verification cleared!")
                return

            if is_challenge_page:
                log(f"  Waiting for verification... ({int(time.time() - start_time)}s)")
                time.sleep(2)
                continue

            # No challenge and no login form - might be loading
            log(f"  Page loading... ({int(time.time() - start_time)}s)")
            time.sleep(2)

        log("  Warning: Verification wait timeout - proceeding anyway")

    def login(self) -> bool:
        """
        Log in to Compass via browser.

        Returns:
            True if login successful

        Raises:
            Exception: If login fails
        """
        if not self._page:
            raise RuntimeError("Browser not initialized. Use as context manager.")

        login_url = f"{self.base_url}/login.aspx?sessionstate=disabled"
        log(f"  Navigating to {login_url}...")

        # Navigate to login page with domcontentloaded (faster than networkidle)
        log("  Calling page.goto()...")
        self._page.goto(login_url, wait_until="domcontentloaded", timeout=60000)
        log("  Page loaded (domcontentloaded)")

        # Wait for Cloudflare challenge to complete
        self._wait_for_cloudflare(max_wait=60)

        # Wait a bit more for page to stabilize
        log("  Waiting for page to fully load...")
        self._page.wait_for_load_state("load", timeout=30000)
        log("  Page fully loaded")

        # Check if we're on the login page
        current_url = self._page.url
        log(f"  Current URL: {current_url}")

        # Fill in login form
        log("  Looking for login form...")
        try:
            # Wait a bit for dynamic content to load
            time.sleep(3)

            # Use locator API which is more robust
            log("  Looking for username field with locator...")
            username_locator = self._page.locator("#username")

            try:
                # Wait for username field to be visible (longer timeout for slow connections)
                username_locator.wait_for(state="visible", timeout=30000)
                log("  Username field is visible")
            except PlaywrightTimeout:
                # Save debug info
                log("  Timeout waiting for username field - saving debug screenshot...")
                debug_path = Path.home() / ".compass-client" / "debug_login.png"
                self._page.screenshot(path=str(debug_path))
                log(f"  Screenshot saved to {debug_path}")

                # Also save HTML for debugging
                html_path = Path.home() / ".compass-client" / "debug_login.html"
                html_path.write_text(self._page.content())
                log(f"  HTML saved to {html_path}")
                raise

            # Fill username
            log(f"  Filling username: {self.username}")
            username_locator.fill(self.username)

            # Fill password
            log("  Filling password...")
            password_locator = self._page.locator("#password")
            password_locator.fill(self.password)

            # Click login button
            log("  Clicking Sign in button...")
            button_locator = self._page.locator("#button1")
            button_locator.click()

            # Wait for navigation after login
            log("  Waiting for login to complete...")
            self._page.wait_for_load_state("load", timeout=30000)

            # Wait for any post-login verification (Cloudflare Turnstile)
            log("  Checking for post-login verification...")
            self._wait_for_cloudflare(max_wait=90)

            # Additional wait for redirects
            time.sleep(2)

        except PlaywrightTimeout:
            log("  Login form interaction timeout")

        # Check if login was successful
        current_url = self._page.url
        log(f"  Post-login URL: {current_url}")

        if "login" in current_url.lower():
            # Save debug screenshot
            debug_path = Path.home() / ".compass-client" / "debug_post_login.png"
            self._page.screenshot(path=str(debug_path))
            log(f"  Debug screenshot saved to {debug_path}")

            # Check for error message - look for common error patterns
            page_content = self._page.content()

            # Look for specific error text patterns
            error_patterns = [
                "invalid username",
                "invalid password",
                "incorrect",
                "authentication failed",
                "login failed",
                "account locked",
                "too many attempts",
            ]

            for pattern in error_patterns:
                if pattern in page_content.lower():
                    raise Exception(f"Login failed: {pattern}")

            # Check for error elements
            error_selectors = [
                ".login-error",
                ".error-message",
                "#error",
                ".alert-danger",
                ".validation-summary-errors",
                "[class*='error']",
            ]
            for selector in error_selectors:
                error_elem = self._page.query_selector(selector)
                if error_elem:
                    error_text = error_elem.text_content()
                    if error_text and error_text.strip():
                        raise Exception(f"Login failed: {error_text.strip()}")

            # Check if still on verification page
            page_content = self._page.content().lower()
            if "verifying" in page_content or "cloudflare" in page_content:
                raise Exception(
                    "Login failed: Cloudflare verification did not complete. "
                    "Run with --no-headless first to complete verification manually, "
                    "then subsequent runs may work in headless mode."
                )

            # If no specific error found, check if the form still has values
            try:
                username_value = self._page.locator("#username").input_value(timeout=5000)
                if username_value:
                    log(f"  Username field still has value: {username_value}")
                    raise Exception(
                        "Login failed: Form still has values (submit may have failed). "
                        "Check credentials or try --no-headless to debug."
                    )
            except PlaywrightTimeout:
                pass  # Element not found, which is fine

            raise Exception(
                "Login failed: Still on login page. "
                "Try running with --no-headless to debug."
            )

        log("  Login successful!")

        # Extract user ID from page
        self._extract_user_id()

        return True

    def _extract_user_id(self) -> None:
        """Extract user ID from the page after login."""
        if not self._page:
            return

        # Try to get user ID from page content or URL
        page_content = self._page.content()

        # Look for userId in various formats
        patterns = [
            r'"userId"\s*:\s*(\d+)',
            r"userId\s*=\s*(\d+)",
            r'data-user-id="(\d+)"',
        ]

        for pattern in patterns:
            match = re.search(pattern, page_content)
            if match:
                self.user_id = int(match.group(1))
                log(f"  Found user ID: {self.user_id}")
                return

        log("  Warning: Could not extract user ID from page")

    def get_user_details(self, target_user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Fetch user details from Compass.

        Args:
            target_user_id: Optional specific user ID to fetch

        Returns:
            User details dict
        """
        if not self._page:
            raise RuntimeError("Browser not initialized. Use as context manager.")

        user_id = target_user_id or self.user_id
        if not user_id:
            raise Exception("No user ID available. Login first.")

        url = f"{self.base_url}/Services/User.svc/GetUserDetailsBlobByUserId"

        log(f"  Fetching user details for user ID {user_id}...")

        # Make API request using page's fetch
        response = self._page.evaluate(
            """async (params) => {
                try {
                    const response = await fetch(params.url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ targetUserId: params.userId }),
                    });

                    // Check if response is OK
                    if (!response.ok) {
                        return { error: `HTTP ${response.status}: ${response.statusText}` };
                    }

                    // Try to parse as JSON
                    const text = await response.text();
                    try {
                        return JSON.parse(text);
                    } catch (e) {
                        return { error: `Not JSON: ${text.substring(0, 200)}` };
                    }
                } catch (e) {
                    return { error: e.message };
                }
            }""",
            {"url": url, "userId": user_id},
        )

        if not response:
            raise Exception("Failed to fetch user details: empty response")

        if isinstance(response, dict) and "error" in response:
            raise Exception(f"Failed to fetch user details: {response['error']}")

        # Extract the data from response
        if isinstance(response, dict) and "d" in response:
            return response["d"]
        return response

    def get_calendar_events(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Fetch calendar events from Compass.

        Args:
            start_date: Start date in YYYY-MM-DD format (defaults to today)
            end_date: End date in YYYY-MM-DD format (defaults to 30 days from now)
            limit: Maximum number of events to return

        Returns:
            List of event dicts
        """
        if not self._page:
            raise RuntimeError("Browser not initialized. Use as context manager.")

        if not self.user_id:
            raise Exception("No user ID available. Login first.")

        # Set default dates
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        url = f"{self.base_url}/Services/Calendar.svc/GetCalendarEventsByUser"

        log(f"  Fetching calendar events from {start_date} to {end_date}...")

        # Make API request using page's fetch
        response = self._page.evaluate(
            """async (params) => {
                try {
                    const response = await fetch(params.url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            userId: params.userId,
                            startDate: params.startDate,
                            endDate: params.endDate,
                            limit: params.limit,
                            start: 0,
                            page: 1,
                        }),
                    });

                    // Check if response is OK
                    if (!response.ok) {
                        return { error: `HTTP ${response.status}: ${response.statusText}` };
                    }

                    // Try to parse as JSON
                    const text = await response.text();
                    try {
                        return JSON.parse(text);
                    } catch (e) {
                        return { error: `Not JSON: ${text.substring(0, 200)}` };
                    }
                } catch (e) {
                    return { error: e.message };
                }
            }""",
            {
                "url": url,
                "userId": self.user_id,
                "startDate": start_date,
                "endDate": end_date,
                "limit": limit,
            },
        )

        if not response:
            raise Exception("Failed to fetch calendar events: empty response")

        if isinstance(response, dict) and "error" in response:
            raise Exception(f"Failed to fetch calendar events: {response['error']}")

        # Extract events from response
        if isinstance(response, dict):
            if "d" in response:
                data = response["d"]
                if isinstance(data, list):
                    return data[:limit]
                elif isinstance(data, dict) and "data" in data:
                    return data["data"][:limit]
            elif "data" in response:
                return response["data"][:limit]

        if isinstance(response, list):
            return response[:limit]

        return []


def fetch_with_browser(
    base_url: str,
    username: str,
    password: str,
    days: int = 30,
    limit: int = 100,
    headless: bool = True,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Fetch user details and events using browser automation.

    Args:
        base_url: Compass base URL
        username: Compass username
        password: Compass password
        days: Number of days to fetch events for
        limit: Maximum number of events
        headless: Whether to run headless

    Returns:
        Tuple of (user_data, events_list)
    """
    with BrowserFetcher(base_url, username, password, headless=headless) as fetcher:
        fetcher.login()

        user_data = fetcher.get_user_details()
        log(f"  Got user data: {len(str(user_data))} bytes")

        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

        events = fetcher.get_calendar_events(start_date, end_date, limit)
        log(f"  Got {len(events)} events")

        return user_data, events
