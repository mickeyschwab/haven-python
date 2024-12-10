from typing import Dict, Any
from .exceptions import AuthenticationError
from .base_client import BaseClient

class LocationClient(BaseClient):
    """Handles location-related API calls."""

    PROD_API_BASE = "https://ase-hvnlght-residential-api-prod.azurewebsites.net/api"

    def fetch_location_list(self) -> Dict[str, Any]:
        """Fetch the list of locations for the authenticated user."""
        if not self.is_authenticated:
            raise AuthenticationError("Authentication required")

        url = f"{self.PROD_API_BASE}/Location/OrderedLocationV2"
        params = {"minimumCapabilityLevel": 0}
        return self._make_request("GET", url, params=params)

    def fetch_location_details(self, location_id: int) -> Dict[str, Any]:
        """Fetch detailed information about a specific location."""
        if not self.is_authenticated:
            raise AuthenticationError("Authentication required")

        url = f"{self.PROD_API_BASE}/Location/InformationSummary/{location_id}"
        return self._make_request("GET", url)

    def fetch_location_capabilities(self, location_id: int) -> Dict[str, Any]:
        """Fetch capabilities for devices at a specific location."""
        if not self.is_authenticated:
            raise AuthenticationError("Authentication required")

        url = f"{self.PROD_API_BASE}/LocationCapabilities/Devices/{location_id}"
        return self._make_request("GET", url) 