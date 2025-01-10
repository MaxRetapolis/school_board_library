import os
import logging

# --- Configuration ---
ROOT_FOLDER = "C:/Users/Maxim/Documents/VSCode/school_board_library/data/documents"
INDEX_FILE = os.path.join(ROOT_FOLDER, "documents_index.json")
LOGS_FOLDER = os.path.join(os.path.dirname(ROOT_FOLDER), "logs")
LOG_FILE = os.path.join(LOGS_FOLDER, "document_pipeline.log")
CLASSIFIED_FOLDER = os.path.join(ROOT_FOLDER, "Classified")
COMBINATIONS_FILE = os.path.join(ROOT_FOLDER, "classification_combinations.json")
FOLDER_LIST_FILE = os.path.join(ROOT_FOLDER, "folder_list.json")

DEFAULT_FOLDERS = {
    "new": "New_Documents",
    "processing": "In_Processing",
    "duplicates": "Duplicates",
    "classified": "Classified"
}

# --- Logging Setup ---
LOGGING_LEVEL = logging.INFO
LOGGING_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'