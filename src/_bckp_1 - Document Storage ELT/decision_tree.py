import os
import json
import logging

def load_decision_tree(filepath: str) -> dict:
    """
    Loads the decision tree JSON from the given filepath.
    Returns a dictionary of classification rules or None if there's an error.
    """
    if not os.path.exists(filepath):
        logging.error(f"Decision tree file not found: {filepath}")
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            decision_tree = json.load(f)
            logging.info(f"Decision tree loaded from: {filepath}")
        return decision_tree
    except Exception as e:
        logging.error(f"Error reading decision tree file: {e}")
        return None
