from typing import Dict
import hashlib
from file_handler import FileHandler
from document_classifier import DocumentClassifier
from index_manager import initialize_index, update_index, save_index
from config import INDEX_FILE
from logging_setup import get_logger

logger = get_logger(__name__)

class DocumentPipeline:
    def __init__(self):
        self.file_handler = FileHandler()
        self.classifier = DocumentClassifier()
        self.document_index = initialize_index(INDEX_FILE)
    
    def process_new_document(self, file_path: str) -> None:
        """
        Main pipeline for processing a new document:
        1. Move to processing folder
        2. Generate hash and check for duplicates
        3. Extract text and metadata
        4. Classify document
        5. Move to final destination
        6. Update index
        """
        try:
            # Move to processing
            processing_path = self.file_handler.move_file(file_path, "processing")
            
            # Generate hash and check duplicates
            file_hash = self._generate_file_hash(processing_path)
            if self._is_duplicate(file_hash):
                self.file_handler.move_file(processing_path, "duplicates")
                return
            
            # TODO: Implement document text extraction
            # document_text = self._extract_text(processing_path)
            # metadata = self._extract_metadata(processing_path)
            
            # TODO: Implement classification
            # categories = self.classifier.classify_document(document_text, metadata)
            
            # TODO: Move to classified folder with appropriate naming
            # final_path = self.file_handler.move_file(
            #     processing_path, 
            #     "classified",
            #     self._generate_classified_name(categories)
            # )
            
            # TODO: Update index with document info
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            raise
    
    def _generate_file_hash(self, file_path: str) -> str:
        """Generates SHA-256 hash of file contents."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _is_duplicate(self, file_hash: str) -> bool:
        """Checks if document hash exists in index."""
        return file_hash in self.document_index 