from typing import Union, BinaryIO, TextIO, Dict, Any
import logging

# Import the required molecules
from src.document_classifier.molecules.feature_extractor import FeatureExtractor
from src.document_classifier.molecules.classifier_logic import ClassifierLogic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DocumentClassifier')


class DocumentClassifier:
    """
    The main document classifier class.
    
    This class combines the feature extractor and classifier logic molecules
    to classify documents based on their characteristics.
    """
    
    def __init__(self):
        """
        Initializes the DocumentClassifier with its component molecules.
        """
        self.feature_extractor = FeatureExtractor()
        self.classifier_logic = ClassifierLogic()
        logger.info("DocumentClassifier initialized")
    
    def classify_document(self, file_path_or_object: Union[str, BinaryIO, TextIO]) -> str:
        """
        Classifies a document based on its features.
        
        Args:
            file_path_or_object: Either a file path (str) or a file object.
            
        Returns:
            str: One of 'Text-based PDF', 'Text-based non-PDF', 'Image-based document', or 'Unknown'.
            
        Raises:
            FileNotFoundError: If the file path is invalid or file doesn't exist.
            ValueError: If there's an error processing the file.
        """
        try:
            logger.debug(f"Classifying document: {file_path_or_object}")
            
            # Step 1: Extract features
            features = self.feature_extractor.extract_features(file_path_or_object)
            logger.debug(f"Extracted features: {features}")
            
            # Step 2: Apply classification logic
            classification = self.classifier_logic.classify(features)
            logger.info(f"Document classified as: {classification}")
            
            return classification
        except Exception as e:
            logger.error(f"Error classifying document: {str(e)}")
            # Re-raise the exception to maintain the error chain
            if isinstance(e, (FileNotFoundError, ValueError, KeyError)):
                raise
            raise ValueError(f"Error classifying document: {str(e)}")