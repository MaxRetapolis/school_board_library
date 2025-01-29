import logging  # Ensure logging is imported at the top
import json
import os
from utils import calculate_hash, verify_document_exists

# Diagnostic print to verify logging import
print("Logging module imported:", logging)

def load_index(index_file):
    """
    Load the document index from a JSON file.

    Args:
        index_file (str): Path to the index JSON file.

    Returns:
        dict: The loaded document index.
    """
    if not os.path.exists(index_file):
        return {}
    with open(index_file, 'r') as f:
        return json.load(f)

def save_index(index_file, index):
    """
    Save the document index to a JSON file.

    Args:
        index_file (str): Path to the index JSON file.
        index (dict): The document index to save.
    """
    with open(index_file, 'w') as f:
        json.dump(index, f, indent=4)

def index_exists(index_file):
    """
    Check if the index file exists.

    Args:
        index_file (str): Path to the index JSON file.

    Returns:
        bool: True if index exists, False otherwise.
    """
    return os.path.exists(index_file)

def update_document_status(document_id, index):
    """Updates the status of the document based on its current folder."""
    doc_info = index.get(document_id)
    if not doc_info:
        return  # Exit if the document doesn't exist in the index

    current_folder = os.path.basename(os.path.dirname(doc_info["filepath"]))
    valid_statuses = ["New_Documents", "In_Processing", "Duplicates", "Classified"]
    if current_folder not in valid_statuses:
        logging.warning(
            f"Unknown folder '{current_folder}' for document ID {document_id}. Setting status to 'Unknown'."
        )
        index[document_id]["status"] = "Unknown"
    else:
        index[document_id]["status"] = current_folder

def cleanse_index(index, folder_list):
    """Cleanses the index by removing entries for missing documents and updating statuses."""
    print("Entering cleanse_index function")  # Debugging message
    removed_entries = []
    for document_id in list(index.keys()):
        exists = verify_document_exists(document_id, index)
        if not exists:
            removed_entries.append(document_id)  # Corrected closing parenthesis
            try:
                del index[document_id]
                logging.warning(f"Removed missing document from index: Document ID {document_id}")
            except KeyError:
                logging.error(f"Failed to remove Document ID {document_id} as it does not exist in the index.")

    logging.info(f"Index cleansing complete. Removed {len(removed_entries)} missing documents.")
    print(f"Index cleansing complete. Removed {len(removed_entries)} missing documents.")  # Debugging message
    return index
