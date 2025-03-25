from typing import Dict, Union, BinaryIO, TextIO, Any, Optional
import os

# Import the required atoms
from Claude.document_classifier.atoms.mime_type_detector import detect_mime_type
from Claude.document_classifier.atoms.pdf_text_layer_detector import has_text_layer


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
            # Get the MIME type
            mime_type = detect_mime_type(file_path_or_object)
            
            # Initialize features dictionary
            features = {
                'mime_type': mime_type,
                'has_text_layer': None  # Default value
            }
            
            # Check for text layer if it's a PDF
            if mime_type == "application/pdf":
                features['has_text_layer'] = has_text_layer(file_path_or_object)
            
            return features
        except Exception as e:
            # Re-raise the exception to maintain the error chain
            if isinstance(e, (FileNotFoundError, ValueError)):
                raise
            raise ValueError(f"Error extracting features: {str(e)}")
