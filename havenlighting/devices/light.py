from typing import Dict, Any, Optional, List
from ..credentials import Credentials

class Light:
    """Represents a Haven light device."""

    def __init__(self, credentials: Credentials, location_id: int, light_id: int, data: Dict[str, Any]) -> None:
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

    @property
    def is_on(self) -> bool:
        """Return True if light is on."""
        return self._state

    def turn_on(self) -> None:
        """Turn the light on."""
        self._send_command(2)  # 2 = ON state
        self._state = True

    def turn_off(self) -> None:
        """Turn the light off."""
        self._send_command(1)  # 1 = OFF state
        self._state = False
        
    def _send_command(self, status_id: int) -> None:
        """Send a command to the light."""
        self._credentials.make_request(
            "POST",
            "/Light/CommandV1",
            params={"locationId": self.location_id},
            json={
                "lightingStatusId": status_id,
                "lightBrightnessId": 63,
                "lightColorId": 63,
                "patternSpeedId": 63,
                "selectedLightIds": [self.id],
                "locationId": self.location_id
            }
        )