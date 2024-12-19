from typing import Dict, Any, Optional, Callable
import requests
from functools import wraps
from .exceptions import AuthenticationError, ApiError
import logging
from .config import DEVICE_ID, AUTH_API_BASE, PROD_API_BASE, API_TIMEOUT

logger = logging.getLogger(__name__)

def refresh_on_auth_error(func: Callable) -> Callable:
    """Decorator to refresh token and retry on authentication errors."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except AuthenticationError:
            logger.info("Authentication error, attempting token refresh")
            if self.refresh_token():
                logger.info("Token refresh successful, retrying request")
                return func(self, *args, **kwargs)
            logger.error("Token refresh failed, unable to retry request")
            raise
    return wrapper

class Credentials:
    """Handles authentication and request credentials."""
    
    def __init__(self):
        self._token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._user_id: Optional[int] = None
        logger.debug("Initialized Credentials")
        
    @property
    def is_authenticated(self) -> bool:
        return bool(self._token and self._user_id)
        
    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate with the Haven Lighting service."""
        logger.debug("Attempting authentication for user: %s", email)
        payload = {
            "email": email,
            "password": password,
            "deviceId": DEVICE_ID,
        }
        
        try:
            response = self._make_request_internal(
                "POST",
                "/User/authenticate",
                json=payload,
                auth_required=False
            )
            if not response["success"] or not response["data"]:
                logger.error("Authentication failed for user %s: %s", email, response["message"])
                return False
            self._update_credentials(response["data"])
            logger.info("Successfully authenticated user: %s", email)
            return True
            
        except ApiError as e:
            logger.error("Authentication failed for user %s: %s", email, str(e))
            return False
            
    def refresh_token(self) -> bool:
        """Refresh the authentication token."""
        if not self._refresh_token or not self._user_id:
            return False
            
        try:
            response = self._make_request_internal(
                "POST",
                "/User/refresh",
                json={
                    "refreshToken": self._refresh_token,
                    "userId": self._user_id
                },
                auth_required=False
            )
            self._update_credentials(response["data"])
            return True
            
        except ApiError as e:
            logger.error("Token refresh failed: %s", str(e))
            return False
            
    def _update_credentials(self, data: Dict[str, Any]) -> None:
        """Update stored credentials from API response."""
        self._token = data["token"]
        self._refresh_token = data["refreshToken"]
        self._user_id = data["id"]
        
    @refresh_on_auth_error
    def make_request(
        self, 
        method: str, 
        path: str, 
        auth_required: bool = True,
        use_prod_api: bool = False,
        timeout: int = API_TIMEOUT,
        **kwargs
    ) -> Dict[str, Any]:
        """Make an authenticated API request with automatic token refresh."""
        return self._make_request_internal(
            method, path, auth_required, use_prod_api, timeout, **kwargs
        )
        
    def _make_request_internal(
        self, 
        method: str, 
        path: str, 
        auth_required: bool = True,
        use_prod_api: bool = False,
        timeout: int = API_TIMEOUT,
        **kwargs
    ) -> Dict[str, Any]:
        """Internal method for making API requests."""
        if auth_required and not self.is_authenticated:
            raise AuthenticationError("Authentication required")
            
        base_url = PROD_API_BASE if use_prod_api else AUTH_API_BASE
        url = f"{base_url}{path}"
        
        if self._token:
            headers = kwargs.pop("headers", {})
            headers["Authorization"] = f"Bearer {self._token}"
            kwargs["headers"] = headers
            
        try:
            response = requests.request(method, url, timeout=timeout, **kwargs)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("success"):
                if response.status_code == 401:
                    raise AuthenticationError(data.get("message", "Token expired"))
                raise ApiError(data.get("message", "Unknown API error"))
                
            return data
        except requests.exceptions.RequestException as e:
            logger.error("Request failed: %s", str(e))
            raise ApiError(f"Request failed: {str(e)}") 