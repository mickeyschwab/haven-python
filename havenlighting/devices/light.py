from typing import Dict, Any, Optional
from ..credentials import Credentials

class Light:
    """Represents a Haven light device."""

    def __init__(self, credentials: Credentials, location_id: int, light_id: int, data: Dict[str, Any]):
        self._credentials = credentials
        self._data = data
        self.location_id = location_id
        self._id = int(data["lightId"])
        self._name = data["name"]
        self._state = False

    @property
    def id(self) -> int:
        """Return light ID."""
        return self._id

    @property
    def name(self) -> str:
        """Return light name."""
        return self._name

    def turn_on(self) -> None:
        """Turn the light on."""
        self._credentials.make_request(
            "POST",
            "/Light/CommandV1",
            params={"locationId": self.location_id},
            json={
                "lightingStatusId": 2,
                "lightBrightnessId": 63,
                "lightColorId": 63,
                "patternSpeedId": 63,
                "selectedLightIds": [self.id],
                "locationId": self.location_id
            }
        )
        self._state = True

    def turn_off(self) -> None:
        """Turn the light off."""
        self._credentials.make_request(
            "POST",
            "/Light/CommandV1",
            params={"locationId": self.location_id},
            json={
                "lightingStatusId": 1,
                "lightBrightnessId": 63,
                "lightColorId": 63,
                "patternSpeedId": 63,
                "selectedLightIds": [self.id],
                "locationId": self.location_id
            }
        )
        self._state = False