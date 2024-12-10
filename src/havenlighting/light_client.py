from typing import Dict, Any, List
from .exceptions import AuthenticationError
from .base_client import BaseClient

class LightClient(BaseClient):
    """Handles light-related API calls."""

    def fetch_location_lights_and_zones(self, location_id: int) -> Dict[str, Any]:
        """Fetch lights and zones for a specific location.
        
        Args:
            location_id: Integer ID of the location
        """
        if not self.is_authenticated:
            raise AuthenticationError("Authentication required")

        url = f"{self.base_url}/Light/OrderedLightsAndZones"
        params = {"locationId": location_id}
        return self._make_request("GET", url, params=params)

    def control_light(self, location_id: int, light_ids: List[int], turn_on: bool = True) -> Dict[str, Any]:
        """Control one or more lights at a location.
        
        Args:
            location_id: Integer ID of the location
            light_ids: List of light IDs to control
            turn_on: True to turn lights on, False to turn them off
        """
        if not self.is_authenticated:
            raise AuthenticationError("Authentication required")

        url = f"{self.base_url}/Light/CommandV1"
        params = {"locationId": location_id}
        
        payload = {
            "lightingStatusId": 2 if turn_on else 1,
            "lightBrightnessId": 63,
            "lightColorId": 63,
            "patternSpeedId": 63,
            "selectedLightIds": light_ids,
            "locationId": location_id
        }

        return self._make_request("POST", url, params=params, json=payload) 