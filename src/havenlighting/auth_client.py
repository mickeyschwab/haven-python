from typing import Dict, Any, Optional
import requests
from .models import AuthResponse
from .exceptions import AuthenticationError, ApiError
from .base_client import BaseClient

class AuthClient(BaseClient):
    """Handles authentication-related API calls."""
    
    DEVICE_ID = "HavenLightingMobile"

    def authenticate(self, email: str, password: str) -> AuthResponse:
        """Authenticate with Haven Lighting and store the token and user_id."""
        url = f"{self.base_url}/User/authenticate"
        payload = {
            "email": email,
            "password": password,
            "deviceId": self.DEVICE_ID,
        }

        try:
            response = self._make_request("POST", url, json=payload)
            data = response["data"]
            self._token = data["token"]
            self._refresh_token = data["refreshToken"] 
            self._user_id = data["id"]
            return AuthResponse(
                success=True,
                token=self._token,
                refresh_token=self._refresh_token,
                user_id=self._user_id
            )
        except ApiError as e:
            return AuthResponse(success=False, message=str(e))

    def refresh_access_token(self) -> Dict[str, Any]:
        """Attempt to refresh the token using the stored refresh token."""
        if not self._refresh_token or not self._user_id:
            raise AuthenticationError("Missing refresh token or user ID")

        url = f"{self.base_url}/User/refresh"
        payload = {
            "refreshToken": self._refresh_token,
            "userId": self._user_id,
        }

        response = self._make_request("POST", url, json=payload)
        self._token = response["data"]["token"]
        return response

    def fetch_user_details(self) -> Dict[str, Any]:
        """Fetch authenticated user details."""
        if not self.is_authenticated:
            raise AuthenticationError("Authentication required")

        url = f"{self.base_url}/User/DetailInfo/{self._user_id}"
        return self._make_request("GET", url) 