import os
import sys
import logging
import json

# Example imports for other modules (to be created or already existing)
from index_manager import load_index, save_index, index_exists, initialize_index
from document_manager import move_to_duplicates_folder, move_to_in_processing_folder
from classifiers import pdf_classifier, doc_classifier, docx_classifier, image_classifier  # etc.
from decision_tree import load_decision_tree
from logging_setup import setup_logging, get_logger

# ----------------------------------------------------------------
# Configure paths (adjust as needed for your environment)
# ----------------------------------------------------------------
DATA_FOLDER = r"C:\Users\Maxim\Documents\VSCode\school_board_library\data"
LOGS_FOLDER = os.path.join(DATA_FOLDER, "logs")
DOCUMENTS_FOLDER = os.path.join(DATA_FOLDER, "documents")

INDEX_FILE = os.path.join(DOCUMENTS_FOLDER, "index.json")
CLASSIFIED_FOLDER = os.path.join(DOCUMENTS_FOLDER, "Classified")
IN_PROCESSING_FOLDER = os.path.join(DOCUMENTS_FOLDER, "In_Processing")
DUPLICATES_FOLDER = os.path.join(DOCUMENTS_FOLDER, "Duplicates")
DECISION_TREE_FILE = os.path.join(DOCUMENTS_FOLDER, "classification_decision_tree.json")

LOG_FILE = os.path.join(LOGS_FOLDER, "document_classifier.log")

# ----------------------------------------------------------------
# Setup logging
# ----------------------------------------------------------------
os.makedirs(LOGS_FOLDER, exist_ok=True)
setup_logging(LOG_FILE)
logger = get_logger(__name__)

# ----------------------------------------------------------------
# Extension to classifier-function mapping
# (Placeholder - actual functions will be defined in the classifiers/ folder)
# ----------------------------------------------------------------
EXTENSION_CLASSIFIERS = {
    "pdf": pdf_classifier.classify_pdf, 
    "doc": doc_classifier.classify_doc,
    "docx": docx_classifier.classify_docx,
    "jpg": image_classifier.classify_image,
    "png": image_classifier.classify_image,
    # Add more as needed...
}

def get_file_extension(filepath: str) -> str:
    """Return the file extension (in lowercase, without the leading dot)."""
    return os.path.splitext(filepath)[1].lower().lstrip('.')

def classify_document(doc_id: str, doc_data: dict, decision_tree_rules: dict, index: dict) -> None:
    """
    Orchestrates classification for a single document:
      - Detect extension
      - Call the corresponding classifier
      - Update the index & handle file movement
    """
    filepath = doc_data["filepath"]
    extension = get_file_extension(filepath)

    # Decide which classifier to use based on the extension
    classifier_func = EXTENSION_CLASSIFIERS.get(extension)

    if not classifier_func:
        logger.warning(f"No classifier found for extension: {extension}. Marking as Unknown.")
        doc_data["document_type"] = "Unknown"
        index[doc_id]["status"] = "Errors"
        return

    try:
        # Perform classification (returns a dict with classification results)
        classification_results = classifier_func(filepath)

        # Update document's metadata
        doc_data["metadata"].update(classification_results)

        # Decide final document type based on decision tree or custom logic
        primary_type = decision_tree_rules.get(extension, {}).get("primary", "Unknown")
        doc_data["document_type"] = primary_type

        # For demonstration, we simply mark it as "Classified" on success
        doc_data["status"] = "Classified"
        logger.info(f"Document {doc_id} classified as {primary_type} with metadata {classification_results}")

        # If needed, move duplicates or otherwise handle final location
        # This is just a placeholder call:
        # move_to_duplicates_folder(doc_id, doc_data)
        # or:
        # move_to_in_processing_folder(doc_id, doc_data)

    except Exception as e:
        logger.error(f"Error classifying document {doc_id}: {e}")
        doc_data["status"] = "Errors"

def classify_documents_sequentially(index: dict, decision_tree_rules: dict) -> None:
    """
    Loops through all files in the IN_PROCESSING_FOLDER,
    classifies them, and updates the index.
    """
    if not os.path.exists(IN_PROCESSING_FOLDER):
        logger.warning(f"In_Processing folder not found: {IN_PROCESSING_FOLDER}")
        return

    for filename in os.listdir(IN_PROCESSING_FOLDER):
        filepath = os.path.join(IN_PROCESSING_FOLDER, filename)
        if not os.path.isfile(filepath):
            continue

        doc_id = filename  # In your real logic, you may use a hash or something else as an ID
        
        # If doc not in index, initialize it
        if doc_id not in index:
            index[doc_id] = {
                "document_id": doc_id,
                "filepath": filepath,
                "filename": filename,
                "extension": get_file_extension(filepath),
                "document_type": "Unknown",
                "status": "In_Processing",
                "metadata": {},
            }
        else:
            # Update path and status if already in index
            index[doc_id]["filepath"] = filepath
            index[doc_id]["status"] = "In_Processing"

        # Call the classification routine
        classify_document(doc_id, index[doc_id], decision_tree_rules, index)

        # Save index after each classification or handle it in bulk later
        save_index(INDEX_FILE, index)

def main():
    logger.info("Starting document classification process.")

    # 1) Initialize or load the index
    if not index_exists(INDEX_FILE):
        index = initialize_index(INDEX_FILE)
    else:
        index = load_index(INDEX_FILE)

    # 2) Load the decision tree from JSON
    decision_tree_rules = load_decision_tree(DECISION_TREE_FILE)
    if not decision_tree_rules:
        logger.error("Decision tree loading failed. Exiting.")
        sys.exit(1)

    # 3) Ensure required folders exist
    os.makedirs(CLASSIFIED_FOLDER, exist_ok=True)
    os.makedirs(IN_PROCESSING_FOLDER, exist_ok=True)
    os.makedirs(DUPLICATES_FOLDER, exist_ok=True)

    # 4) Classify documents
    classify_documents_sequentially(index, decision_tree_rules)

    logger.info("Document classification process completed.")

if __name__ == "__main__":
    main()
