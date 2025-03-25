from typing import Dict, Any

# Import the required atom
from Claude.document_classifier.atoms.classification_atom import classify_document


class ClassifierLogic:
    """
    Class for applying classification logic to extracted document features.
    
    This molecule uses the classification atom to determine the document type
    based on its features.
    """
    
    def classify(self, features: Dict[str, Any]) -> str:
        """
        Classifies a document based on its extracted features.
        
        Args:
            features: Dictionary with 'mime_type' (str) and 'has_text_layer' (bool or None).
            
        Returns:
            str: One of 'Text-based PDF', 'Text-based non-PDF', 'Image-based document', or 'Unknown'.
            
        Raises:
            KeyError: If the features dictionary is missing required keys.
        """
        try:
            return classify_document(features)
        except Exception as e:
            # Re-raise the exception to maintain the error chain
            if isinstance(e, KeyError):
                raise
            raise ValueError(f"Error in classification logic: {str(e)}")
