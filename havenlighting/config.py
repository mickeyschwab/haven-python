"""Configuration constants for Haven Lighting API."""

from typing import Final

# API Configuration
API_TIMEOUT: Final[int] = 30
MAX_RETRIES: Final[int] = 3

# Light States
LIGHT_STATE: Final[dict] = {
    "OFF": 1,
    "ON": 2
}

# Default Light Parameters
LIGHT_PARAMS: Final[dict] = {
    "BRIGHTNESS": 63,
    "COLOR": 63,
    "PATTERN_SPEED": 63
}

# API Configuration
DEVICE_ID: Final[str] = "HavenLightingMobile"
AUTH_API_BASE: Final[str] = "https://havenwebservices-apiapp-test.azurewebsites.net/api/v2"
PROD_API_BASE: Final[str] = "https://ase-hvnlght-residential-api-prod.azurewebsites.net/api" 