"""
Fallback MIME type detector that uses Python's built-in mimetypes module.
This is used when python-magic is not available.
"""

import os
import mimetypes
from typing import Union, BinaryIO, TextIO

# Initialize mimetypes
mimetypes.init()

def detect_mime_type_fallback(file_path_or_object: Union[str, BinaryIO, TextIO]) -> str:
    """
    Detects the MIME type of a file using Python's built-in mimetypes module.
    This is a fallback when python-magic is not available.
    
    Args:
        file_path_or_object: Either a file path (str) or a file object.
        
    Returns:
        str: The detected MIME type (e.g., 'application/pdf', 'image/jpeg').
        
    Raises:
        FileNotFoundError: If the file path is invalid or file doesn't exist.
        ValueError: If the input is neither a valid file path nor a file object.
    """
    try:
        if isinstance(file_path_or_object, str):
            if not os.path.exists(file_path_or_object):
                raise FileNotFoundError(f"File not found: {file_path_or_object}")
            
            # Get file extension and use mimetypes to guess the type
            mime_type, encoding = mimetypes.guess_type(file_path_or_object)
            
            # Handle common file types that might not be in mimetypes
            if mime_type is None:
                ext = os.path.splitext(file_path_or_object)[1].lower()
                if ext == '.pdf':
                    mime_type = 'application/pdf'
                elif ext in ['.jpg', '.jpeg']:
                    mime_type = 'image/jpeg'
                elif ext == '.png':
                    mime_type = 'image/png'
                elif ext == '.txt':
                    mime_type = 'text/plain'
                elif ext == '.doc':
                    mime_type = 'application/msword'
                elif ext == '.docx':
                    mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                else:
                    mime_type = 'application/octet-stream'  # Default binary type
            
            return mime_type
        
        elif hasattr(file_path_or_object, 'name'):
            # If it's a file object with a name attribute
            return detect_mime_type_fallback(file_path_or_object.name)
        
        else:
            # For file objects without names, we can't reliably determine the type
            # without reading content, so return a generic type
            raise ValueError("File objects must have a 'name' attribute for fallback MIME type detection")
        
    except Exception as e:
        if isinstance(e, (FileNotFoundError, ValueError)):
            raise
        raise ValueError(f"Error detecting MIME type: {str(e)}")