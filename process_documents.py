import os
import sys
import json
import shutil
from typing import List, Dict

# Add the src directory to the path
src_path = os.path.join(os.path.dirname(__file__), 'src/2 - Document Classifier')
sys.path.append(src_path)

# Import necessary modules
import logging_setup
logger = logging_setup.get_logger("process_documents")

def find_document_type(file_path: str) -> str:
    """Determine document type based on file extension"""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    if ext == '.pdf':
        return "PDF"
    elif ext in ['.vtt', '.srt']:
        return "Text-Only"
    elif ext in ['.txt', '.md', '.csv']:
        return "Text-Only"
    else:
        return "Unknown"

def classify_documents():
    """Classify documents from raw_documents to appropriate folders"""
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_docs_dir = os.path.join(base_dir, 'data/raw_documents')
    classified_dir = os.path.join(base_dir, 'data/documents/Classified')
    
    # Ensure classified folders exist
    categories = ["PDF-Text", "PDF-Images", "PDF-Text-Images", "PDF-Unknown", "Text-Only"]
    for category in categories:
        category_dir = os.path.join(classified_dir, category)
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)
            logger.info(f"Created category directory: {category_dir}")
    
    # Process each file in raw_documents
    processed_count = 0
    file_list = os.listdir(raw_docs_dir)
    total_files = len(file_list)
    
    print(f"Found {total_files} files to process")
    
    for filename in file_list:
        source_path = os.path.join(raw_docs_dir, filename)
        
        # Skip directories
        if os.path.isdir(source_path):
            continue
        
        # Determine document type and target category
        doc_type = find_document_type(source_path)
        target_category = ""
        
        if doc_type == "PDF":
            # For demo purposes, use a simple size-based rule for PDFs
            file_size = os.path.getsize(source_path)
            if file_size < 100000:  # Small PDFs likely text-only
                target_category = "PDF-Text"
            elif file_size < 1000000:  # Medium PDFs likely have text and images
                target_category = "PDF-Text-Images"
            else:  # Large PDFs might be image-heavy
                target_category = "PDF-Images"
        elif doc_type == "Text-Only":
            target_category = "Text-Only"
        else:
            target_category = "PDF-Unknown"
        
        # Copy file to classified folder
        target_dir = os.path.join(classified_dir, target_category)
        target_path = os.path.join(target_dir, filename)
        
        try:
            # Check if file already exists at destination
            if os.path.exists(target_path):
                logger.info(f"File already exists at destination: {target_path}")
            else:
                shutil.copy2(source_path, target_path)
                logger.info(f"Copied {filename} to {target_category}")
                processed_count += 1
        except Exception as e:
            logger.error(f"Error copying {filename}: {e}")
    
    print(f"Successfully processed {processed_count} out of {total_files} files")
    return processed_count

def main():
    print("Document Processing System")
    print("=========================")
    
    # Classify documents
    processed_count = classify_documents()
    
    print("\nProcess completed!")
    print(f"Total documents classified: {processed_count}")

if __name__ == "__main__":
    main()