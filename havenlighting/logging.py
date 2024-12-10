"""Logging configuration for Haven Lighting."""

import logging
from typing import Optional

def setup_logging(level: int = logging.INFO, 
                 log_file: Optional[str] = None) -> None:
    """
    Configure logging for the Haven Lighting client.
    
    Args:
        level: Logging level (default: INFO)
        log_file: Optional file path for logging output
    """
    logger = logging.getLogger("havenlighting")
    logger.setLevel(level)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler) 