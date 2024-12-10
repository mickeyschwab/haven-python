from typing import Dict, Any, Optional
import requests
from .exceptions import AuthenticationError, ApiError

class Credentials:
    """Handles authentication and request credentials."""
    
    DEVICE_ID = "HavenLightingMobile"
    AUTH_API_BASE = "https://havenwebservices-apiapp-test.azurewebsites.net/api/v2"
    PROD_API_BASE = "https://ase-hvnlght-residential-api-prod.azurewebsites.net/api"
    
    def __init__(self):
        self._token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._user_id: Optional[str] = None
        
    @property
    def is_authenticated(self) -> bool:
        return bool(self._token and self._user_id)
        
    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate with the Haven Lighting service."""
        payload = {
            "email": email,
            "password": password,
            "deviceId": self.DEVICE_ID,
        }
        
        try:
            response = self.make_request(
                "POST",
                "/User/authenticate",
                json=payload,
                auth_required=False,
                use_prod_api=False
            )
            data = response["data"]
            self._token = data["token"]
            self._refresh_token = data["refreshToken"]
            self._user_id = data["id"]
            return True
            
        except ApiError:
            return False
            
    def make_request(
        self, 
        method: str, 
        path: str, 
        auth_required: bool = True,
        use_prod_api: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Make an authenticated API request."""
        if auth_required and not self.is_authenticated:
            raise AuthenticationError("Authentication required")
            
        base_url = self.PROD_API_BASE if use_prod_api else self.AUTH_API_BASE
        url = f"{base_url}{path}"
        
        if self._token:
            headers = kwargs.pop("headers", {})
            headers["Authorization"] = f"Bearer {self._token}"
            kwargs["headers"] = headers
            
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success"):
            raise ApiError(data.get("message", "Unknown API error"))
            
        return data 