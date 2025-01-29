import os
import json
import logging

def index_exists(index_file: str) -> bool:
    """
    Checks if the index file exists.
    
    Args:
        index_file (str): Path to the index JSON file.
        
    Returns:
        bool: True if the file exists, otherwise False.
    """
    return os.path.exists(index_file)

def load_index(index_file: str) -> dict:
    """
    Loads the index from a JSON file.
    
    Args:
        index_file (str): Path to the index JSON file.
        
    Returns:
        dict: The loaded index dictionary.
    """
    if not os.path.exists(index_file):
        logging.warning(f"Index file does not exist: {index_file}")
        return {}

    try:
        with open(index_file, "r", encoding="utf-8") as f:
            index_data = json.load(f)
            logging.info(f"Index loaded from: {index_file}")
        return index_data
    except Exception as e:
        logging.error(f"Error loading index from {index_file}: {e}")
        return {}

def save_index(index_file: str, index_data: dict) -> None:
    """
    Saves the index to a JSON file.
    
    Args:
        index_file (str): Path to the index JSON file.
        index_data (dict): The index dictionary to save.
    """
    try:
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=4)
            logging.debug(f"Index saved to: {index_file}")
    except Exception as e:
        logging.error(f"Error saving index to {index_file}: {e}")

def initialize_index(index_file: str) -> dict:
    """
    Creates a new index file if it doesn't exist and returns an empty dictionary.
    
    Args:
        index_file (str): Path to the index JSON file.
        
    Returns:
        dict: The newly created (empty) index dictionary.
    """
    if not index_exists(index_file):
        try:
            with open(index_file, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)
            logging.info(f"Created new empty index file at: {index_file}")
            return {}
        except Exception as e:
            logging.error(f"Error creating index file {index_file}: {e}")
            return {}
    else:
        # If it already exists, load it instead
        return load_index(index_file)

def cleanse_index(index_data: dict) -> dict:
    """
    (Optional utility) Cleans or prunes unwanted entries from the index. 
    Implementation depends on your requirements.
    
    Args:
        index_data (dict): Current index data.
        
    Returns:
        dict: The cleansed index data.
    """
    # Example: Remove entries with status == "Errors" older than 30 days, etc.
    # Implement as needed.
    logging.debug("Running optional cleanse routine on the index.")
    return index_data
