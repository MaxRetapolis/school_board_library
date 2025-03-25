"""
Fallback PDF text layer detector that checks file extension.
This is used when PyPDF2 is not available.
"""

import os
from typing import Union, BinaryIO, TextIO

def has_text_layer_fallback(file_path_or_object: Union[str, BinaryIO, TextIO]) -> bool:
    """
    A fallback function that checks if a file is a PDF based on extension.
    Since we can't check for text layer without PyPDF2, we assume PDFs have text.
    
    Args:
        file_path_or_object: Either a file path (str) or a file object.
        
    Returns:
        bool: True if the file is a PDF (assuming it has text), False otherwise.
        
    Raises:
        FileNotFoundError: If the file path is invalid or file doesn't exist.
        ValueError: If the input is neither a valid file path nor a file object.
    """
    try:
        if isinstance(file_path_or_object, str):
            if not os.path.exists(file_path_or_object):
                raise FileNotFoundError(f"File not found: {file_path_or_object}")
            
            # Check if file has .pdf extension
            return file_path_or_object.lower().endswith('.pdf')
        
        elif hasattr(file_path_or_object, 'name'):
            # If it's a file object with a name attribute
            return file_path_or_object.name.lower().endswith('.pdf')
        
        else:
            # For file objects without names, we can't determine if it's a PDF
            raise ValueError("File objects must have a 'name' attribute for fallback PDF detection")
        
    except Exception as e:
        if isinstance(e, (FileNotFoundError, ValueError)):
            raise
        raise ValueError(f"Error detecting PDF: {str(e)}")