import os
import logging
from file_operations import move_file, delete_file

def move_to_duplicates_folder(doc_id, doc_data, duplicates_folder):
    """
    Moves the duplicate document to the Duplicates folder and overwrites if it exists.
    
    Args:
        doc_id (str): The unique identifier for the document (e.g., its hash).
        doc_data (dict): Dictionary containing document metadata (filepath, status, etc.).
        duplicates_folder (str): Path to the Duplicates folder.
    """
    try:
        if not os.path.exists(duplicates_folder):
            os.makedirs(duplicates_folder, exist_ok=True)
            logging.info(f"Created Duplicates folder: {duplicates_folder}")
        else:
            logging.debug(f"Duplicates folder already exists: {duplicates_folder}")

        filename = os.path.basename(doc_data["filepath"])
        new_filepath = os.path.join(duplicates_folder, filename)

        # Overwrite if exists
        if os.path.exists(new_filepath):
            delete_file(new_filepath)
            logging.info(f"Overwriting existing file in Duplicates folder: {filename}")

        move_file(doc_data["filepath"], new_filepath)
        doc_data["filepath"] = new_filepath
        doc_data["status"] = "Duplicates"
        logging.info(f"Moved document {doc_id} to Duplicates folder as {filename}")

    except Exception as e:
        logging.error(f"Error moving document {doc_id} to Duplicates folder: {e}")

def move_to_in_processing_folder(doc_id, doc_data, in_processing_folder):
    """
    Moves the document back to the In_Processing folder.
    
    Args:
        doc_id (str): The unique identifier for the document.
        doc_data (dict): Dictionary containing document metadata.
        in_processing_folder (str): Path to the In_Processing folder.
    """
    try:
        if not os.path.exists(in_processing_folder):
            os.makedirs(in_processing_folder, exist_ok=True)
            logging.info(f"Created In_Processing folder: {in_processing_folder}")
        else:
            logging.debug(f"In_Processing folder already exists: {in_processing_folder}")

        new_filepath = os.path.join(in_processing_folder, os.path.basename(doc_data["filepath"]))
        move_file(doc_data["filepath"], new_filepath)
        doc_data["filepath"] = new_filepath
        logging.info(f"Moved document {doc_id} back to In_Processing folder.")

    except Exception as e:
        logging.error(f"Error moving document {doc_id} back to In_Processing folder: {e}")
