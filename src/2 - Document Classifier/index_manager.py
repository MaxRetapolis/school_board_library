import os
import json
from logging_setup import get_logger

logger = get_logger(__name__)

def index_exists(index_file: str) -> bool:
    return os.path.exists(index_file)

def initialize_index(index_file: str) -> dict:
    if not index_exists(index_file):
        new_index = {}
        try:
            save_index(index_file, new_index)
            logger.info(f"Created new index file at {index_file}")
            return new_index
        except Exception as e:
            logger.error(f"Failed to create new index file: {e}")
            raise
    else:
        logger.info(f"Index file already exists at {index_file}. Loading existing data.")
        return load_index(index_file)

def load_index(index_file: str) -> dict:
    try:
        with open(index_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        logger.error(f"Index file not found: {index_file}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {index_file}: {e}")
        raise

def update_index(index_data: dict, file_hash: str, doc_info: dict) -> None:
    index_data[file_hash] = doc_info
    logger.debug(f"Updated index entry for hash: {file_hash}")

def save_index(index_file: str, index_data: dict) -> None:
    try:
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2)
        logger.info(f"Index data saved to {index_file}")
    except Exception as e:
        logger.error(f"Failed to save index data to {index_file}: {e}")
        raise
