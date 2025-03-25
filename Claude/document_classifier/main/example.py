#!/usr/bin/env python3

import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the DocumentClassifier
from src.document_classifier.main.document_classifier import DocumentClassifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Example')


def main():
    """Example usage of the DocumentClassifier."""
    # Initialize the document classifier
    classifier = DocumentClassifier()
    logger.info("DocumentClassifier initialized")
    
    # Get sample files from raw_documents directory
    sample_dir = os.path.join(project_root, 'data', 'raw_documents')
    if not os.path.exists(sample_dir):
        logger.error(f"Sample directory not found: {sample_dir}")
        return
    
    # List files in the directory
    files = os.listdir(sample_dir)
    logger.info(f"Found {len(files)} files in {sample_dir}")
    
    # Classify each file
    for filename in files[:5]:  # Limit to first 5 files
        file_path = os.path.join(sample_dir, filename)
        try:
            classification = classifier.classify_document(file_path)
            logger.info(f"Classified {filename} as: {classification}")
        except Exception as e:
            logger.error(f"Error classifying {filename}: {str(e)}")


if __name__ == "__main__":
    main()
