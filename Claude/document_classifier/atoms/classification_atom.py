from typing import Dict, Optional, Any, Union
import logging

# Set up logging
logger = logging.getLogger(__name__)

def classify_document(features: Dict[str, Any]) -> str:
    """
    Classifies a document based on its extracted features.
    
    Args:
        features: Dictionary with 'mime_type' (str) and 'has_text_layer' (bool or None).
        Optional keys include 'using_fallback_mime' and 'using_fallback_pdf' to indicate
        if fallback detection methods were used.
        
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
    using_fallback_mime = features.get('using_fallback_mime', False)
    using_fallback_pdf = features.get('using_fallback_pdf', False)
    
    # Log if we're using fallback methods
    if using_fallback_mime or using_fallback_pdf:
        logger.warning(f"Using fallbacks - mime: {using_fallback_mime}, pdf: {using_fallback_pdf}")
        logger.warning("Classification may be less accurate due to fallback detection methods")
    
    # If using fallback PDF detection, we need to be cautious about PDF text layer determination
    if using_fallback_pdf and mime_type == 'application/pdf':
        logger.info("Using fallback PDF text layer detection based on file extension only")
    
    # Get OCR needs feature if available
    needs_ocr = features.get('needs_ocr', False)
    
    # Classification rules
    # Rule 1a: Text-based PDF with images (mixed content)
    if mime_type == "application/pdf" and has_text_layer is True and needs_ocr is True:
        return "PDF-Text-With-Images"
        
    # Rule 1b: Text-based PDF
    if mime_type == "application/pdf" and has_text_layer is True:
        return "Text-based PDF"
    
    # Rule 2: Image-based document
    if (mime_type == "application/pdf" and has_text_layer is False) or \
       mime_type in ["image/jpeg", "image/png", "image/tiff", "image/bmp"]:
        return "Image-based document"
    
    # Rule 3a: Special text formats
    if mime_type in ["text/vtt", "text/srt"]:
        return "Plain-Text-Special-Format"
    
    # Rule 3b: Text-based non-PDF
    if mime_type in [
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "application/rtf"
    ]:
        return "Text-based non-PDF"
    
    # Rule 4: Binary files that are actually text-based
    if using_fallback_mime and 'is_text' in features and features['is_text'] is True:
        return "Text-based non-PDF"
    
    # Default: Unknown
    return "Unknown"
