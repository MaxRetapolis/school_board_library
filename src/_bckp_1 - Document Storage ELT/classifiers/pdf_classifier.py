"""
pdf_classifier.py

Contains classification logic for PDF documents:
1. Detect presence of text
2. Detect presence of images
3. Detect presence of tables
"""

import logging
import fitz  # PyMuPDF
import tabula

def classify_pdf(filepath: str) -> dict:
    """
    Classify a PDF by checking if it contains text, images, and/or tables.
    
    Args:
        filepath (str): Path to the PDF file.
        
    Returns:
        dict: A dictionary with keys "Text", "Images", and "Tables" 
              each set to "Yes", "No", or "Unknown".
    """
    classification_results = {
        "Text": "No",
        "Images": "No",
        "Tables": "No"
    }

    # 1) Detect text
    try:
        if pdf_has_text(filepath):
            classification_results["Text"] = "Yes"
    except Exception as e:
        logging.error(f"Error detecting text in PDF: {e}")
        classification_results["Text"] = "Unknown"

    # 2) Detect images
    try:
        if pdf_has_images(filepath):
            classification_results["Images"] = "Yes"
    except Exception as e:
        logging.error(f"Error detecting images in PDF: {e}")
        classification_results["Images"] = "Unknown"

    # 3) Detect tables
    try:
        if pdf_has_tables(filepath):
            classification_results["Tables"] = "Yes"
    except Exception as e:
        logging.error(f"Error detecting tables in PDF: {e}")
        classification_results["Tables"] = "Unknown"

    return classification_results

def pdf_has_text(filepath: str) -> bool:
    """
    Returns True if any page in the PDF has non-empty text.
    """
    with fitz.open(filepath) as doc:
        for page_num in range(len(doc)):
            text = doc.load_page(page_num).get_text().strip()
            if text:
                return True
    return False

def pdf_has_images(filepath: str) -> bool:
    """
    Returns True if any page in the PDF contains images.
    """
    with fitz.open(filepath) as doc:
        for page_num in range(len(doc)):
            images = doc.load_page(page_num).get_images(full=True)
            if images:
                return True
    return False

def pdf_has_tables(filepath: str) -> bool:
    """
    Returns True if Tabula detects tables in the PDF.
    """
    # tabula.read_pdf can raise errors with certain PDFs or if Java isn't configured
    tables = tabula.read_pdf(filepath, pages='all', multiple_tables=True)
    return bool(tables)
