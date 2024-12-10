class HavenException(Exception):
    """Base exception for Haven Lighting."""
    pass

class ApiError(HavenException):
    """API failed."""
    pass

class AuthenticationError(HavenException):
    """Authentication failed."""
    pass

class DeviceError(HavenException):
    """Device operation failed."""
    pass