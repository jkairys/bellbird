"""
Compass Education API client.

Handles authentication and calendar event fetching without browser automation.
Uses HTTP requests with proper cookie handling for session management.
"""

import json
import re
from logging import getLogger
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from .exceptions import CompassAuthenticationError, CompassClientError

logger = getLogger(__name__)


class CompassClient:
    """
    Python client for Compass Education API.

    Handles authentication and calendar event fetching without browser automation.
    """

    def __init__(self, base_url: str, username: str, password: str):
        """
        Initialize Compass client.

        Args:
            base_url: Base URL of Compass instance (e.g., "https://compass.example.com")
            username: Compass username
            password: Compass password
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.session = requests.Session()
        self._setup_session_headers()
        self.user_id: Optional[int] = None
        self.school_config_key: Optional[str] = None
        self._authenticated = False

    def _setup_session_headers(self) -> None:
        """
        Set up realistic browser headers to avoid being blocked.

        Compass may block requests that don't look like they come from a real browser.
        """
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/142.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-AU,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )

    def login(self) -> bool:
        """
        Authenticate with Compass by submitting login form.

        Returns:
            True if successful

        Raises:
            CompassAuthenticationError: If login fails
        """
        login_url = f"{self.base_url}/login.aspx?sessionstate=disabled"

        logger.info("Attempting to log in to Compass at %s", login_url)

        try:
            response = self.session.get(login_url, timeout=10)
            response.raise_for_status()

            form_data = self._extract_form_fields(response.text)

            form_data["username"] = self.username
            form_data["password"] = self.password
            form_data["rememberMeChk"] = "on"

            headers = {
                "Referer": login_url,
                "Origin": self.base_url,
            }

            response = self.session.post(
                login_url, data=form_data, headers=headers, allow_redirects=True, timeout=10
            )
            response.raise_for_status()

            if "login.aspx" in response.url.lower():
                raise CompassAuthenticationError("Login failed: Invalid credentials or server error")

            self._extract_session_metadata(response.text)

            self._authenticated = True
            return True

        except requests.RequestException as e:
            raise CompassClientError(f"Login request failed: {e}") from e

    def _extract_form_fields(self, html_content: str) -> Dict[str, str]:
        """
        Extract all form fields from the login page HTML.

        This includes hidden fields like __VIEWSTATE and __VIEWSTATEGENERATOR
        which are required by ASP.NET forms.

        Args:
            html_content: HTML content of the login page

        Returns:
            Dictionary of form field names and values (empty dict if no form found)
        """
        soup = BeautifulSoup(html_content, "html.parser")
        form_data = {}

        form = soup.find("form")
        if not form:
            return {}

        for input_field in form.find_all("input"):
            name = input_field.get("name")
            value = input_field.get("value", "")
            if name:
                form_data[name] = value

        if "__EVENTTARGET" not in form_data:
            form_data["__EVENTTARGET"] = "button1"
        if "__EVENTARGUMENT" not in form_data:
            form_data["__EVENTARGUMENT"] = ""

        return form_data

    def _extract_session_metadata(self, html_content: str) -> None:
        """
        Extract userId and schoolConfigKey from HTML response.

        These are usually embedded in JavaScript or window object.
        We'll look for them in the initial page load response.
        """
        user_id_match = re.search(r'organisationUserId["\']?\s*[:=]\s*(\d+)', html_content)
        if user_id_match:
            self.user_id = int(user_id_match.group(1))

        key_match = re.search(r'schoolConfigKey["\']?\s*[:=]\s*["\']([^"\']+)["\']', html_content)
        if key_match:
            self.school_config_key = key_match.group(1)

    def _ensure_session_metadata(self) -> None:
        """
        Fetch session metadata if not already extracted.

        Makes a request to the home page or an API endpoint to get
        userId and schoolConfigKey if they weren't available after login.
        """
        if self.user_id is None:
            response = self.session.get(f"{self.base_url}/home.aspx", timeout=10)
            self._extract_session_metadata(response.text)

        if self.user_id is None:
            raise CompassClientError("Failed to extract userId from Compass session")

    def get_user_details(self, target_user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Fetch detailed user information from Compass.

        Args:
            target_user_id: User ID to fetch details for (defaults to current user)

        Returns:
            Dictionary containing user details

        Raises:
            CompassClientError: If not authenticated or request fails
        """
        if not self._authenticated:
            raise CompassClientError("Not authenticated. Call login() first.")

        self._ensure_session_metadata()

        user_id = target_user_id if target_user_id is not None else self.user_id

        api_url = f"{self.base_url}/Services/User.svc/GetUserDetailsBlobByUserId"

        payload = {"targetUserId": user_id}

        try:
            response = self.session.post(
                api_url,
                json=payload,
                headers={"Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest"},
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()

            if isinstance(data, dict) and "d" in data:
                user_details = data["d"]
            else:
                user_details = data

            return user_details if isinstance(user_details, dict) else {}

        except requests.RequestException as e:
            raise CompassClientError(f"Failed to fetch user details: {e}") from e
        except json.JSONDecodeError as e:
            raise CompassClientError(f"Invalid JSON response from Compass: {e}") from e

    def get_calendar_events(
        self, start_date: str, end_date: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetch calendar events from Compass for a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Maximum number of events to return (default 100)

        Returns:
            List of calendar event dictionaries

        Raises:
            CompassClientError: If not authenticated or request fails
        """
        if not self._authenticated:
            raise CompassClientError("Not authenticated. Call login() first.")

        self._ensure_session_metadata()

        api_url = (
            f"{self.base_url}/Services/Calendar.svc/GetCalendarEventsByUser"
            "?sessionstate=readonly&ExcludeNonRelevantPd=true"
        )

        payload = {
            "userId": self.user_id,
            "homePage": True,
            "activityId": None,
            "locationId": None,
            "staffIds": None,
            "startDate": start_date,
            "endDate": end_date,
            "page": 1,
            "start": 0,
            "limit": limit,
        }

        try:
            response = self.session.post(
                api_url,
                json=payload,
                headers={"Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest"},
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()

            if isinstance(data, dict) and "d" in data:
                events = data["d"]
            else:
                events = data

            return events if isinstance(events, list) else []

        except requests.RequestException as e:
            raise CompassClientError(f"Failed to fetch calendar events: {e}") from e
        except json.JSONDecodeError as e:
            raise CompassClientError(f"Invalid JSON response from Compass: {e}") from e

    def close(self) -> None:
        """Close the session."""
        self.session.close()
