import time
from functools import wraps
from typing import Callable, Any
from .config import MAX_RETRIES
from .exceptions import ApiError

def retry_on_error(max_retries: int = MAX_RETRIES, delay: float = 1.0) -> Callable:
    """Decorator to retry functions on failure."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except ApiError as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))
            raise last_error
        return wrapper
    return decorator 