import logging
from typing import Dict, Any, Optional
from .credentials import Credentials
from .devices.light import Light
from .devices.location import Location
from .exceptions import AuthenticationError, ApiError

logger = logging.getLogger(__name__)

class HavenClient:
    """Main client for interacting with Haven Lighting devices."""
    
    def __init__(self) -> None:
        self._credentials: Optional[Credentials] = None
        self._locations: Dict[int, Location] = {}
        self._lights: Dict[int, Light] = {}
        logger.debug("Initialized HavenClient")

    def authenticate(self, email: str, password: str) -> bool:
        """
        Authenticate with the Haven Lighting service.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            bool: True if authentication successful, False otherwise
            
        Raises:
            ApiError: If API request fails
        """
        try:
            self._credentials = Credentials()
            authenticated = self._credentials.authenticate(email, password)
            if authenticated:
                logger.info("Successfully authenticated user: %s", email)
            else:
                logger.warning("Authentication failed for user: %s", email)
            return authenticated
        except ApiError as e:
            logger.error("API error during authentication: %s", str(e))
            raise

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