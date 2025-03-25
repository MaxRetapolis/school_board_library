import PyPDF2
from typing import Union, BinaryIO, TextIO, Optional
import os


def has_text_layer(file_path_or_object: Union[str, BinaryIO, TextIO]) -> bool:
    """
    Checks if a PDF has an extractable text layer using PyPDF2.
    
    Args:
        file_path_or_object: Either a file path (str) or a file object.
        
    Returns:
        bool: True if the PDF has extractable text, False otherwise.
        
    Raises:
        FileNotFoundError: If the file path is invalid or file doesn't exist.
        ValueError: If the input is not a PDF or is corrupted.
    """
    try:
        # Handle file path or file object
        if isinstance(file_path_or_object, str):
            if not os.path.exists(file_path_or_object):
                raise FileNotFoundError(f"File not found: {file_path_or_object}")
            pdf_reader = PyPDF2.PdfReader(file_path_or_object)
        elif hasattr(file_path_or_object, 'read'):
            # For file objects
            pdf_reader = PyPDF2.PdfReader(file_path_or_object)
        else:
            raise ValueError("Input must be either a file path or a file object")
        
        # Check if the PDF has any extractable text
        if len(pdf_reader.pages) == 0:
            return False
        
        # Check each page for text
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text and text.strip():  # If any page has text, return True
                return True
        
        return False  # No text found in any page
    except PyPDF2.errors.PdfReadError:
        raise ValueError("Invalid or corrupted PDF file")
    except Exception as e:
        if isinstance(e, (FileNotFoundError, ValueError)):
            raise
        raise ValueError(f"Error checking PDF text layer: {str(e)}")
