import os
import shutil
from pipeline_coordinator import DocumentPipeline
from config import ROOT_FOLDER, DEFAULT_FOLDERS

def create_test_document(folder_path: str, filename: str, content: str) -> str:
    """Creates a test document with specified content"""
    file_path = os.path.join(folder_path, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path

def test_duplicate_detection():
    """Tests the duplicate detection functionality"""
    try:
        new_docs_folder = os.path.join(ROOT_FOLDER, DEFAULT_FOLDERS["new"])
        if not os.path.exists(new_docs_folder):
            os.makedirs(new_docs_folder)

        # Create original document
        original_path = create_test_document(
            new_docs_folder,
            "original.txt",
            "This is a test document"
        )
        print(f"Created original document at: {original_path}")

        pipeline = DocumentPipeline()
        
        # Process original document
        pipeline.process_new_document(original_path)
        print("Processed original document")

        # Create duplicate document
        duplicate_path = create_test_document(
            new_docs_folder,
            "duplicate.txt",
            "This is a test document"
        )
        print(f"Created duplicate document at: {duplicate_path}")

        # Process duplicate document
        pipeline.process_new_document(duplicate_path)
        print("Processed duplicate document")

        # Verify duplicate was moved to duplicates folder
        duplicates_folder = os.path.join(ROOT_FOLDER, DEFAULT_FOLDERS["duplicates"])
        duplicate_files = os.listdir(duplicates_folder)
        print(f"Files in duplicates folder: {duplicate_files}")

        assert len(duplicate_files) == 1, "Expected one file in duplicates folder"
        print("Duplicate detection test passed!")

    except Exception as e:
        print(f"Duplicate detection test failed: {e}")
    finally:
        cleanup_test_environment()

if __name__ == "__main__":
    test_duplicate_detection() 