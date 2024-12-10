from typing import Dict, Any, Optional
from .light import Light
from ..exceptions import AuthenticationError

class Location:
    """Represents a Haven location with its associated lights."""
    
    def __init__(self, credentials, location_id: int, data: Optional[Dict[str, Any]] = None):
        self.credentials = credentials
        self.location_id = location_id
        self._data = data or {}
        self._lights: Dict[int, Light] = {}
        
    @property
    def name(self) -> str:
        return self._data.get("ownerName", "")
        
    @classmethod
    def discover(cls, credentials) -> Dict[int, 'Location']:
        """Discover all locations available to the authenticated user."""
        response = credentials.make_request(
            "GET",
            "/Location/OrderedLocationV2",
            params={"minimumCapabilityLevel": 0},
            use_prod_api=True
        )
        
        locations = {}
        for loc_data in response.get("data", []):
            location_id = int(loc_data["locationId"])
            locations[location_id] = cls(credentials, location_id, loc_data)
        return locations
        
    def update(self) -> None:
        """Update location details."""
        response = self.credentials.make_request(
            "GET", 
            f"/Location/InformationSummary/{self.location_id}",
            use_prod_api=True
        )
        self._data = response["data"]

    def get_lights(self) -> Dict[int, Light]:
        """Get all lights for this location."""
        if not self._lights:
            response = self.credentials.make_request(
                "GET",
                "/Light/OrderedLightsAndZones",
                params={"locationId": self.location_id}
            )
            
            for light_data in response["data"]["lights"]:
                light_id = int(light_data["lightId"])
                self._lights[light_id] = Light(
                    self.credentials,
                    self.location_id,
                    light_id,
                    light_data
                )
                
        return self._lights