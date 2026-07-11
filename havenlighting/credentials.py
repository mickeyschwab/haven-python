from typing import Any, Dict, Optional
from curl_cffi import requests
from curl_cffi.requests.exceptions import RequestException
import logging
from .exceptions import AuthenticationError, ApiError
from .config import API_BASE, API_TIMEOUT, APP_SOURCE, APP_VERSION

logger = logging.getLogger(__name__)

class Credentials:
    """Handles authentication and request credentials."""

    def __init__(self):
        self._token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._user_id: Optional[int] = None
        # impersonate="chrome": Haven's Azure Front Door WAF blocks the TLS
        # fingerprint of plain requests/urllib3 (403 "request is blocked",
        # verified against real headers/UA too) but passes curl and browser
        # fingerprints. A Session (vs. a fresh request each call) also avoids
        # re-negotiating that fingerprint/TLS handshake on every API call.
        self._session = requests.Session(impersonate="chrome")
        logger.debug("Initialized Credentials")

    @property
    def is_authenticated(self) -> bool:
        return bool(self._token and self._user_id)

    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate with the Haven Lighting service."""
        logger.debug("Attempting authentication for user: %s", email)
        payload = {
            "username": email,
            "password": password,
        }

        try:
            response = self._make_request_internal(
                "POST",
                "/Auth/authenticate",
                json=payload,
                auth_required=False
            )
            if not response.get("token"):
                logger.error("Authentication failed for user %s: no token in response", email)
                return False
            self._update_credentials(response)
            logger.info("Successfully authenticated user: %s", email)
            return True

        except ApiError as e:
            logger.error("Authentication failed for user %s: %s", email, str(e))
            return False

    def refresh_token(self) -> bool:
        """Refresh the authentication token."""
        if not self._refresh_token or not self._user_id:
            logger.debug("Cannot refresh token - missing refresh token or user ID")
            return False

        try:
            logger.debug("Attempting token refresh for user ID: %s", self._user_id)
            response = self._make_request_internal(
                "POST",
                "/Auth/refresh",
                json={
                    "refreshToken": self._refresh_token,
                    "userId": self._user_id
                },
                auth_required=False
            )
            self._update_credentials(response)
            logger.info("Token refresh successful")
            return True

        except ApiError as e:
            logger.error("Token refresh failed: %s", str(e))
            return False

    def _update_credentials(self, data: Dict[str, Any]) -> None:
        """Update stored credentials from API response."""
        try:
            self._token = data["token"]
            self._refresh_token = data["refreshToken"]
            self._user_id = data["id"]
        except KeyError as e:
            raise ApiError(f"Auth response missing expected field: {e}")

    def make_request(
        self,
        method: str,
        path: str,
        auth_required: bool = True,
        timeout: int = API_TIMEOUT,
        **kwargs: Any
    ) -> Any:
        """Make an authenticated API request with automatic token refresh."""
        try:
            return self._make_request_internal(
                method=method,
                path=path,
                auth_required=auth_required,
                timeout=timeout,
                **kwargs
            )
        except AuthenticationError:
            logger.info("Authentication error, attempting token refresh")
            if self.refresh_token():
                logger.info("Token refresh successful, retrying request")
                return self._make_request_internal(
                    method=method,
                    path=path,
                    auth_required=auth_required,
                    timeout=timeout,
                    **kwargs
                )
            logger.error("Token refresh failed, unable to retry request")
            raise AuthenticationError("Token refresh failed")

    def _make_request_internal(
        self,
        method: str,
        path: str,
        auth_required: bool = True,
        timeout: int = API_TIMEOUT,
        **kwargs: Any
    ) -> Any:
        """Internal method for making API requests."""
        if auth_required and not self.is_authenticated:
            raise AuthenticationError("Authentication required")

        url = f"{API_BASE}{path}"

        headers = kwargs.pop("headers", {})
        headers.setdefault("Accept", "application/json")
        headers["app-haven-source"] = APP_SOURCE
        headers["app-haven-version"] = APP_VERSION
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        kwargs["headers"] = headers

        try:
            response = self._session.request(method, url, timeout=timeout, **kwargs)
        except RequestException as e:
            logger.error("Request failed: %s", str(e))
            raise ApiError(f"Request failed: {str(e)}")

        if response.status_code == 401:
            raise AuthenticationError("Received 401 Unauthorized response")

        if not response.ok:
            raise ApiError(self._extract_error_message(response), code=response.status_code)

        if not response.content:
            return {}

        return response.json()

    @staticmethod
    def _extract_error_message(response: Any) -> str:
        """Build an error message from an application/problem+json body, if present."""
        try:
            error_data = response.json()
        except ValueError:
            return response.text

        message = error_data.get("title") or error_data.get("message") or response.text

        # ASP.NET validation errors: {"errors": {"Field": ["reason", ...]}}
        errors = error_data.get("errors")
        if isinstance(errors, dict) and errors:
            detail = "; ".join(
                f"{field}: {', '.join(reasons)}" for field, reasons in errors.items()
            )
            message = f"{message}: {detail}" if message else detail

        return message
