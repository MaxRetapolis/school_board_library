import logging
import os
from config import LOG_FILE, LOGGING_LEVEL, LOGGING_FORMAT

def setup_logging() -> None:
    """
    Configures the logging system based on LOG_FILE, LOGGING_LEVEL, and LOGGING_FORMAT.
    Ensures logs are written to a file in LOG_FILE.
    """
    logs_dir = os.path.dirname(LOG_FILE)
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    logging.basicConfig(
        filename=LOG_FILE,
        level=LOGGING_LEVEL,
        format=LOGGING_FORMAT,
        filemode='a'
    )

def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger instance with the above settings.
    """
    return logging.getLogger(name)
