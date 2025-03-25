#!/usr/bin/env python3

import os
import sys
import logging
import shutil
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the DocumentClassifier
from Claude.document_classifier.main.document_classifier import DocumentClassifier
from Claude.document_classifier.configs.classifier_config import PATHS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ClassifyAll')

def ensure_directories():
    """Ensure all required directories exist."""
    # Make sure output directories exist
    for dir_path in PATHS['CLASSIFIED_DIR'].values():
        os.makedirs(os.path.join(project_root, dir_path), exist_ok=True)
    
    os.makedirs(os.path.join(project_root, PATHS['IN_PROCESSING_DIR']), exist_ok=True)
    os.makedirs(os.path.join(project_root, 'Claude/logs'), exist_ok=True)
    
    # Create outbound directory if it doesn't exist
    os.makedirs(os.path.join(project_root, PATHS['OUTPUT_DIR']), exist_ok=True)

def classify_all_files():
    """
    Classify all files from the data/raw_documents directory and move them to the appropriate output directories.
    """
    # Initialize the classifier
    classifier = DocumentClassifier()
    logger.info("DocumentClassifier initialized")
    
    # Get input files
    raw_dir = os.path.join(project_root, 'data/raw_documents')
    if not os.path.exists(raw_dir):
        logger.error(f"Raw documents directory not found: {raw_dir}")
        return
    
    # List files in the directory
    files = os.listdir(raw_dir)
    logger.info(f"Found {len(files)} files to process")
    
    # Statistics
    results = {
        'Text-based PDF': 0,
        'Text-based non-PDF': 0,
        'Image-based document': 0,
        'PDF-Text-With-Images': 0,
        'Plain-Text-Special-Format': 0,
        'Unknown': 0,
        'Error': 0
    }
    
    # Process each file
    for filename in files:
        file_path = os.path.join(raw_dir, filename)
        logger.info(f"Processing {filename}")
        
        try:
            # First move to in-processing directory
            in_processing_path = os.path.join(
                project_root, PATHS['IN_PROCESSING_DIR'], filename
            )
            shutil.copy2(file_path, in_processing_path)
            logger.debug(f"Copied to in-processing: {in_processing_path}")
            
            # Classify the file
            classification = classifier.classify_document(file_path)
            logger.info(f"Classified {filename} as: {classification}")
            
            # Determine the destination directory
            dest_dir = os.path.join(
                project_root, PATHS['CLASSIFIED_DIR'].get(classification, PATHS['CLASSIFIED_DIR']['Unknown'])
            )
            
            # Move the file to the destination
            dest_path = os.path.join(dest_dir, filename)
            shutil.copy2(file_path, dest_path)
            logger.info(f"Moved to {dest_path}")
            
            # Clean up in-processing
            os.remove(in_processing_path)
            
            # Update statistics
            if classification in results:
                results[classification] += 1
            else:
                results['Unknown'] += 1
                
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            # Update error statistics
            results['Error'] += 1
    
    # Log summary
    logger.info("Classification completed. Summary:")
    for category, count in results.items():
        logger.info(f"{category}: {count} files")

def main():
    """Main entry point for the script."""
    logger.info("Starting classification process for all files")
    
    # Create required directories
    ensure_directories()
    
    # Classify and move files
    classify_all_files()
    
    logger.info("Classification process completed")

if __name__ == "__main__":
    main()