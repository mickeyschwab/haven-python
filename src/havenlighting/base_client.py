from typing import Dict, Optional, Any
import requests
from .exceptions import ApiError

class BaseClient:
    """Base class for API clients with common functionality."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self._token: Optional[str] = None
        self._user_id: Optional[str] = None 
        self._refresh_token: Optional[str] = None

    @property
    def is_authenticated(self) -> bool:
        """Check if client is authenticated with valid token."""
        return bool(self._token and self._user_id)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling and auth headers."""
        if self._token:
            headers = kwargs.pop("headers", {})
            headers["Authorization"] = f"Bearer {self._token}"
            kwargs["headers"] = headers

        try:
            response = requests.request(method, endpoint, **kwargs)
            response.raise_for_status()
            data = response.json()

            if not data.get("success"):
                raise ApiError(data.get("message", "Unknown API error"))

            return {"success": True, "data": data.get("data")}

        except requests.exceptions.RequestException as e:
            raise ApiError(str(e)) 