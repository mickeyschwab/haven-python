class HavenLightingError(Exception):
    """Base exception for Haven Lighting client."""
    pass

class AuthenticationError(HavenLightingError):
    """Raised when authentication fails."""
    pass

class ApiError(HavenLightingError):
    """Raised when API returns an error."""
    pass 