import os
import sys
import json

# =======================
# Configuration Section
# =======================

# Directory to scan for files (Example: "C:/school_board_library/data/raw_document")
# This can be passed as a command-line argument or set directly.
SOURCE_DIR = r"C:/school_board_library/data/raw_documents"

# Directory to save the JSON index (Example: "C:/school_board_library/data")
DESTINATION_DIR = r"C:/school_board_library/data"

# Name of the output JSON file
OUTPUT_FILE = "1_available_files.json"

# Supported file extensions
SUPPORTED_EXTENSIONS = ['.pdf', '.txt']

# =======================
# Indexing Functionality
# =======================

def index_documents(source_dir, destination_dir, output_file):
    """
    Scans the source directory for supported files and indexes their paths into a JSON file.

    Parameters:
        source_dir (str): Directory to scan for files.
        destination_dir (str): Directory to save the JSON index.
        output_file (str): Name of the output JSON file.
    """
    if not os.path.isdir(source_dir):
        print(f"❌ Source directory does not exist: {source_dir}", file=sys.stderr)
        sys.exit(1)
    
    os.makedirs(destination_dir, exist_ok=True)
    
    available_files = []
    print(f"🔍 Scanning directory: {source_dir}")
    
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext.lower() in SUPPORTED_EXTENSIONS:
                file_path = os.path.join(root, file).replace("\\", "/")
                available_files.append({"path": file_path})
                print(f"✅ Indexed file: {file_path}")
            else:
                print(f"ℹ️ Skipping unsupported file: {file}")
    
    if available_files:
        output_path = os.path.join(destination_dir, output_file)
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(available_files, f, indent=4)
            print(f"📄 Successfully indexed {len(available_files)} files to '{output_path}'.")
        except Exception as e:
            print(f"❌ Failed to write JSON file '{output_path}': {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("⚠️ No supported files found to index.")

# =======================
# Main Execution
# =======================

def main():
    """
    Main function to execute the indexing process.
    """
    # Optional: Allow command-line arguments for flexibility
    if len(sys.argv) == 4:
        source_dir = sys.argv[1]
        destination_dir = sys.argv[2]
        output_file = sys.argv[3]
    else:
        source_dir = SOURCE_DIR
        destination_dir = DESTINATION_DIR
        output_file = OUTPUT_FILE
    
    index_documents(source_dir, destination_dir, output_file)

if __name__ == "__main__":
    main()