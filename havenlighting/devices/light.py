from typing import Dict, Any
from ..models import LightData
from ..config import LIGHT_STATE, LIGHT_PARAMS
from ..credentials import Credentials

class Light:
    """Represents a Haven light device."""

    def __init__(self, credentials: Credentials, location_id: int, light_id: int, data: Dict[str, Any]) -> None:
        self._credentials = credentials
        self.location_id = location_id
        self._data = LightData(
            light_id=int(data["lightId"]),
            name=data["name"],
            status=data.get("lightingStatusId", LIGHT_STATE["OFF"]),
            brightness=data.get("brightness", LIGHT_PARAMS["BRIGHTNESS"]),
            color=data.get("color", LIGHT_PARAMS["COLOR"]),
            pattern_speed=data.get("patternSpeed", LIGHT_PARAMS["PATTERN_SPEED"])
        )

    @property
    def id(self) -> int:
        return self._data.light_id

    @property
    def name(self) -> str:
        return self._data.name

    @property
    def is_on(self) -> bool:
        return self._data.status == LIGHT_STATE["ON"]

    def turn_on(self) -> None:
        """Turn the light on."""
        self._send_command(2)  # 2 = ON state
        self._data.status = LIGHT_STATE["ON"]

    def turn_off(self) -> None:
        """Turn the light off."""
        self._send_command(1)  # 1 = OFF state
        self._data.status = LIGHT_STATE["OFF"]
        
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