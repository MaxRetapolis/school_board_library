"""
Fallback MIME type detector that uses Python's built-in mimetypes module.
This is used when python-magic is not available.
"""

import os
import mimetypes
import logging
from typing import Union, BinaryIO, TextIO

# Initialize mimetypes
mimetypes.init()

# Set up logging
logger = logging.getLogger(__name__)

def sample_is_text(file_path: str, sample_size: int = 2048) -> bool:
    """
    Sample the beginning of a file to determine if it's likely a text file.
    
    Args:
        file_path: Path to the file to sample
        sample_size: Number of bytes to sample (default: 2KB)
        
    Returns:
        bool: True if the file appears to be text, False otherwise
    """
    try:
        with open(file_path, 'rb') as f:
            sample = f.read(sample_size)
            
        # Check if sample contains mostly printable ASCII characters
        if not sample:
            return False
            
        # Count printable ASCII characters (32-126) and common whitespace/control chars
        printable_count = sum(32 <= b <= 126 or b in (9, 10, 13) for b in sample)
        
        # If sample is >70% printable ASCII, it's likely text
        text_ratio = printable_count / len(sample)
        
        # Log the results for debugging
        if text_ratio > 0.7:
            logger.debug(f"File {file_path} appears to be text (ratio: {text_ratio:.2f})")
        else:
            logger.debug(f"File {file_path} doesn't appear to be text (ratio: {text_ratio:.2f})")
            
        return text_ratio > 0.7
    except Exception as e:
        logger.warning(f"Error sampling file {file_path}: {str(e)}")
        return False

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
                elif ext in ['.vtt', '.webvtt']:
                    mime_type = 'text/vtt'  # WebVTT subtitle format
                elif ext == '.srt':
                    mime_type = 'text/srt'  # SRT subtitle format
                elif ext == '.doc':
                    mime_type = 'application/msword'
                elif ext == '.docx':
                    mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                else:
                    # Try to detect if it's a text file by sampling content
                    if isinstance(file_path_or_object, str) and os.path.exists(file_path_or_object):
                        if sample_is_text(file_path_or_object):
                            mime_type = 'text/plain'
                        else:
                            mime_type = 'application/octet-stream'  # Default binary type
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