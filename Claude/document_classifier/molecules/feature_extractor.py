from typing import Dict, Union, BinaryIO, TextIO, Any, Optional
import os
import importlib.util
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Try to import the required atoms - if not available, use fallbacks
try:
    from Claude.document_classifier.atoms.mime_type_detector import detect_mime_type
    USING_MAGIC = True
except ImportError:
    logger.warning("python-magic not available, using fallback MIME type detector")
    from Claude.document_classifier.atoms.fallback_mime_detector import detect_mime_type_fallback as detect_mime_type
    from Claude.document_classifier.atoms.fallback_mime_detector import sample_is_text
    USING_MAGIC = False

try:
    from Claude.document_classifier.atoms.pdf_text_layer_detector import has_text_layer
    USING_PYPDF2 = True
except ImportError:
    logger.warning("PyPDF2 not available, using fallback PDF detector")
    from Claude.document_classifier.atoms.fallback_pdf_detector import has_text_layer_fallback as has_text_layer
    USING_PYPDF2 = False

# Try to import the PDF OCR detector
try:
    from Claude.document_classifier.atoms.pdf_ocr_detector import analyze_pdf_content
    USING_OCR_DETECTOR = True
except ImportError:
    logger.warning("PDF OCR detector not available, using fallback method")
    from Claude.document_classifier.atoms.pdf_ocr_detector import needs_ocr_fallback
    USING_OCR_DETECTOR = False


class FeatureExtractor:
    """
    Class for extracting features from documents for classification.
    
    This molecule combines the MIME type detector and PDF text layer detector
    atoms to extract relevant features from a document.
    """
    
    def extract_features(self, file_path_or_object: Union[str, BinaryIO, TextIO]) -> Dict[str, Any]:
        """
        Extracts features from a document.
        
        Args:
            file_path_or_object: Either a file path (str) or a file object.
            
        Returns:
            Dict[str, Any]: Dictionary with features including:
                - 'mime_type' (str)
                - 'has_text_layer' (bool or None)
                - 'needs_ocr' (bool) - True if PDF contains images that need OCR
                - 'is_text' (bool) - True if file appears to be text-based
                - Various implementation flags
            
        Raises:
            FileNotFoundError: If the file path is invalid or file doesn't exist.
            ValueError: If there's an error processing the file.
        """
        try:
            # Log which implementation we're using
            logger.debug(f"Using python-magic: {USING_MAGIC}, Using PyPDF2: {USING_PYPDF2}, Using OCR detector: {USING_OCR_DETECTOR}")
            
            # Get the MIME type
            mime_type = detect_mime_type(file_path_or_object)
            logger.debug(f"Detected MIME type: {mime_type}")
            
            # Initialize features dictionary
            features = {
                'mime_type': mime_type,
                'has_text_layer': None,  # Default value
                'needs_ocr': False,      # Default value
                'is_text': False,        # Default value
                'using_fallback_mime': not USING_MAGIC,
                'using_fallback_pdf': not USING_PYPDF2,
                'using_fallback_ocr': not USING_OCR_DETECTOR
            }
            
            # For file path strings, do additional analysis
            if isinstance(file_path_or_object, str) and os.path.exists(file_path_or_object):
                file_path = file_path_or_object
                
                # Check for text layer if it's a PDF
                if mime_type == "application/pdf":
                    features['has_text_layer'] = has_text_layer(file_path)
                    logger.debug(f"PDF text layer detection result: {features['has_text_layer']}")
                    
                    if not USING_PYPDF2:
                        logger.warning("Using fallback PDF detector - assuming PDFs have text based on extension only")
                    
                    # Check if PDF needs OCR (has images with text)
                    if USING_OCR_DETECTOR:
                        pdf_analysis = analyze_pdf_content(file_path)
                        features['needs_ocr'] = pdf_analysis['has_images']
                        features['image_to_text_ratio'] = pdf_analysis['image_to_text_ratio']
                    else:
                        features['needs_ocr'] = needs_ocr_fallback(file_path)
                
                # For unknown or binary types, check if it's actually text
                if mime_type == 'application/octet-stream' or not mime_type.startswith('text/'):
                    # If we're using fallback MIME detection, try content sampling
                    if not USING_MAGIC:
                        features['is_text'] = sample_is_text(file_path)
                        if features['is_text']:
                            logger.info(f"File {file_path} appears to be text-based despite MIME type {mime_type}")
            
            # For file objects, we have more limited analysis
            elif hasattr(file_path_or_object, 'read'):
                # For file objects, we have limited options
                if mime_type == "application/pdf":
                    features['has_text_layer'] = has_text_layer(file_path_or_object)
            
            return features
        except Exception as e:
            # Log the error
            logger.error(f"Error extracting features: {str(e)}")
            # Re-raise the exception to maintain the error chain
            if isinstance(e, (FileNotFoundError, ValueError)):
                raise
            raise ValueError(f"Error extracting features: {str(e)}")
