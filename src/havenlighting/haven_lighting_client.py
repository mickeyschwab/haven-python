from typing import Optional
from .auth_client import AuthClient
from .location_client import LocationClient
from .light_client import LightClient

class HavenLightingClient:
    """Main client that combines all Haven Lighting API functionality."""

    API_VERSION = "v2"

    def __init__(self, base_url: str):
        """Initialize the Haven Lighting client."""
        self.base_url = base_url
        self.auth = AuthClient(base_url)
        self.locations = LocationClient(base_url)
        self.lights = LightClient(base_url)

    def _sync_auth_state(self):
        """Sync authentication state between all clients."""
        self.locations._token = self.auth._token
        self.locations._user_id = self.auth._user_id
        self.locations._refresh_token = self.auth._refresh_token
        
        self.lights._token = self.auth._token
        self.lights._user_id = self.auth._user_id
        self.lights._refresh_token = self.auth._refresh_token

    def authenticate(self, email: str, password: str):
        """Authenticate and sync state across all clients."""
        response = self.auth.authenticate(email, password)
        if response.success:
            self._sync_auth_state()
        return response

    @property
    def is_authenticated(self) -> bool:
        """Check if client is authenticated."""
        return self.auth.is_authenticated 