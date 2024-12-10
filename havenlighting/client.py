from typing import Dict, Any, Optional
from .credentials import Credentials
from .devices.light import Light
from .devices.location import Location
from .exceptions import AuthenticationError

class HavenClient:
    """Main client for interacting with Haven Lighting devices."""
    
    def __init__(self):
        self._credentials: Optional[Credentials] = None
        self._locations: Dict[int, Location] = {}
        self._lights: Dict[int, Light] = {}

    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate with the Haven Lighting service."""
        self._credentials = Credentials()
        return self._credentials.authenticate(email, password)

    def get_location(self, location_id: int) -> Location:
        """Get a location by ID."""
        if not self._credentials:
            raise AuthenticationError("Not authenticated")
            
        if location_id not in self._locations:
            self._locations[location_id] = Location(self._credentials, location_id)
        
        return self._locations[location_id]

    def discover_locations(self) -> Dict[int, Location]:
        """Discover all available locations."""
        if not self._credentials:
            raise AuthenticationError("Not authenticated")
            
        locations = Location.discover(self._credentials)
        self._locations.update(locations)
        return self._locations 