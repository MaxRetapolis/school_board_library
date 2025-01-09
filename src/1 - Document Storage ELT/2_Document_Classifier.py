import json
import logging
import os
import shutil  # Import shutil for moving files
import fitz  # Import PyMuPDF for PDF processing
import tabula  # Import tabula-py for table extraction
from docx import Document as DocxDocument  # Import python-docx for DOCX processing
from PIL import Image  # Import Pillow for image processing
from pptx import Presentation  # Import python-pptx for PPTX processing
import pandas as pd  # Import pandas for CSV and Excel processing
import pypandoc  # Import pypandoc for RTF processing
from bs4 import BeautifulSoup  # Import BeautifulSoup for HTML processing
import xml.etree.ElementTree as ET  # Import ElementTree for XML processing
import zipfile  # Import zipfile for ZIP processing
from odf.opendocument import load  # Import odfpy for ODT processing
from odf.text import P  # Import odfpy text elements
from odf.draw import Image as ODFImage  # Import odfpy image elements
from odf.table import Table  # Import odfpy table elements

# --- Configuration ---
ROOT_FOLDER = "C:/Users/Maxim/Documents/VSCode/school_board_library/data/documents"  # Root folder location
INDEX_FILE = os.path.join(ROOT_FOLDER, "documents_index.json")  # Ensure index file is in the documents folder
IN_PROCESSING_FOLDER = os.path.join(ROOT_FOLDER, "In_Processing")  # Folder for documents in processing
CLASSIFIED_FOLDER = os.path.join(ROOT_FOLDER, "Classified")  # Folder for classified documents
COMBINATIONS_FILE = os.path.join(ROOT_FOLDER, "classification_combinations.json")  # File to store classification combinations

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

# Classification functions
def classify_pdf_for_text(filepath):
    """Classifies a PDF document to check if it contains text."""
    try:
        doc = fitz.open(filepath)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text.strip():  # Check if the extracted text is non-empty
                return True
        return False
    except Exception as e:
        logging.error(f"Error classifying PDF for text: {e}")
        return False

def classify_pdf_for_images(filepath):
    """Classifies a PDF document to check if it contains images."""
    try:
        doc = fitz.open(filepath)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            images = page.get_images(full=True)
            if images:  # Check if any images are found
                return True
        return False
    except Exception as e:
        logging.error(f"Error classifying PDF for images: {e}")
        return False

def classify_pdf_for_tables(filepath):
    """Classifies a PDF document to check if it contains tables."""
    try:
        tables = tabula.read_pdf(filepath, pages='all', multiple_tables=True)
        if tables:  # Check if any tables are found
            return True
        return False
    except Exception as e:
        logging.error(f"Error classifying PDF for tables: {e}")
        return False

def classify_docx_document(filepath):
    """Classifies a DOCX document to analyze its structure."""
    try:
        doc = DocxDocument(filepath)
        has_text = False
        has_images = False
        has_tables = False

        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                has_text = True
                break

        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                has_images = True
                break

        if doc.tables:
            has_tables = True

        if has_text and has_images and has_tables:
            return "DOCX-Text-with-Images-and-Tables"
        elif has_text and has_images:
            return "DOCX-Text-with-Images"
        elif has_text and has_tables:
            return "DOCX-Text-with-Tables"
        elif has_text:
            return "DOCX-Text-Only"
        else:
            return "DOCX-Unknown"
    except Exception as e:
        logging.error(f"Error classifying DOCX document: {e}")
        return "DOCX-Unknown"

def classify_image_document(filepath):
    """Classifies an image document to analyze its content."""
    try:
        with Image.open(filepath) as img:
            format = img.format
            size = img.size
            mode = img.mode
            return f"Image-{format}-{size[0]}x{size[1]}-{mode}"
    except Exception as e:
        logging.error(f"Error classifying image document: {e}")
        return "Image-Unknown"

def classify_tiff_as_multipage(filepath):
    """Classifies a TIFF document to check if it is multipage."""
    try:
        with Image.open(filepath) as img:
            if getattr(img, "n_frames", 1) > 1:  # Check if the TIFF has multiple frames
                return True
        return False
    except Exception as e:
        logging.error(f"Error classifying TIFF as multipage: {e}")
        return False

def classify_pptx_document(filepath):
    """Classifies a PPTX document to analyze its structure."""
    try:
        presentation = Presentation(filepath)
        has_text = False
        has_images = False

        for slide in presentation.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    has_text = True
                if shape.shape_type == 13:  # Shape type 13 corresponds to pictures
                    has_images = True

        if has_text and has_images:
            return "PPTX-Text-with-Images"
        elif has_text:
            return "PPTX-Text-Only"
        elif has_images:
            return "PPTX-Image-Only"
        else:
            return "PPTX-Unknown"
    except Exception as e:
        logging.error(f"Error classifying PPTX document: {e}")
        return "PPTX-Unknown"

def classify_text_document(filepath):
    """Classifies a TXT document to analyze its content."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()
            if content.strip():  # Check if the text content is non-empty
                return "Text-Only"
            else:
                return "Text-Empty"
    except Exception as e:
        logging.error(f"Error classifying TXT document: {e}")
        return "Text-Unknown"

def classify_csv_document(filepath):
    """Classifies a CSV document to analyze its structure."""
    try:
        df = pd.read_csv(filepath)
        if not df.empty:  # Check if the DataFrame is not empty
            return "Table-Only"
        else:
            return "Table-Empty"
    except Exception as e:
        logging.error(f"Error classifying CSV document: {e}")
        return "Table-Unknown"

def classify_excel_document(filepath):
    """Classifies an Excel document (XLS/XLSX) to analyze its structure."""
    try:
        if filepath.endswith('.xlsx'):
            df = pd.read_excel(filepath, engine='openpyxl')
        elif filepath.endswith('.xls'):
            df = pd.read_excel(filepath, engine='xlrd')
        else:
            return "Table-Unknown"

        if not df.empty:  # Check if the DataFrame is not empty
            return "Table-Only"
        else:
            return "Table-Empty"
    except Exception as e:
        logging.error(f"Error classifying Excel document: {e}")
        return "Table-Unknown"

def classify_rtf_document(filepath):
    """Classifies an RTF document to analyze its content."""
    try:
        content = pypandoc.convert_file(filepath, 'plain')
        if content.strip():  # Check if the text content is non-empty
            return "Text-Only"
        else:
            return "Text-Empty"
    except Exception as e:
        logging.error(f"Error classifying RTF document: {e}")
        return "Text-Unknown"

def classify_html_document(filepath):
    """Classifies an HTML document to analyze its content."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
            has_text = bool(soup.get_text(strip=True))
            has_images = bool(soup.find_all("img"))
            if has_text and has_images:
                return "HTML-Text-with-Images"
            elif has_text:
                return "HTML-Text-Only"
            elif has_images:
                return "HTML-Image-Only"
            else:
                return "HTML-Unknown"
    except Exception as e:
        logging.error(f"Error classifying HTML document: {e}")
        return "HTML-Unknown"

def classify_xml_document(filepath):
    """Classifies an XML document to analyze its content."""
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        has_text = bool(root.text.strip() if root.text else False)
        has_elements = bool(root.findall(".//*"))
        if has_text and has_elements:
            return "XML-Text-with-Elements"
        elif has_text:
            return "XML-Text-Only"
        elif has_elements:
            return "XML-Elements-Only"
        else:
            return "XML-Unknown"
    except Exception as e:
        logging.error(f"Error classifying XML document: {e}")
        return "XML-Unknown"

def classify_zip_contents(filepath):
    """Classifies a ZIP document to analyze its content."""
    try:
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            if zip_ref.namelist():  # Check if the ZIP file contains any files
                return "Archive"
            else:
                return "Archive-Empty"
    except Exception as e:
        logging.error(f"Error classifying ZIP document: {e}")
        return "Archive-Unknown"

def classify_odt_document(filepath):
    """Classifies an ODT document to analyze its structure."""
    try:
        doc = load(filepath)
        has_text = False
        has_images = False
        has_tables = False

        for element in doc.getElementsByType(P):
            if element.text.strip():
                has_text = True
                break

        for element in doc.getElementsByType(ODFImage):
            has_images = True
            break

        for element in doc.getElementsByType(Table):
            has_tables = True
            break

        if has_text and has_images and has_tables:
            return "ODT-Text-with-Images-and-Tables"
        elif has_text and has_images:
            return "ODT-Text-with-Images"
        elif has_text and has_tables:
            return "ODT-Text-with-Tables"
        elif has_text:
            return "ODT-Text-Only"
        else:
            return "ODT-Unknown"
    except Exception as e:
        logging.error(f"Error classifying ODT document: {e}")
        return "ODT-Unknown"

def update_classification_combinations(primary_classification, secondary_classifications):
    """Updates the classification combinations file with new combinations."""
    try:
        if os.path.exists(COMBINATIONS_FILE):
            with open(COMBINATIONS_FILE, "r") as f:
                combinations = json.load(f)
        else:
            combinations = []

        new_combination = {
            "primary_classification": primary_classification,
            "secondary_classifications": secondary_classifications
        }

        if new_combination not in combinations:
            combinations.append(new_combination)
            with open(COMBINATIONS_FILE, "w") as f:
                json.dump(combinations, f, indent=4)
            logging.info(f"Updated classification combinations with: {new_combination}")
    except Exception as e:
        logging.error(f"Error updating classification combinations: {e}")

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

    # Handling for TXT, VTT, VRT, CSV, XLS, XLSX, RTF, HTML, XML, ZIP, ODT documents
    elif primary_classification in ("TXT", "VTT", "VRT", "CSV", "XLS", "XLSX", "RTF", "HTML", "XML", "ZIP", "ODT"):
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
    secondary_classifications = []

    # Execute use cases in order
    for use_case in secondary_use_cases:
        if use_case in use_case_to_function:
            classification_function = use_case_to_function[use_case]
            result = classification_function(filepath)
            if result:
                if isinstance(result, list):
                    for item in result:
                        index[doc_id]["metadata"][use_case] = item
                        secondary_classifications.append(use_case)
                else:
                    index[doc_id]["metadata"][use_case] = result
                    secondary_classifications.append(use_case)
                logging.info(f"Use case '{use_case}' returned: {result}")

    # Determine final document type
    document_type = determine_document_type(doc_id, index, primary_classification)
    index[doc_id]["document_type"] = document_type
    logging.info(f"Document {doc_id} classified as: {document_type}")

    # Update classification combinations
    update_classification_combinations(primary_classification, secondary_classifications)

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