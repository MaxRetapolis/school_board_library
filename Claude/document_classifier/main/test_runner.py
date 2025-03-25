#!/usr/bin/env python3

import os
import sys
import logging
import importlib.util
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TestRunner')

def main():
    """Test runner for documenting execution with exception handling."""
    logger.info("Beginning test run to document exceptions")
    
    # Check Python version
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Python path: {sys.path}")
    
    # Check if we can install packages
    logger.info("Checking package installation options:")
    
    # Check if pip is available
    try:
        import pip
        logger.info("pip is available - you can install packages with pip")
    except ImportError:
        logger.warning("pip is not available - packages need to be installed with apt-get")
        logger.info("Try: sudo apt-get install python3-magic python3-pypdf2")
    
    # Check for alternative package installations
    for module_name in ['magic', 'PyPDF2']:
        try:
            module_spec = importlib.util.find_spec(module_name)
            if module_spec:
                logger.info(f"Module {module_name} is already installed at {module_spec.origin}")
            else:
                alternative_names = {
                    'magic': ['python3-magic', 'libmagic'],
                    'PyPDF2': ['python3-pypdf2', 'pypdf2', 'pypdf']
                }
                
                for alt_name in alternative_names.get(module_name, []):
                    alt_spec = importlib.util.find_spec(alt_name)
                    if alt_spec:
                        logger.info(f"Found alternative module: {alt_name} at {alt_spec.origin}")
                        if module_name == 'magic' and alt_name == 'libmagic':
                            logger.info("libmagic can be used with: import magic.Magic as Magic")
                        break
                else:
                    logger.error(f"No alternative found for {module_name}")
        except ImportError:
            logger.error(f"Error checking for module {module_name}")
    
    # Attempt to import the required modules
    try:
        import magic
        logger.info(f"Successfully imported python-magic module: {magic.__file__}")
    except ImportError:
        logger.error("Failed to import python-magic module. Please install it with: pip install python-magic")
        logger.error("On Windows, you may also need: pip install python-magic-bin")
        logger.error("On Linux, try: sudo apt-get install python3-magic")
    
    try:
        import PyPDF2
        logger.info(f"Successfully imported PyPDF2 module: {PyPDF2.__file__}")
    except ImportError:
        logger.error("Failed to import PyPDF2 module. Please install it with: pip install PyPDF2")
        logger.error("On Linux, try: sudo apt-get install python3-pypdf2")
    
    # Check if inbound and outbound directories exist
    inbound_dir = os.path.join(project_root, 'Claude', 'inbound')
    if os.path.exists(inbound_dir):
        logger.info(f"Inbound directory exists: {inbound_dir}")
        files = os.listdir(inbound_dir)
        logger.info(f"Found {len(files)} files in inbound directory")
        if files:
            logger.info(f"First few files: {files[:5]}")
    else:
        logger.error(f"Inbound directory not found: {inbound_dir}")
    
    outbound_dir = os.path.join(project_root, 'Claude', 'outbound')
    if os.path.exists(outbound_dir):
        logger.info(f"Outbound directory exists: {outbound_dir}")
    else:
        logger.error(f"Outbound directory not found: {outbound_dir}")
    
    # Try to import document classifier
    try:
        from Claude.document_classifier.main.document_classifier import DocumentClassifier
        logger.info("Successfully imported DocumentClassifier")
        
        # Try to initialize DocumentClassifier
        try:
            classifier = DocumentClassifier()
            logger.info("Successfully initialized DocumentClassifier")
            
            # Try to classify a document
            if len(files) > 0:
                sample_file = os.path.join(inbound_dir, files[0])
                try:
                    classification = classifier.classify_document(sample_file)
                    logger.info(f"Successfully classified document: {files[0]} as {classification}")
                except Exception as e:
                    logger.error(f"Error classifying document: {str(e)}")
                    if isinstance(e, (ImportError, ModuleNotFoundError)):
                        logger.error("This is likely due to missing dependencies. Check that python-magic and PyPDF2 are installed.")
                    elif isinstance(e, FileNotFoundError):
                        logger.error("File not found error. Make sure the file path is correct.")
                    else:
                        logger.error(f"Unexpected error type: {type(e).__name__}")
        except Exception as e:
            logger.error(f"Error initializing DocumentClassifier: {str(e)}")
    except Exception as e:
        logger.error(f"Error importing DocumentClassifier: {str(e)}")
    
    logger.info("Test run completed")

if __name__ == "__main__":
    main()