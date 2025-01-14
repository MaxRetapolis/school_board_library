import sys
import os
import hashlib  # Import hashlib for hashing document contents
import json
import shutil
import datetime
import logging
import uuid

# Import configuration
from config import ROOT_FOLDER, INDEX_FILE, LOGS_FOLDER, LOG_FILE, FOLDER_LIST_FILE, DEFAULT_FOLDERS

# Add the parent directory to sys.path to locate helpers.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from file_operations import move_file, delete_file
from utils import generate_document_id
from logging_setup import setup_logging, get_logger
from index_management import load_index, save_index, index_exists, cleanse_index  # Ensure cleanse_index is imported

# Initialize logging using config
setup_logging(LOG_FILE)
logger = get_logger(__name__)

# Ensure the directory for the log file exists
os.makedirs(LOGS_FOLDER, exist_ok=True)

# --- Logging Setup ---
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# --- Folder List Management ---
def load_folder_list(folder_list_file=FOLDER_LIST_FILE):
    """Loads the list of folders from a JSON file. If empty or not found, returns default list."""
    try:
        if os.path.getsize(folder_list_file) > 0:
            with open(folder_list_file, "r") as f:
                folder_list = json.load(f)
            return folder_list
        else:
            logging.warning(f"Folder list file is empty: {folder_list_file}. Using default folders.")
            return list(DEFAULT_FOLDERS.values())
    except FileNotFoundError:
        logging.error(f"Folder list file not found: {folder_list_file}. Using default folders.")
        return list(DEFAULT_FOLDERS.values())
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from {folder_list_file}. Check for valid JSON format. Using default folders.")
        return list(DEFAULT_FOLDERS.values())
    except Exception as e:
        logging.error(f"An unexpected error occurred while loading folder list from {folder_list_file}: {e}. Using default folders.")
        return list(DEFAULT_FOLDERS.values())

def create_folders(folder_list):
    """Creates the necessary folders if they don't exist.""" 
    for folder in folder_list:
        folder_path = os.path.join(ROOT_FOLDER, folder)
        os.makedirs(folder_path, exist_ok=True)
        print(f"Ensured folder exists: {folder_path}")

def hash_file(filepath):
    """Generates a SHA-256 hash of the file contents."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# --- Document Class ---
class Document:
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.extension = os.path.splitext(self.filename)[1].lower()
        self.size = os.path.getsize(filepath)
        self.hash = hash_file(filepath)  # Generate hash of the file contents
        self.status = None  # Will be set based on the folder
        self.document_id = self.hash  # Make sure we use the file's hash as the document ID
        self.metadata = {}

    def to_dict(self):
        """Converts the Document object to a dictionary."""
        return {
            "document_id": self.document_id,
            "filepath": self.filepath,
            "filename": self.filename,
            "extension": self.extension,
            "size": self.size,
            "hash": self.hash,
            "status": self.status,
            "metadata": self.metadata,
        }

    def move_to_folder(self, destination_folder):
        """Moves the document to the specified folder and updates status and filepath"""
        new_filepath = os.path.join(destination_folder, self.filename)
        try:
            shutil.move(self.filepath, new_filepath)
            self.filepath = new_filepath
            self.status = os.path.basename(destination_folder) # Update status to folder name
            logging.info(f"Moved document {self.filename} to {destination_folder}")
            print(f"Moved document {self.filename} to {destination_folder}")
        except Exception as e:
            logging.error(f"Error moving document {self.filename} to {destination_folder}: {e}")
            self.status = "Errors"
            print(f"Error moving document {self.filename} to {destination_folder}: {e}")

# --- Helper Functions ---
def initialize_index(index_file):
    if not index_exists(index_file):
        index = {}
        save_index(index_file, index)
    else:
        index = load_index(index_file)
    return index

def handle_new_document(document, main_index, new_doc_folder, in_processing_folder):
    """Handles the processing of a new document."""
    document.status = "In_Processing"
    document.move_to_folder(os.path.join(ROOT_FOLDER, in_processing_folder))
    main_index[document.document_id] = document.to_dict()  # Use hash as key
    logging.debug(f"Assigned document ID {document.document_id} to {document.filename}")
    print(f"Handled new document {document.filename}, assigned ID: {document.document_id}")

def move_to_classified_folder(doc_id, doc_data, classified_folder):
    """Moves the document to the classified folder based on its document type."""
    document_type = doc_data["document_type"]
    destination_folder = os.path.join(classified_folder, document_type)
    os.makedirs(destination_folder, exist_ok=True)
    new_filepath = os.path.join(destination_folder, os.path.basename(doc_data["filepath"]))
    move_file(doc_data["filepath"], new_filepath)
    doc_data["filepath"] = new_filepath
    doc_data["status"] = "Classified"
    logging.info(f"Moved document {doc_id} to {destination_folder}")

def synchronize_index_with_folders(main_index, folder_list):
    """Synchronizes the index with the actual files in the folders by removing records for missing files."""
    removed_entries = []
    for doc_id, doc_info in list(main_index.items()):
        filepath = doc_info.get("filepath")
        if not filepath or not os.path.isfile(filepath):
            removed_entries.append(doc_id)
            del main_index[doc_id]
            logging.warning(f"Removed index entry for missing file: Document ID {doc_id}, Path: {filepath}")
            print(f"Removed index entry for missing file: Document ID {doc_id}, Path: {filepath}")
    if removed_entries:
        logging.info(f"Total removed index entries: {len(removed_entries)}")
        print(f"Total removed index entries: {len(removed_entries)}")
    else:
        logging.info("No missing files found. Index is synchronized with folders.")

def rationalize_index(main_index):
    """Removes duplicate records from the index and retains the original document IDs."""
    logging.info("Starting index rationalization.")
    print("Starting index rationalization.")
    
    hash_to_doc_id = {}
    duplicates = []

    for doc_id, doc_info in main_index.items():
        doc_hash = doc_info.get("hash")
        if not doc_hash:
            logging.warning(f"Document ID {doc_id} has no hash. Skipping.")
            continue
        if doc_hash in hash_to_doc_id:
            original_doc_id = hash_to_doc_id[doc_hash]
            duplicates.append((doc_id, original_doc_id))  # Corrected variable name
        else:
            hash_to_doc_id[doc_hash] = doc_id

    for duplicate_id, original_id in duplicates:
        logging.info(f"Removing duplicate Document ID {duplicate_id}, original Document ID {original_id}.")
        print(f"Removing duplicate Document ID {duplicate_id}, original Document ID {original_id}.")
        # Optionally, move the duplicate file to a separate folder or delete it
        duplicate_filepath = main_index[duplicate_id]["filepath"]
        try:
            shutil.move(duplicate_filepath, os.path.join(ROOT_FOLDER, DEFAULT_FOLDERS["duplicates"], os.path.basename(duplicate_filepath)))
            logging.info(f"Moved duplicate file {duplicate_filepath} to Duplicates folder.")
            print(f"Moved duplicate file {duplicate_filepath} to Duplicates folder.")
        except Exception as e:
            logging.error(f"Error moving duplicate file {duplicate_filepath}: {e}")
            print(f"Error moving duplicate file {duplicate_filepath}: {e}")
        # Remove the duplicate entry from the index
        del main_index[duplicate_id]

    logging.info(f"Index rationalization complete. Removed {len(duplicates)} duplicates.")
    print(f"Index rationalization complete. Removed {len(duplicates)} duplicates.")

# --- Main Processing Logic ---
def process_documents():
    """Main function to process documents in the specified folders."""
    logging.info("Script started.")
    print("Script started.")

    # Load the folder list
    folder_list = load_folder_list(FOLDER_LIST_FILE)
    if not folder_list:
        logging.error("No folders specified in the folder list and no default folders available. Exiting.")
        print("No folders specified in the folder list and no default folders available. Exiting.")
        return  # Exit if folder list is empty and no defaults

    # Step 1: Initialization and Load Main Index
    main_index = initialize_index(INDEX_FILE)
    logging.info(f"Loaded index with {len(main_index)} documents.")
    print(f"Loaded index with {len(main_index)} documents.")
    create_folders(folder_list)

    # Cleanse the index before processing
    main_index = cleanse_index(main_index, folder_list)  # Cleanse the index
    save_index(INDEX_FILE, main_index)  # Save the cleansed index

    # Rationalize the index to remove duplicates
    rationalize_index(main_index)
    save_index(INDEX_FILE, main_index)

    # Step 2: Create Temporary Indexes for Each Folder
    temp_indexes = {}
    for folder_name in folder_list:
        temp_indexes[folder_name] = {}
        folder_path = os.path.join(ROOT_FOLDER, folder_name)  # Get full path
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath):
                doc = Document(filepath)
                existing_doc_id = None
                # Check if the document already exists in the main index
                for doc_id, doc_info in main_index.items():
                    if doc.hash == doc_info["hash"]:
                        existing_doc_id = doc_id
                        break
                if existing_doc_id:
                    # Existing document, retain its ID
                    doc.document_id = existing_doc_id
                    temp_doc_id = existing_doc_id
                else:
                    # New document, assign a new ID
                    temp_doc_id = doc.document_id
                doc.status = folder_name
                temp_indexes[folder_name][temp_doc_id] = doc.to_dict()
        logging.info(f"Found {len(temp_indexes[folder_name])} documents in {folder_name}")
        print(f"Found {len(temp_indexes[folder_name])} documents in {folder_name}")

    # Step 3: Compare Indexes, Identify Edge Cases, and Determine Actions

    # 3.1 Compare New_Documents with Main Index
    new_docs_folder = DEFAULT_FOLDERS["new"]
    in_processing_folder = DEFAULT_FOLDERS["processing"]
    duplicates_folder = DEFAULT_FOLDERS["duplicates"]
    classified_folder = DEFAULT_FOLDERS["classified"]
    
    if new_docs_folder in temp_indexes:
        for temp_doc_id, doc_dict in temp_indexes[new_docs_folder].items():
            doc = Document(doc_dict["filepath"])
            
            match_found = False
            for existing_doc_id, existing_doc_dict in main_index.items():
                if doc.hash == existing_doc_dict["hash"]:
                    match_found = True
                    print(f"Duplicate found: {repr(doc.filename)}")
                    if existing_doc_dict["status"] in ["In_Processing", "Duplicates", "Processed"]:
                        # Duplicate found
                        doc.move_to_folder(os.path.join(ROOT_FOLDER, duplicates_folder))
                        main_index[existing_doc_id]["status"] = "Duplicates"
                        main_index[existing_doc_id]["filepath"] = doc.filepath
                        logging.info(f"Moved duplicate document {doc.filename} from {new_docs_folder} to {duplicates_folder}")
                        print(f"Moved duplicate document {repr(doc.filename)} from {repr(new_docs_folder)} to {repr(duplicates_folder)}")
                    elif existing_doc_dict["status"] == "Errors":
                        # Retry document previously in Error
                        handle_new_document(doc, main_index, new_docs_folder, in_processing_folder)
                        logging.info(f"Retrying processing of document {doc.filename} previously in Errors, moved from {new_docs_folder} to {in_processing_folder}, assigned ID: {doc.document_id}")
                        print(f"Retrying processing of document {repr(doc.filename)} previously in Errors, moved from {repr(new_docs_folder)} to {repr(in_processing_folder)}, assigned ID: {repr(doc.document_id)}")
                    break  # Exit the inner loop once a match is found

            if not match_found:
                # New document
                handle_new_document(doc, main_index, new_docs_folder, in_processing_folder)
                logging.info(f"Moved new document {doc.filename} from {new_docs_folder} to {in_processing_folder}, assigned ID: {doc.document_id}")
                print(f"Moved new document {repr(doc.filename)} from {repr(new_docs_folder)} to {repr(in_processing_folder)}, assigned ID: {repr(doc.document_id)}")

        # Step 3.1.5 Save index
        save_index(INDEX_FILE, main_index)

    # 3.2 Analyze Other Temporary Indexes
    for folder_name in folder_list:
        if folder_name != "New_Documents":
            for temp_doc_id, doc_dict in temp_indexes[folder_name].items():
                doc = Document(doc_dict["filepath"])
                doc.document_id = doc_dict["document_id"]
                doc.status = doc_dict["status"]
                doc.metadata = doc_dict["metadata"]

                match_found = False
                for existing_doc_id, existing_doc_dict in main_index.items():
                    if (doc.filename == existing_doc_dict["filename"] and
                            doc.size == existing_doc_dict["size"] and
                            doc.hash == existing_doc_dict["hash"]):  # Compare using hash instead of creation date
                        match_found = True
                        break
                
                if not match_found:
                    # Anomaly: Document not found in the main index
                    logging.info(f"Found document {doc.filename} in {folder_name} that was not in the main index. Adding to index with ID: {doc.document_id}")
                    print(f"Found document {repr(doc.filename)} in {repr(folder_name)} that was not in the main index. Adding to index with ID: {repr(doc.document_id)}")
                    
                    if folder_name != "In_Processing":
                        doc.status = folder_name
                    else:
                        doc.status = "In_Processing"

                    main_index[doc.document_id] = doc.to_dict()

            # Step 3.2.5 Save index after each folder is processed
            save_index(INDEX_FILE, main_index)

    logging.info("Script finished.")
    print("Script finished.")

if __name__ == "__main__":
    process_documents()
