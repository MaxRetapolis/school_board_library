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
    USING_MAGIC = False

try:
    from Claude.document_classifier.atoms.pdf_text_layer_detector import has_text_layer
    USING_PYPDF2 = True
except ImportError:
    logger.warning("PyPDF2 not available, using fallback PDF detector")
    from Claude.document_classifier.atoms.fallback_pdf_detector import has_text_layer_fallback as has_text_layer
    USING_PYPDF2 = False


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
            Dict[str, Any]: Dictionary with 'mime_type' (str) and possibly 'has_text_layer' (bool).
            
        Raises:
            FileNotFoundError: If the file path is invalid or file doesn't exist.
            ValueError: If there's an error processing the file.
        """
        try:
            # Log which implementation we're using
            logger.debug(f"Using python-magic: {USING_MAGIC}, Using PyPDF2: {USING_PYPDF2}")
            
            # Get the MIME type
            mime_type = detect_mime_type(file_path_or_object)
            logger.debug(f"Detected MIME type: {mime_type}")
            
            # Initialize features dictionary
            features = {
                'mime_type': mime_type,
                'has_text_layer': None,  # Default value
                'using_fallback_mime': not USING_MAGIC,
                'using_fallback_pdf': not USING_PYPDF2
            }
            
            # Check for text layer if it's a PDF
            if mime_type == "application/pdf":
                features['has_text_layer'] = has_text_layer(file_path_or_object)
                logger.debug(f"PDF text layer detection result: {features['has_text_layer']}")
                if not USING_PYPDF2:
                    logger.warning("Using fallback PDF detector - assuming PDFs have text based on extension only")
            
            return features
        except Exception as e:
            # Log the error
            logger.error(f"Error extracting features: {str(e)}")
            # Re-raise the exception to maintain the error chain
            if isinstance(e, (FileNotFoundError, ValueError)):
                raise
            raise ValueError(f"Error extracting features: {str(e)}")
