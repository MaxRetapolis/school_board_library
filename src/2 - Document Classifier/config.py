import os
import logging

# Use real project paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT_FOLDER = os.path.join(BASE_DIR, "data")
INDEX_FILE = os.path.join(ROOT_FOLDER, "documents/documents_index.json")
LOGS_FOLDER = os.path.join(ROOT_FOLDER, "logs")
if not os.path.exists(LOGS_FOLDER):
    os.makedirs(LOGS_FOLDER)
LOG_FILE = os.path.join(LOGS_FOLDER, "document_pipeline.log")
CLASSIFIED_FOLDER = os.path.join(ROOT_FOLDER, "documents/Classified")
COMBINATIONS_FILE = os.path.join(ROOT_FOLDER, "documents/classification_combinations.json")
FOLDER_LIST_FILE = os.path.join(ROOT_FOLDER, "documents/folder_list.json")

DEFAULT_FOLDERS = {
    "new": "documents/In_Processing",
    "processing": "documents/In_Processing",
    "duplicates": "documents/Duplicates",
    "classified": "documents/Classified"
}

LOGGING_LEVEL = logging.INFO
LOGGING_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
