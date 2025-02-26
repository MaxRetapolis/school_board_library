import os
import json

# =======================
# Configuration Section
# =======================

# Directory to scan for files
SCAN_DIR = r"C:\school_board_library\data\raw_documents"

# Supported file extensions
SUPPORTED_EXTENSIONS = ['.pdf', '.txt']

# Output JSON file path
OUTPUT_INDEX = r"C:\school_board_library\experiments\1_prelearning\data\1_available_files.json"

# =======================
# Indexing Functionality
# =======================

def index_files(scan_dir, supported_extensions, output_file):
    """
    Scans the specified directory for files with supported extensions and
    writes their paths to a JSON file.
    """
    available_files = []
    print(f"🔍 Scanning directory: {scan_dir}")

    if not os.path.isdir(scan_dir):
        print(f"❌ Error: The directory '{scan_dir}' does not exist.")
        return

    for root, dirs, files in os.walk(scan_dir):
        for file in files:
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext in supported_extensions:
                file_path = os.path.join(root, file)
                # Normalize the path to use forward slashes
                file_path = file_path.replace("\\", "/")
                available_files.append({"path": file_path})
                print(f"✅ Found supported file: {file_path}")
            else:
                print(f"ℹ️ Skipping unsupported file: {file}")

    if available_files:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(available_files, f, indent=4)
            print(f"📄 Successfully indexed {len(available_files)} files.")
            print(f"🗂️ Output JSON file created at: {output_file}")
        except Exception as e:
            print(f"❌ Failed to write to JSON file '{output_file}': {e}")
    else:
        print("⚠️ No supported files found to index.")

# =======================
# Main Execution
# =======================

if __name__ == "__main__":
    index_files(SCAN_DIR, SUPPORTED_EXTENSIONS, OUTPUT_INDEX)