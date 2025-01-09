import json
import logging
import os
import shutil  # Import shutil for moving files

# --- Configuration ---
ROOT_FOLDER = "C:/Users/Maxim/Documents/VSCode/school_board_library/data/documents"  # Root folder location
INDEX_FILE = os.path.join(ROOT_FOLDER, "documents_index.json")  # Ensure index file is in the documents folder
IN_PROCESSING_FOLDER = os.path.join(ROOT_FOLDER, "In_Processing")  # Folder for documents in processing
CLASSIFIED_FOLDER = os.path.join(ROOT_FOLDER, "Classified")  # Folder for classified documents

# --- Logging Setup ---
LOGS_FOLDER = os.path.join(os.path.dirname(ROOT_FOLDER), "logs")
os.makedirs(LOGS_FOLDER, exist_ok=True)
LOG_FILE = os.path.join(LOGS_FOLDER, "document_classifier.log")
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load the decision tree
def load_decision_tree(filepath):
    """Loads the decision tree from a JSON file."""
    try:
        with open(filepath, "r") as f:
            decision_tree = json.load(f)
        return decision_tree
    except Exception as e:
        logging.error(f"Error loading decision tree: {e}")
        return None

# Placeholder classification functions
def classify_pdf_for_text(filepath):
    """Placeholder for PDF text classification."""
    # Implement logic to check if PDF contains text using PyMuPDF or pdfminer.six
    # For now, just return True
    return True  

def classify_pdf_for_images(filepath):
    """Placeholder for PDF image classification."""
    # Implement logic to check if PDF contains images using PyMuPDF
    # For now, just return True
    return True

def classify_pdf_for_tables(filepath):
    """Placeholder for PDF table classification."""
    # Implement logic to check if PDF contains tables using tabula-py
    # For now, just return False
    return False

def classify_docx_document(filepath):
    """Placeholder for DOCX classification."""
    # Implement logic to analyze DOCX structure using python-docx
    # For now, return a default value
    return "DOCX-Text-Only"  

def classify_image_document(filepath):
    """Placeholder for image classification."""
    # Implement logic for basic image analysis
    # For now, just return the default value
    return "Image-Only"

def classify_tiff_as_multipage(filepath):
    """Placeholder for TIFF multipage check."""
    # Implement logic to check if TIFF is multipage
    # For now, just return False
    return False

def classify_pptx_document(filepath):
    """Placeholder for PPTX classification."""
    # Implement logic to extract text and images from PPTX using python-pptx
    # For now, return a default value
    return "PPTX-Text-Only"

def classify_text_document(filepath):
    """Placeholder for TXT classification."""
    # Implement logic to analyze plain text content
    return "Text-Only"

def classify_csv_document(filepath):
    """Placeholder for CSV classification."""
    # Implement logic to analyze CSV structure
    return "Text-Only"

def classify_excel_document(filepath):
    """Placeholder for XLSX classification."""
    # Implement logic to analyze XLSX content
    return "Text-Only"

def classify_rtf_document(filepath):
    """Placeholder for RTF classification."""
    # Implement logic to analyze RTF content
    return "Text-Only"

def classify_html_document(filepath):
    """Placeholder for HTML classification."""
    # Implement logic to analyze HTML content
    return "Text-Only"

def classify_xml_document(filepath):
    """Placeholder for XML classification."""
    # Implement logic to analyze XML content
    return "Text-Only"

def classify_zip_contents(filepath):
    """Placeholder for ZIP classification."""
    # Implement logic to extract and classify ZIP contents
    return "Text-Only"

def classify_odt_document(filepath):
    """Placeholder for ODT classification."""
    # Implement logic to analyze ODT content
    return "Text-Only"

# --- Helper Functions ---
def get_file_extension(filepath):
    """Extracts the file extension from a filepath."""
    return os.path.splitext(filepath)[1].lower()

def determine_document_type(doc_id, index, primary_classification):
    """Determines the final document type based on primary and secondary classifications."""
    metadata = index[doc_id]["metadata"]

    # Handling for PDF documents
    if primary_classification == "PDF":
        if metadata.get("classify_pdf_for_text"):
            if metadata.get("classify_pdf_for_images"):
                return "Text-with-Images" if not metadata.get("classify_pdf_for_tables") else "Text-with-Images-and-Tables"
            elif metadata.get("classify_pdf_for_tables"):
                return "Text-with-Tables"
            else:
                return "Text-Only"
        elif metadata.get("classify_pdf_for_images"):
            return "Image-Only"
        else:
            return "PDF-Unknown"

    # Handling for DOCX documents
    elif primary_classification == "DOCX":
        if metadata.get("analyze_docx_structure") == "DOCX-Text-with-Images-and-Tables":
            return "Text-with-Images-and-Tables"
        elif metadata.get("analyze_docx_structure") == "DOCX-Text-with-Images":
            return "Text-with-Images"
        elif metadata.get("analyze_docx_structure") == "DOCX-Text-with-Tables":
            return "Text-with-Tables"
        elif metadata.get("analyze_docx_structure") == "DOCX-Text-Only":
            return "Text-Only"
        else:
            return "DOCX-Unknown"

    # Handling for image documents (JPEG, PNG, GIF, BMP)
    elif primary_classification in ("JPEG", "PNG", "GIF", "BMP"):
        return "Image-Only"

    # Handling for TIFF documents
    elif primary_classification == "TIFF":
        if metadata.get("classify_tiff_as_multipage"):
            return "Image-Only-Multi-Page"
        else:
            return "Image-Only-Single-Page"

    # Handling for PPTX documents
    elif primary_classification == "PPTX":
        if metadata.get("analyze_pptx_content") == "PPTX-Text-with-Images":
            return "Text-with-Images"
        elif metadata.get("analyze_pptx_content") == "PPTX-Text-Only":
            return "Text-Only"
        elif metadata.get("analyze_pptx_content") == "PPTX-Image-Only":
            return "Image-Only"
        else:
            return "PPTX-Unknown"

    # Handling for TXT, VTT, VRT, CSV, XLSX, RTF, HTML, XML, ZIP, ODT documents
    elif primary_classification in ("TXT", "VTT", "VRT", "CSV", "XLSX", "RTF", "HTML", "XML", "ZIP", "ODT"):
        return "Text-Only"

    # Default to primary classification if no specific logic is defined
    else:
        return primary_classification

def move_to_classified_folder(doc_id, doc_data, classified_folder):
    """Moves the document to the classified folder based on its document type."""
    document_type = doc_data["document_type"]
    destination_folder = os.path.join(classified_folder, document_type)
    os.makedirs(destination_folder, exist_ok=True)
    new_filepath = os.path.join(destination_folder, os.path.basename(doc_data["filepath"]))
    try:
        shutil.move(doc_data["filepath"], new_filepath)
        doc_data["filepath"] = new_filepath
        doc_data["status"] = "Classified"
        logging.info(f"Moved document {doc_id} to {destination_folder}")
    except Exception as e:
        logging.error(f"Error moving document {doc_id} to {destination_folder}: {e}")

# --- Main Classification Logic ---
def classify_document(doc_id, doc_data, decision_tree, use_case_to_function, index):
    """Classifies a document based on the decision tree."""
    filepath = doc_data["filepath"]
    extension = get_file_extension(filepath)

    if extension not in decision_tree:
        logging.warning(f"No classification rule found for extension '{extension}' (document ID: {doc_id})")
        return

    primary_classification = decision_tree[extension]["primary"]
    index[doc_id]["document_type"] = primary_classification
    index[doc_id]["metadata"]["document_type"] = primary_classification

    secondary_use_cases = decision_tree[extension]["secondary"]["use_cases"]

    # Execute use cases in order
    for use_case in secondary_use_cases:
        if use_case in use_case_to_function:
            classification_function = use_case_to_function[use_case]
            result = classification_function(filepath)
            if result:
                if isinstance(result, list):
                    for item in result:
                        index[doc_id]["metadata"][use_case] = item
                else:
                    index[doc_id]["metadata"][use_case] = result
                logging.info(f"Use case '{use_case}' returned: {result}")

    # Determine final document type
    document_type = determine_document_type(doc_id, index, primary_classification)
    index[doc_id]["document_type"] = document_type
    logging.info(f"Document {doc_id} classified as: {document_type}")

    # Move document to classified folder
    move_to_classified_folder(doc_id, doc_data, CLASSIFIED_FOLDER)

# --- Main Execution ---
if __name__ == "__main__":
    # Load the decision tree
    decision_tree = load_decision_tree("classification_decision_tree.json")
    if not decision_tree:
        exit(1)  # Exit if decision tree loading failed

    # Mapping of use cases to classification functions
    use_case_to_function = {
        "extract_text_from_pdf": classify_pdf_for_text,
        "detect_images_in_pdf": classify_pdf_for_images,
        "detect_tables_in_pdf": classify_pdf_for_tables,
        "analyze_docx_structure": classify_docx_document,
        "analyze_image_content": classify_image_document,
        "analyze_tiff_for_multi_page": classify_tiff_as_multipage,
        "analyze_pptx_content": classify_pptx_document,
        "analyze_txt_content": classify_text_document,
        "analyze_csv_structure": classify_csv_document,
        "analyze_xlsx_content": classify_excel_document,
        "analyze_rtf_content": classify_rtf_document,
        "analyze_html_structure": classify_html_document,
        "analyze_xml_structure": classify_xml_document,
        "extract_and_classify_zip": classify_zip_contents,
        "analyze_odt_structure": classify_odt_document,
    }

    # Load the document index
    try:
        with open(INDEX_FILE, "r") as f:
            index = json.load(f)
    except Exception as e:
        logging.error(f"Error loading document index: {e}")
        exit(1)  # Exit if document index loading failed

    # Classify documents in the In_Processing folder
    for doc_id, doc_data in index.items():
        if doc_data["status"] == "In_Processing":
            classify_document(doc_id, doc_data, decision_tree, use_case_to_function, index)

    # Save the updated document index
    try:
        with open(INDEX_FILE, "w") as f:
            json.dump(index, f, indent=4)
        logging.info("Updated document index saved successfully.")
    except Exception as e:
        logging.error(f"Error saving updated document index: {e}")