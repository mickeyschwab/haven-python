from dataclasses import dataclass
from typing import Optional

@dataclass
class AuthResponse:
    success: bool
    token: Optional[str] = None
    refresh_token: Optional[str] = None
    user_id: Optional[str] = None
    message: Optional[str] = None 