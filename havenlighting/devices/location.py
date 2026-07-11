from typing import Dict, Any, Optional
import logging
from ..models import LocationData
from .light import Light
from ..credentials import Credentials
from ..exceptions import ApiError

logger = logging.getLogger(__name__)

class Location:
    """
    Represents a Haven location with its associated lights.

    Attributes:
        credentials: Credentials object for API requests
        location_id: Unique identifier for the location
        name: Location name
    """

    def __init__(self, credentials: Credentials, location_id: int, data: Optional[Dict[str, Any]] = None) -> None:
        self._credentials = credentials
        self._location_id = location_id
        self._data = LocationData(
            location_id=location_id,
            name=data.get("name", "")
        ) if data else None
        self._lights: Dict[int, Light] = {}
        logger.debug("Initialized Location: %s (ID: %d)", self.name, location_id)

    @property
    def name(self) -> str:
        """Get location name."""
        return self._data.name if self._data else ""

    @classmethod
    def discover(cls, credentials: Credentials) -> Dict[int, 'Location']:
        """
        Discover the authenticated user's default location.

        Only the account's default location is returned — `/user/GetUserInfo/`
        doesn't expose the other locations a multi-location account might
        have (the old pre-2025 API did, via a since-decommissioned endpoint).
        Revisit this if a verified capture ever turns up the 2025 equivalent.

        Args:
            credentials: Authenticated credentials object

        Returns:
            Dictionary of location_id to Location objects

        Raises:
            AuthenticationError: If not authenticated
            ApiError: If API request fails or the response is missing the
                expected default location
        """
        response = credentials.make_request("GET", "/user/GetUserInfo/")

        if "defaultLocationId" not in response:
            raise ApiError("GetUserInfo response is missing defaultLocationId")

        location_id = int(response["defaultLocationId"])
        owner_name = f"{response.get('firstName', '')} {response.get('lastName', '')}".strip()
        return {
            location_id: cls(credentials, location_id, {"name": owner_name})
        }

    def get_lights(self) -> Dict[int, Light]:
        """Get all lights for this location."""
        logger.debug("Fetching lights for location: %s (ID: %d)", self.name, self._location_id)

        try:
            response = self._credentials.make_request(
                "GET",
                f"/Location/InformationSummaryWithAllZonesGroup/{self._location_id}"
            )

            if self._data and response.get("name"):
                self._data.name = response["name"]

            self._lights = {}
            for light_data in response.get("lights", []):
                light_id = int(light_data["lightId"])
                self._lights[light_id] = Light(
                    self._credentials,
                    self._location_id,
                    light_id,
                    light_data
                )
            logger.info("Found %d lights for location: %s", len(self._lights), self.name)
        except Exception as e:
            logger.error("Failed to fetch lights for location %d: %s", self._location_id, str(e))
            raise

        return self._lights
