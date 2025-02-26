import os
import shutil
from pipeline_coordinator import DocumentPipeline
from config import ROOT_FOLDER, DEFAULT_FOLDERS

def setup_test_environment():
    """Creates test folders and sample documents"""
    # Create test document
    new_docs_folder = os.path.join(ROOT_FOLDER, DEFAULT_FOLDERS["new"])
    if not os.path.exists(new_docs_folder):
        os.makedirs(new_docs_folder)
    
    # Create a sample test document
    test_doc_path = os.path.join(new_docs_folder, "test_document.txt")
    with open(test_doc_path, "w", encoding="utf-8") as f:
        f.write("This is a test document for the classification system.")
    
    return test_doc_path

def cleanup_test_environment():
    """Removes test files and folders"""
    try:
        # Clean up the test folders
        for folder in DEFAULT_FOLDERS.values():
            folder_path = os.path.join(ROOT_FOLDER, folder)
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
        print("Test environment cleaned up successfully")
    except Exception as e:
        print(f"Error during cleanup: {e}")

def run_tests():
    try:
        # Setup test environment
        test_doc_path = setup_test_environment()
        print(f"Created test document at: {test_doc_path}")

        # Initialize pipeline
        pipeline = DocumentPipeline()
        print("Pipeline initialized")

        # Process the test document
        pipeline.process_new_document(test_doc_path)
        print("Document processed")

        # Verify the document was moved to processing
        processing_folder = os.path.join(ROOT_FOLDER, DEFAULT_FOLDERS["processing"])
        processed_files = os.listdir(processing_folder)
        print(f"Files in processing folder: {processed_files}")

    except Exception as e:
        print(f"Test failed with error: {e}")
    finally:
        cleanup_test_environment()

if __name__ == "__main__":
    run_tests() 