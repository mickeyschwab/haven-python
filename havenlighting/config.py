"""Configuration constants for Haven Lighting API."""

from typing import Final

# API Configuration
API_TIMEOUT: Final[int] = 30

# Light States
LIGHT_STATE: Final[dict] = {
    "OFF": 1,
    "ON": 2
}

# Default Light Parameters (brightness is 0-10 on Haven's scale)
LIGHT_PARAMS: Final[dict] = {
    "BRIGHTNESS": 10,
    "COLOR": 63,
    "PATTERN_SPEED": 63
}

# API Configuration
API_BASE: Final[str] = "https://stg-api.havenlighting.com/api"
APP_SOURCE: Final[str] = "REACT_NATIVE"
APP_VERSION: Final[str] = "1.6" 