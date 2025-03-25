import magic
from typing import Union, BinaryIO, TextIO
import os


def detect_mime_type(file_path_or_object: Union[str, BinaryIO, TextIO]) -> str:
    """
    Detects the MIME type of a file using the python-magic library.
    
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
            mime_type = magic.from_file(file_path_or_object, mime=True)
        elif hasattr(file_path_or_object, 'read'):
            # If it's a file object, we need to read from it without changing position
            current_pos = file_path_or_object.tell()
            try:
                file_path_or_object.seek(0)
                data = file_path_or_object.read(2048)  # Read first 2KB for MIME detection
                if isinstance(data, str):
                    data = data.encode('utf-8')  # Convert to bytes if it's a text file
                mime_type = magic.from_buffer(data, mime=True)
            finally:
                # Return to the original position
                file_path_or_object.seek(current_pos)
        else:
            raise ValueError("Input must be either a file path or a file object")
        
        return mime_type
    except Exception as e:
        if isinstance(e, (FileNotFoundError, ValueError)):
            raise
        raise ValueError(f"Error detecting MIME type: {str(e)}")
