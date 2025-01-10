import logging
import os

def setup_logging(log_file_path):
    """Sets up logging configuration."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler()
        ]
    )

def get_logger(name):
    """Retrieves a logger with the specified name."""
    return logging.getLogger(name)