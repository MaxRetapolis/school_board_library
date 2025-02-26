import os
import sys
import json
from datetime import datetime
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

# =======================
# Configuration Section
# =======================

# Path to the index JSON file
INDEX_FILE_PATH = r"C:\school_board_library\experiments\1_prelearning\data\1_available_files.json"

# Poppler bin path
POPPLER_PATH = r"C:\poppler\Library\bin"

# Tesseract executable path
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Output directory
OUTPUT_DIR = r"C:\school_board_library\experiments\1_prelearning\data\processed_text"

# =======================
# Processing Functions
# =======================

# Configure pytesseract to use the specified Tesseract executable
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def process_text_file(file_path, output_path):
    """
    Copies the content of a plain text file to the output path.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f_src:
            content = f_src.read()
        with open(output_path, 'w', encoding='utf-8') as f_dst:
            f_dst.write(content)
        return True
    except Exception as e:
        print(f"Failed to process text file {file_path}: {e}")
        return False

def process_pdf_with_text(file_path, output_path):
    """
    Attempts to extract text from a PDF using PyPDF2.
    Returns True if text is extracted and written to the output path; otherwise, False.
    """
    try:
        reader = PdfReader(file_path)
        text_content = ""
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text:
                text_content += f"\n\nPage {page_num}:\n{text}"
        if text_content.strip():
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            return True
        return False
    except Exception as e:
        print(f"Failed to extract text from PDF {file_path}: {e}")
        return False

def process_pdf_with_ocr(file_path, output_path):
    """
    Converts each page of the PDF to an image and performs OCR using pytesseract.
    Writes the extracted text to the output path.
    """
    try:
        images = convert_from_path(file_path, poppler_path=POPPLER_PATH)
        text_content = ""
        for page_number, image in enumerate(images, start=1):
            text = pytesseract.image_to_string(image)
            text_content += f"\n\nPage {page_number}:\n{text}"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        return True
    except Exception as e:
        print(f"Failed to perform OCR on PDF {file_path}: {e}")
        return False

# =======================
# Main Processing Loop
# =======================

def main():
    # Load the index of available files
    try:
        with open(INDEX_FILE_PATH, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
    except FileNotFoundError:
        print(f"Index file not found at {INDEX_FILE_PATH}. Please ensure the file exists.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {INDEX_FILE_PATH}: {e}")
        sys.exit(1)

    # Validate that index_data is a list
    if not isinstance(index_data, list):
        print(f"Unexpected index data format: Expected a list, got {type(index_data)}")
        sys.exit(1)

    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Process each item in the index
    for index, item in enumerate(index_data, start=1):
        print(f"\nProcessing Item {index}/{len(index_data)}:")

        # Debug: Print item keys and content
        print(f"Item keys: {item.keys()}")
        print(f"Item content: {item}")

        # Safely get the 'path' value
        file_path = item.get('path')
        if not file_path:
            print(f"⚠️ Warning: 'path' key missing in item {index}. Skipping this item.")
            continue

        # Check if the file exists
        if not os.path.isfile(file_path):
            print(f"⚠️ Warning: File does not exist at {file_path}. Skipping.")
            continue

        # Extract file extension and name
        file_ext = os.path.splitext(file_path)[1].lower()
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file_path = os.path.join(OUTPUT_DIR, f"{file_name}.txt")

        print(f"📂 File Path: {file_path}")
        print(f"📄 File Extension: {file_ext}")
        print(f"📝 Output File Path: {output_file_path}")

        try:
            if file_ext == '.txt':
                success = process_text_file(file_path, output_file_path)
                if success:
                    print(f"✅ Copied text file to {output_file_path}")
                else:
                    print(f"❌ Failed to copy text file {file_path}")

            elif file_ext == '.pdf':
                print("🔍 Attempting to extract text from PDF...")
                if process_pdf_with_text(file_path, output_file_path):
                    print(f"✅ Extracted text from PDF to {output_file_path}")
                else:
                    print("⚠️ No text extracted from PDF. Performing OCR...")
                    if process_pdf_with_ocr(file_path, output_file_path):
                        print(f"✅ OCR complete. Saved to {output_file_path}")
                    else:
                        print(f"❌ Failed to perform OCR on {file_path}")
            else:
                print(f"🚫 Unsupported file format: {file_ext}. Skipping.")
        except Exception as e:
            print(f"🔴 Error processing {file_path}: {e}")

    print("\n✅ All files processed.")

if __name__ == "__main__":
    main()