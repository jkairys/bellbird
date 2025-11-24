"""
Compass Education API client using browser automation.

Uses pyppeteer (Python Puppeteer) for reliable authentication and calendar event fetching.
This implementation handles complex login flows and JavaScript-heavy pages.
Includes stealth plugin to bypass Cloudflare bot detection in headless mode.
"""

import json
import logging
import os
import asyncio
from datetime import datetime
from typing import Optional, Dict, List, Any
from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.page import Page
from pyppeteer_stealth import stealth

# Set up logging for debugging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def client_has_auth_cookies(cookies: List[Dict[str, Any]]) -> bool:
    """Check if client has authentication-related cookies."""
    cookie_names = [c.get('name') for c in cookies]
    return any(auth_cookie in cookie_names for auth_cookie in ['cpsdid', '__cf_chl_jschl_tk', 'cf_clearance'])


class CompassBrowserClient:
    """
    Python client for Compass Education API using browser automation.

    Uses pyppeteer (Python Puppeteer) for reliable session management and form submission.
    Includes stealth plugin to bypass Cloudflare bot detection.
    Handles complex authentication and JavaScript interactions.
    """

    def __init__(self, base_url: str, username: str, password: str, debug: bool = False, headless: bool = True):
        """
        Initialize Compass browser client.

        Args:
            base_url: Base URL of Compass instance (e.g., "https://compass.example.com")
            username: Compass username
            password: Compass password
            debug: If True, show browser window and save screenshots on errors
            headless: If True, run browser in headless mode (ignored if debug=True)
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.debug = debug
        self.headless = headless if not debug else False
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.user_id: Optional[int] = None
        self.school_config_key: Optional[str] = None
        self._authenticated = False
        self.screenshot_dir = "debug_screenshots" if debug else None
        if debug and not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
        # For managing async event loop
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def _get_event_loop(self) -> asyncio.AbstractEventLoop:
        """Get or create an event loop for async operations."""
        try:
            # Try to get the currently running loop
            return asyncio.get_running_loop()
        except RuntimeError:
            # No running loop, check if we have a saved one
            if self._loop is None or self._loop.is_closed():
                try:
                    # Try to get the event loop for this thread
                    self._loop = asyncio.get_event_loop()
                    if self._loop.is_closed():
                        self._loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(self._loop)
                except RuntimeError:
                    # Create a new event loop
                    self._loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(self._loop)
            return self._loop

    async def _launch_browser_async(self) -> None:
        """Launch the browser asynchronously if not already running."""
        if self.browser is None:
            logger.info(f"Launching browser (headless={self.headless}, debug={self.debug})")

            # Browser launch arguments for both headless and debug modes
            # These are critical for avoiding headless browser detection
            args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',  # Avoid shared memory issues in headless
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-background-networking',
                '--disable-client-side-phishing-detection',
                '--disable-popup-blocking',
                '--disable-prompt-on-repost',
                '--disable-sync',
                '--metrics-recording-only',
                '--mute-audio',
            ]

            self.browser = await launch(
                headless=self.headless,
                args=args,
                defaultViewport={'width': 1280, 'height': 720}
            )

            # Create new page first (before applying stealth)
            self.page = await self.browser.newPage()

            # Apply stealth plugin to avoid Cloudflare bot detection
            logger.info("Applying pyppeteer-stealth plugin to bypass bot detection...")
            try:
                await stealth(self.page)
                logger.info("Stealth plugin applied successfully")
            except Exception as e:
                logger.warning(f"Warning: Failed to apply stealth plugin: {e} (continuing anyway)")

            # Set viewport and other options
            await self.page.setViewport({'width': 1280, 'height': 720})

            # Set user agent to look more human
            await self.page.setUserAgent(
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/142.0.0.0 Safari/537.36'
            )

            # Inject comprehensive stealth script to avoid Cloudflare bot detection
            # Based on puppeteer-extra-plugin-stealth patterns
            await self.page.evaluateOnNewDocument("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });

                // Additional stealth properties for Cloudflare bypass
                Object.defineProperty(navigator, 'permissions', {
                    get: () => ({
                        query: (q) => Promise.resolve({ state: Notification.permission })
                    })
                });

                // Override chrome property that Cloudflare checks
                window.chrome = {
                    runtime: {}
                };

                // Phantom/headless detection bypass
                Object.defineProperty(navigator, 'vendor', {
                    get: () => 'Google Inc.',
                });

                // Spoof devtools detection
                const originalQuery = window.matchMedia;
                window.matchMedia = function(query) {
                    if (query === '(prefers-color-scheme: dark)') {
                        return originalQuery.call(window, query);
                    }
                    return {
                        matches: false,
                        media: query,
                        onchange: null,
                        addListener: function() {},
                        removeListener: function() {},
                        addEventListener: function() {},
                        removeEventListener: function() {},
                        dispatchEvent: function() {}
                    };
                };
            """)

            # Set up request/response logging for all modes (helps debug)
            self.captured_responses = {}

            def capture_response(response):
                # Capture responses for analysis (not async)
                try:
                    url = response.url
                    status = response.status
                    if 'home' in url or 'calendar' in url or 'user' in url.lower() or 'location' in url.lower():
                        self.captured_responses[url] = {
                            'status': status,
                            'url': url,
                        }
                        logger.debug(f"<< {status} {url}")
                except Exception as e:
                    logger.debug(f"Error capturing response: {e}")

            def capture_request(request):
                logger.debug(f">> {request.method} {request.url}")

            self.page.on('request', capture_request)
            self.page.on('response', capture_response)

            logger.info("Browser launched successfully")

    async def login_async(self) -> bool:
        """
        Authenticate with Compass using browser automation.

        Returns:
            True if successful, raises exception otherwise
        """
        try:
            await self._launch_browser_async()

            login_url = f"{self.base_url}/login.aspx"
            logger.info(f"Navigating to login URL: {login_url}")

            # Navigate to login page with extended timeout
            try:
                await self.page.goto(login_url, waitUntil='networkidle0', timeout=30000)
                logger.info("Login page loaded successfully")
            except Exception as e:
                logger.error(f"Failed to navigate to login page: {e}")
                if self.debug:
                    await self._save_screenshot("01_navigation_failed")
                raise

            # Take screenshot of login page
            if self.debug:
                await self._save_screenshot("02_login_page_loaded")

            # Check page content for Cloudflare challenges - be more lenient
            page_content = await self.page.content()
            if 'cloudflare' in page_content.lower() or 'checking your browser' in page_content.lower():
                logger.warning("Cloudflare challenge detected on login page")
                logger.info("Waiting for Cloudflare challenge to be resolved (up to 60 seconds)...")
                if self.debug:
                    await self._save_screenshot("03_cloudflare_challenge")
                # Wait for the challenge to be resolved (up to 60 seconds for pyppeteer)
                try:
                    # Wait for either the form to appear or the challenge text to disappear
                    await asyncio.wait_for(
                        self.page.waitForFunction(
                            "() => {"
                            "  const hasForm = document.querySelector('input[name=\"username\"]') !== null;"
                            "  const noChallenge = !document.body.innerText.includes('Checking your browser');"
                            "  return hasForm || noChallenge;"
                            "}",
                            timeout=60000
                        ),
                        timeout=65.0
                    )
                    logger.info("Cloudflare challenge resolved or form appeared")
                except (Exception, asyncio.TimeoutError):
                    logger.warning("Cloudflare challenge resolution timeout - trying to wait more...")
                    await asyncio.sleep(5)  # Additional wait
                    page_content = await self.page.content()
                    if 'cloudflare' in page_content.lower():
                        logger.warning("Still detecting Cloudflare - continuing anyway")

            # Wait for form fields to be visible (increased timeout for Cloudflare)
            logger.info("Waiting for username field...")
            try:
                await self.page.waitForSelector('input[name="username"]', timeout=30000)
                logger.info("Username field found")
            except Exception as e:
                logger.error(f"Username field not found: {e}")
                if self.debug:
                    await self._save_screenshot("04_username_field_not_found")
                # Get page content for debugging
                try:
                    page_content = await self.page.content()
                    if len(page_content) < 5000:
                        logger.error(f"Page content: {page_content}")
                    else:
                        logger.error(f"Page content (first 2000 chars): {page_content[:2000]}")
                except:
                    pass
                raise

            # Fill in credentials with delays to look more human
            logger.info(f"Filling username: {self.username}")
            await self.page.focus('input[name="username"]')
            await asyncio.sleep(0.1)
            for char in self.username:
                await self.page.keyboard.type(char)
                await asyncio.sleep(0.05)

            await asyncio.sleep(0.2)

            logger.info("Filling password...")
            await self.page.focus('input[name="password"]')
            await asyncio.sleep(0.1)
            for char in self.password:
                await self.page.keyboard.type(char)
                await asyncio.sleep(0.05)

            await asyncio.sleep(0.3)

            # Check "remember me" if available
            try:
                remember_checkbox = await self.page.querySelector('input[name="rememberMeChk"]')
                if remember_checkbox:
                    await remember_checkbox.click()
                    await asyncio.sleep(0.1)
                    logger.info("Checked 'remember me' checkbox")
            except Exception as e:
                logger.warning(f"Could not check 'remember me': {e}")

            if self.debug:
                await self._save_screenshot("05_form_filled")

            # Submit the form
            logger.info("Submitting login form...")
            await asyncio.sleep(0.5)

            # Find and click submit button
            submit_button = await self.page.querySelector('input[type="submit"]')
            if not submit_button:
                submit_button = await self.page.querySelector('button[type="submit"]')

            if submit_button:
                logger.info("Found submit button, clicking it")
                # Click and wait for navigation in parallel
                try:
                    await asyncio.gather(
                        self.page.click('input[type="submit"]') if await self.page.querySelector('input[type="submit"]') else self.page.click('button[type="submit"]'),
                        self.page.waitForNavigation(waitUntil='networkidle0', timeout=60000)
                    )
                    logger.info("Navigation completed successfully")
                except asyncio.TimeoutError:
                    logger.warning("Navigation wait timed out (continuing anyway)")
                except Exception as nav_error:
                    logger.warning(f"Navigation error: {nav_error} (continuing anyway)")
            else:
                logger.warning("No submit button found, trying Enter key")
                await self.page.press('input[name="password"]', 'Enter')
                try:
                    await self.page.waitForNavigation(waitUntil='networkidle0', timeout=60000)
                    logger.info("Navigation completed successfully")
                except Exception as nav_error:
                    logger.warning(f"Navigation wait timed out: {nav_error} (continuing anyway)")

            # Wait for Cloudflare challenge after form submission
            logger.info("Waiting for potential Cloudflare challenge after form submission...")
            try:
                await self.page.waitForFunction(
                    "() => !window.location.search.includes('__cf_chl')",
                    timeout=20000
                )
                logger.info("Cloudflare challenge after submission resolved")
            except Exception:
                logger.warning("Cloudflare challenge timeout after submission")

            # Wait for navigation away from login page
            logger.info("Waiting for login navigation...")
            navigation_success = False
            try:
                await self.page.waitForFunction(
                    "() => !window.location.href.includes('login.aspx')",
                    timeout=40000
                )
                logger.info(f"Successfully navigated away from login. New URL: {self.page.url}")
                navigation_success = True
            except Exception as e:
                logger.warning(f"Navigation timeout or still on login page: {e}")
                # Check if we have auth cookies anyway
                cookies = await self.page.cookies()
                logger.info(f"Current cookies: {[c['name'] for c in cookies]}")
                if self.debug:
                    await self._save_screenshot("07_navigation_timeout")

                # Even if navigation timed out, if we have authentication-related cookies, continue
                if client_has_auth_cookies(cookies):
                    logger.info("Auth cookies present, attempting to extract userId anyway...")
                    # Try to navigate to home page to get userId
                    try:
                        logger.info("Attempting to navigate to home page...")
                        await self.page.goto(f"{self.base_url}/home.aspx", waitUntil='domcontentloaded', timeout=20000)
                        logger.info(f"Navigated to home page. URL: {self.page.url}")
                        await asyncio.sleep(2)  # Give page time to load
                    except Exception as nav_e:
                        logger.warning(f"Could not navigate to home page: {nav_e}")

            # Take final screenshot
            if self.debug:
                await self._save_screenshot("08_after_login")

            # Extract userId from the page
            logger.info("Extracting session metadata...")
            await self._extract_session_metadata()

            # If we navigated successfully or have auth cookies, mark as authenticated
            if navigation_success:
                logger.info("Session cookies confirmed, performing initialization API calls...")
                try:
                    await self._initialize_session()
                    logger.info("Session initialization complete")
                except Exception as e:
                    logger.warning(f"Session initialization had issues: {e} (continuing anyway)")

                self._authenticated = True
                logger.info("Login successful!")
                return True
            else:
                cookies = await self.page.cookies()
                if client_has_auth_cookies(cookies):
                    logger.info("Auth cookies present despite navigation timeout, marking as authenticated")
                    try:
                        await self._initialize_session()
                    except Exception as e:
                        logger.warning(f"Session initialization had issues: {e} (continuing anyway)")
                    self._authenticated = True
                    return True
                else:
                    raise Exception("Navigation failed and no authentication cookies present")

        except Exception as e:
            logger.error(f"Login failed with exception: {e}", exc_info=True)
            if self.debug:
                await self._save_screenshot("99_login_error")
            raise Exception(f"Login failed: {e}")

    def login(self) -> bool:
        """
        Synchronous wrapper for login_async.
        """
        loop = self._get_event_loop()
        return loop.run_until_complete(self.login_async())

    async def _initialize_session(self) -> None:
        """
        Perform required API calls to initialize the Compass session.

        These calls are necessary after login to properly set up the session,
        even though they don't appear to return meaningful data.
        """
        # Give the session time to stabilize after login
        logger.info("Waiting for session to stabilize...")
        await asyncio.sleep(2)

        try:
            logger.info("Calling getAllLocations API...")
            response_text = await self.page.evaluate(
                f"""
                async () => {{
                    try {{
                        const response = await fetch('{self.base_url}/Services/Location.svc/GetAllLocations', {{
                            method: 'GET',
                            headers: {{
                                'X-Requested-With': 'XMLHttpRequest',
                                'Accept': 'application/json'
                            }}
                        }});
                        const text = await response.text();
                        console.log('getAllLocations status:', response.status);
                        console.log('getAllLocations response:', text.substring(0, 200));
                        return JSON.stringify({{status: response.status, body: text.substring(0, 500)}});
                    }} catch (error) {{
                        console.log('getAllLocations error:', error.message);
                        return JSON.stringify({{ error: error.message }});
                    }}
                }}
                """
            )
            if response_text:
                try:
                    data = json.loads(response_text)
                    logger.info(f"getAllLocations response status: {data.get('status')}")
                    if data.get('status') == 200:
                        logger.info("getAllLocations returned 200 OK")
                except:
                    pass
            logger.info("getAllLocations API called")
        except Exception as e:
            logger.warning(f"Error calling getAllLocations: {e}")

        await asyncio.sleep(1)

        try:
            logger.info("Calling getUserDetails API...")
            user_details = await self.page.evaluate(
                f"""
                async () => {{
                    try {{
                        const response = await fetch('{self.base_url}/Services/User.svc/GetUserDetails', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                                'X-Requested-With': 'XMLHttpRequest',
                                'Accept': 'application/json'
                            }},
                            body: JSON.stringify({{}})
                        }});
                        const text = await response.text();
                        console.log('getUserDetails status:', response.status);
                        console.log('getUserDetails response:', text.substring(0, 200));
                        return JSON.stringify({{status: response.status, body: text.substring(0, 500)}});
                    }} catch (error) {{
                        console.log('getUserDetails error:', error.message);
                        return JSON.stringify({{ error: error.message }});
                    }}
                }}
                """
            )
            if user_details:
                try:
                    data = json.loads(user_details)
                    logger.info(f"getUserDetails response status: {data.get('status')}")
                    if data.get('status') == 200:
                        logger.info("getUserDetails returned 200 OK - session appears valid")
                        try:
                            body_data = json.loads(data.get('body', '{}'))
                            if isinstance(body_data, dict):
                                if 'd' in body_data and isinstance(body_data['d'], dict):
                                    user_id = body_data['d'].get('id') or body_data['d'].get('userId') or body_data['d'].get('organisationUserId')
                                    if user_id:
                                        self.user_id = int(user_id)
                                        logger.info(f"Extracted userId from getUserDetails: {self.user_id}")
                                elif 'id' in body_data:
                                    self.user_id = int(body_data['id'])
                                    logger.info(f"Extracted userId from response: {self.user_id}")
                        except:
                            pass
                    else:
                        logger.warning(f"getUserDetails returned status {data.get('status')} - possible HTML error page")
                except Exception as e:
                    logger.warning(f"Error parsing getUserDetails response: {e}")
            logger.info("getUserDetails API called")
        except Exception as e:
            logger.warning(f"Error calling getUserDetails: {e}")

    async def _save_screenshot(self, name: str) -> None:
        """Save a screenshot for debugging purposes."""
        if self.page and self.screenshot_dir:
            try:
                path = os.path.join(self.screenshot_dir, f"{name}.png")
                await self.page.screenshot({'path': path})
                logger.info(f"Screenshot saved: {path}")
            except Exception as e:
                logger.warning(f"Failed to save screenshot {name}: {e}")

    async def _extract_session_metadata(self) -> None:
        """
        Extract userId and schoolConfigKey from the page JavaScript context.

        Looks for these values in window object or local storage.
        """
        try:
            # Try to get from window object
            logger.info("Attempting to extract userId from window object...")
            user_id = await self.page.evaluate(
                "window?.Compass?.organisationUserId"
            )
            if user_id:
                self.user_id = int(user_id)
                logger.info(f"Extracted userId: {self.user_id}")
            else:
                logger.warning("Could not extract userId from window.Compass.organisationUserId")
                logger.debug("Checking what window.Compass contains...")
                compass_obj = await self.page.evaluate("JSON.stringify(window.Compass || {})")
                logger.debug(f"window.Compass: {compass_obj[:200]}")

            # Try to get schoolConfigKey
            logger.info("Attempting to extract schoolConfigKey...")
            school_key = await self.page.evaluate(
                "window?.Compass?.referenceDataCacheKeys?.schoolConfigKey"
            )
            if school_key:
                self.school_config_key = str(school_key)
                logger.info(f"Extracted schoolConfigKey: {self.school_config_key}")
            else:
                logger.warning("Could not extract schoolConfigKey from window.Compass.referenceDataCacheKeys.schoolConfigKey")
        except Exception as e:
            logger.warning(f"Error extracting session metadata: {e}")

    async def get_calendar_events_async(
        self,
        start_date: str,  # YYYY-MM-DD
        end_date: str,    # YYYY-MM-DD
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetch calendar events from Compass for a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Maximum number of events to return (default 100)

        Returns:
            List of calendar event dictionaries
        """
        logger.info(f"Fetching calendar events from {start_date} to {end_date}")

        if not self._authenticated:
            raise Exception("Not authenticated. Call login() first.")

        # Ensure userId is extracted
        if self.user_id is None:
            logger.warning("userId not extracted yet, attempting extraction...")
            await self._extract_session_metadata()

        # If userId still not available, try to use 0 as fallback
        if self.user_id is None:
            logger.warning("userId still not extracted. Will try to use 0 as fallback (API may handle it)")
            self.user_id = 0

        # Build the API request payload
        api_url = (
            f"{self.base_url}/Services/Calendar.svc/GetCalendarEventsByUser"
            "?ExcludeNonRelevantPd=true"
        )

        payload = {
            'userId': self.user_id,
            'homePage': True,
            'activityId': None,
            'locationId': None,
            'staffIds': None,
            'startDate': start_date,
            'endDate': end_date,
            'page': 1,
            'start': 0,
            'limit': limit
        }

        logger.info(f"Calling API: {api_url}")
        logger.debug(f"Payload: {payload}")

        try:
            # Navigate to base URL first to ensure page context is set properly
            current_url = self.page.url
            if not current_url.startswith(self.base_url):
                logger.info(f"Navigating to base URL before API call: {self.base_url}")
                try:
                    await self.page.goto(self.base_url, waitUntil='domcontentloaded', timeout=15000)
                    logger.info("Base URL loaded for API context")
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.warning(f"Could not navigate to base URL: {e} (continuing anyway)")
                    await asyncio.sleep(2)

            # Add a delay before making API request
            logger.info("Waiting before API call...")
            await asyncio.sleep(1)

            # Make the API request using the authenticated session
            response_text = await self.page.evaluate(
                f"""
                async () => {{
                    try {{
                        const response = await fetch('{api_url}', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                                'X-Requested-With': 'XMLHttpRequest',
                                'Accept': 'application/json'
                            }},
                            body: JSON.stringify({json.dumps(payload)})
                        }});
                        console.log('Calendar API response status:', response.status);
                        const text = await response.text();
                        console.log('Response first 200 chars:', text.substring(0, 200));

                        // Try to parse as JSON, otherwise return raw text
                        try {{
                            const data = JSON.parse(text);
                            return JSON.stringify({{status: response.status, data: data}});
                        }} catch (e) {{
                            return JSON.stringify({{status: response.status, raw: text.substring(0, 1000), error: 'Not JSON'}});
                        }}
                    }} catch (error) {{
                        return JSON.stringify({{ error: error.message }});
                    }}
                }}
                """
            )

            response_data = json.loads(response_text)
            logger.debug(f"API Response: {response_data}")

            # Check response status
            status = response_data.get('status')
            logger.info(f"API returned status code: {status}")

            if status == 403:
                # Check if it's a Cloudflare challenge response
                raw_body = response_data.get('raw', '').lower()
                if 'cloudflare' in raw_body or 'verifying' in raw_body:
                    logger.warning("Got 403 with Cloudflare challenge - waiting and retrying...")
                    await asyncio.sleep(5)
                    # Retry the request
                    response_text = await self.page.evaluate(
                        f"""
                        async () => {{
                            try {{
                                const response = await fetch('{api_url}', {{
                                    method: 'POST',
                                    headers: {{
                                        'Content-Type': 'application/json',
                                        'X-Requested-With': 'XMLHttpRequest',
                                        'Accept': 'application/json'
                                    }},
                                    body: JSON.stringify({json.dumps(payload)})
                                }});
                                const text = await response.text();
                                try {{
                                    const data = JSON.parse(text);
                                    return JSON.stringify({{status: response.status, data: data}});
                                }} catch (e) {{
                                    return JSON.stringify({{status: response.status, raw: text.substring(0, 1000), error: 'Not JSON'}});
                                }}
                            }} catch (error) {{
                                return JSON.stringify({{ error: error.message }});
                            }}
                        }}
                        """
                    )
                    response_data = json.loads(response_text)
                    status = response_data.get('status')
                    logger.info(f"Retry returned status code: {status}")

            if status != 200:
                logger.error(f"API returned non-200 status: {status}")
                if response_data.get('raw'):
                    logger.error(f"Response body: {response_data['raw'][:500]}")
                raise Exception(f"API returned status {status}")

            # Check for errors in response
            if 'error' in response_data:
                raise Exception(f"API error: {response_data['error']}")

            # Extract actual events from response
            data = response_data.get('data')
            if isinstance(data, dict) and 'd' in data:
                events = data['d']
            else:
                events = data if isinstance(data, list) else []

            result = events if isinstance(events, list) else []
            logger.info(f"Successfully fetched {len(result)} calendar events")
            return result

        except Exception as e:
            logger.error(f"Failed to fetch calendar events: {e}", exc_info=True)
            raise Exception(f"Failed to fetch calendar events: {e}")

    def get_calendar_events(
        self,
        start_date: str,
        end_date: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Synchronous wrapper for get_calendar_events_async.
        """
        loop = self._get_event_loop()
        return loop.run_until_complete(self.get_calendar_events_async(start_date, end_date, limit))

    async def close_async(self) -> None:
        """Close the browser and clean up resources."""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()

    def close(self) -> None:
        """Synchronous wrapper for close_async."""
        loop = self._get_event_loop()
        if not loop.is_closed():
            loop.run_until_complete(self.close_async())
