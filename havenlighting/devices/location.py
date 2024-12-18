from typing import Dict, Any, Optional, ClassVar
from ..models import LocationData
from .light import Light
from ..credentials import Credentials
from ..exceptions import AuthenticationError

class Location:
    """
    Represents a Haven location with its associated lights.
    
    Attributes:
        credentials: Credentials object for API requests
        location_id: Unique identifier for the location
        name: Location name
    """
    
    MIN_CAPABILITY_LEVEL: ClassVar[int] = 0
    
    def __init__(self, credentials: Credentials, location_id: int, data: Optional[Dict[str, Any]] = None) -> None:
        self._credentials = credentials
        self._location_id = location_id
        self._data = LocationData(
            location_id=location_id,
            name=data.get("name", ""),
            owner_name=data.get("ownerName", "")
        ) if data else None
        self._lights: Dict[int, Light] = {}
        
    @property
    def name(self) -> str:
        """Get location name."""
        return self._data.owner_name if self._data else ""
        
    @classmethod
    def discover(cls, credentials: Credentials) -> Dict[int, 'Location']:
        """
        Discover all locations available to the authenticated user.
        
        Args:
            credentials: Authenticated credentials object
            
        Returns:
            Dictionary of location_id to Location objects
            
        Raises:
            AuthenticationError: If not authenticated
            ApiError: If API request fails
        """
        response = credentials.make_request(
            "GET",
            "/Location/OrderedLocationV2",
            params={"minimumCapabilityLevel": cls.MIN_CAPABILITY_LEVEL},
            use_prod_api=True
        )
        
        locations = {}
        for loc_data in response.get("data", []):
            location_id = int(loc_data["locationId"])
            locations[location_id] = cls(credentials, location_id, loc_data)
        return locations
        
    def update(self) -> None:
        """Update location details."""
        response = self._credentials.make_request(
            "GET", 
            f"/Location/InformationSummary/{self._location_id}",
            use_prod_api=True
        )
        self._data = response["data"]

    def get_lights(self) -> Dict[int, Light]:
        """Get all lights for this location."""
        if not self._lights:
            response = self._credentials.make_request(
                "GET",
                "/Light/OrderedLightsAndZones",
                params={"locationId": self._location_id}
            )
            
            for light_data in response["data"]["lights"]:
                light_id = int(light_data["lightId"])
                self._lights[light_id] = Light(
                    self._credentials,
                    self._location_id,
                    light_id,
                    light_data
                )
                
        return self._lights