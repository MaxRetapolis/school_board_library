
import hashlib
import os
import logging

def calculate_hash(filepath):
    """
    Calculate the SHA256 hash of a file.
    
    Args:
        filepath (str): Path to the file.
        
    Returns:
        str: SHA256 hash of the file.
    """
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def generate_document_id(filepath):
    """
    Generate a document ID based on the file's hash.
    
    Args:
        filepath (str): Path to the file.
        
    Returns:
        str: Generated document ID.
    """
    return calculate_hash(filepath)

def get_file_extension(filepath):
    """Extracts the file extension from a filepath."""
    return os.path.splitext(filepath)[1].lower().lstrip('.')  # Remove the leading dot

def verify_document_exists(document_id, index):
    """Checks if the document file exists. Removes the index entry if it does not."""
    doc_info = index.get(document_id)
    if doc_info and not os.path.isfile(doc_info["filepath"]):
        logging.warning(f"Document file not found: {doc_info['filepath']}. Removing from index.")
        del index[document_id]
        return False
    return True

class Document:
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.extension = os.path.splitext(self.filename)[1].lower()
        self.size = os.path.getsize(filepath)
        self.hash = calculate_hash(filepath)  # Generate hash of the file contents
        self.document_id = self.hash  # Set hash as document_id
        self.status = None  # Will be set based on the folder
        self.metadata = {}