from dataclasses import dataclass
from typing import Optional

@dataclass
class LightData:
    """Data model for light attributes."""
    light_id: int
    name: str
    status: int
    brightness: int = 63
    color: int = 63
    pattern_speed: int = 63

@dataclass
class LocationData:
    """Data model for location attributes."""
    location_id: int
    name: str
    owner_name: Optional[str] = None 