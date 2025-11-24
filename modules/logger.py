# modules/logger.py
import logging
import os
from logging.handlers import RotatingFileHandler
import config

def setup_logger():
    """Configure and return the system logger."""
    logger = logging.getLogger("ShopManager")
    logger.setLevel(logging.DEBUG)

    # Prevent adding handlers multiple times
    if logger.hasHandlers():
        return logger

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # File Handler (Rotating)
    # Max 5MB per file, keep last 3 files
    file_handler = RotatingFileHandler(
        config.LOG_FILE, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    # Add Handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Logger initialized.")
    return logger

# Create a singleton logger instance
log = setup_logger()
