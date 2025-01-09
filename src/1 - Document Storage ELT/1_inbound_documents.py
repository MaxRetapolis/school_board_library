import os
import hashlib  # Import hashlib for hashing document contents
import json
import shutil
import datetime
import logging
import uuid
from helpers import move_file, get_file_extension  # Import helper functions

# Ensure the directory for the log file exists
ROOT_FOLDER = "C:/Users/Maxim/Documents/VSCode/school_board_library/data/documents"  # Root folder location
LOGS_FOLDER = os.path.join(os.path.dirname(ROOT_FOLDER), "logs")
os.makedirs(LOGS_FOLDER, exist_ok=True)
LOG_FILE = os.path.join(LOGS_FOLDER, "document_pipeline.log")

# --- Configuration ---
DEFAULT_FOLDERS = {
    "new": "New_Documents",
    "processing": "In_Processing",
    "duplicates": "Duplicates",
    "classified": "Classified"
}
FOLDER_LIST_FILE = os.path.join(ROOT_FOLDER, "folder_list.json")  # File to store the list of folders
INDEX_FILE = os.path.join(ROOT_FOLDER, "documents_index.json")  # Ensure index file is in the documents folder

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
        self.document_id = None  # Will be assigned later
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
def load_index(index_file):
    """Loads the document index from a JSON file."""
    if not os.path.exists(index_file):
        return {}, 0  # Return empty index and 0 as next_document_id
    try:
        with open(index_file, "r") as f:
            index = json.load(f)
            # Find the maximum document_id
            max_id = 0
            for doc_id in index.keys():
                try:
                    doc_id_int = int(doc_id)
                    if doc_id_int > max_id:
                        max_id = doc_id_int
                except ValueError:
                    logging.warning(f"Non-integer document ID found in index: {doc_id}. It will be ignored for max ID calculation.")

            return index, max_id + 1
    except Exception as e:
        logging.error(f"Error loading index from {index_file}: {e}")
        return {}, 0

def save_index(index_file, index):
    """Saves the document index to a JSON file."""
    try:
        with open(index_file, "w") as f:
            json.dump(index, f, indent=4)
        logging.info("Index saved successfully.")
        print("Index saved successfully.")
    except Exception as e:
        logging.error(f"Error saving index to {index_file}: {e}")
        print(f"Error saving index to {index_file}: {e}")

def handle_new_document(document, main_index, document_id, new_doc_folder, in_proc_folder):
    """Handles the processing of a new document."""
    document.document_id = document_id
    document.status = "In_Processing"
    document.move_to_folder(os.path.join(ROOT_FOLDER, in_proc_folder))
    main_index[str(document.document_id)] = document.to_dict()
    print(f"Handled new document {document.filename}, assigned ID: {document_id}")

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
    main_index, next_document_id = load_index(INDEX_FILE)
    logging.info(f"Loaded index with {len(main_index)} documents, next document ID: {next_document_id}")
    print(f"Loaded index with {len(main_index)} documents, next document ID: {next_document_id}")
    create_folders(folder_list)

    # Step 2: Create Temporary Indexes for Each Folder
    temp_indexes = {}
    for folder_name in folder_list:
        temp_indexes[folder_name] = {}
        folder_path = os.path.join(ROOT_FOLDER, folder_name)  # Get full path
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath):
                doc = Document(filepath)
                temp_doc_id = str(uuid.uuid4()) # Generate a temporary ID
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
          doc.document_id = doc_dict["document_id"]
          doc.status = doc_dict["status"]
          doc.metadata = doc_dict["metadata"]
          
          match_found = False
          for existing_doc_id, existing_doc_dict in main_index.items():
              if (doc.filename == existing_doc_dict["filename"] and
                      doc.size == existing_doc_dict["size"] and
                      doc.hash == existing_doc_dict["hash"]):  # Compare using hash instead of creation date
                  match_found = True
                  print(f"Duplicate found: {doc.filename}")
                  if existing_doc_dict["status"] in ["In_Processing", "Duplicates", "Processed"]:
                      # Duplicate found
                      doc.move_to_folder(os.path.join(ROOT_FOLDER, duplicates_folder))
                      main_index[existing_doc_id]["status"] = "Duplicates"
                      main_index[existing_doc_id]["filepath"] = doc.filepath
                      logging.info(f"Moved duplicate document {doc.filename} from {new_docs_folder} to {duplicates_folder}")
                      print(f"Moved duplicate document {doc.filename} from {new_docs_folder} to {duplicates_folder}")
                  elif existing_doc_dict["status"] == "Errors":
                      # Retry document previously in Error
                      handle_new_document(doc, main_index, next_document_id, new_docs_folder, in_processing_folder)
                      logging.info(f"Retrying processing of document {doc.filename} previously in Errors, moved from {new_docs_folder} to {in_processing_folder}, assigned ID: {next_document_id}")
                      print(f"Retrying processing of document {doc.filename} previously in Errors, moved from {new_docs_folder} to {in_processing_folder}, assigned ID: {next_document_id}")
                      next_document_id += 1
                  break  # Exit the inner loop once a match is found

          if not match_found:
              # New document
              handle_new_document(doc, main_index, next_document_id, new_docs_folder, in_processing_folder)
              logging.info(f"Moved new document {doc.filename} from {new_docs_folder} to {in_processing_folder}, assigned ID: {next_document_id}")
              print(f"Moved new document {doc.filename} from {new_docs_folder} to {in_processing_folder}, assigned ID: {next_document_id}")
              next_document_id += 1
      
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
                logging.info(f"Found document {doc.filename} in {folder_name} that was not in the main index. Adding to index with ID: {next_document_id}")
                print(f"Found document {doc.filename} in {folder_name} that was not in the main index. Adding to index with ID: {next_document_id}")
                doc.document_id = str(next_document_id)
                next_document_id += 1
                
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