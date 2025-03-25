from typing import Dict, Optional, Any, Union


def classify_document(features: Dict[str, Any]) -> str:
    """
    Classifies a document based on its extracted features.
    
    Args:
        features: Dictionary with 'mime_type' (str) and 'has_text_layer' (bool or None).
        
    Returns:
        str: One of 'Text-based PDF', 'Text-based non-PDF', 'Image-based document', or 'Unknown'.
        
    Raises:
        KeyError: If the features dictionary is missing required keys.
    """
    # Validate features dictionary
    if 'mime_type' not in features:
        raise KeyError("Missing required feature: 'mime_type'")
    
    mime_type = features['mime_type']
    has_text_layer = features.get('has_text_layer', None)  # None for non-PDFs
    
    # Classification rules
    # Rule 1: Text-based PDF
    if mime_type == "application/pdf" and has_text_layer is True:
        return "Text-based PDF"
    
    # Rule 2: Image-based document
    if (mime_type == "application/pdf" and has_text_layer is False) or \
       mime_type in ["image/jpeg", "image/png", "image/tiff", "image/bmp"]:
        return "Image-based document"
    
    # Rule 3: Text-based non-PDF
    if mime_type in [
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "application/rtf"
    ]:
        return "Text-based non-PDF"
    
    # Default: Unknown
    return "Unknown"
