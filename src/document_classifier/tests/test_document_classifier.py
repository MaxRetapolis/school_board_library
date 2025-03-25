import unittest
from unittest.mock import patch, MagicMock

# Import the main class to test
from src.document_classifier.main.document_classifier import DocumentClassifier


class TestDocumentClassifier(unittest.TestCase):
    """Tests for the DocumentClassifier class."""
    
    def setUp(self):
        """Set up a DocumentClassifier instance for tests."""
        self.classifier = DocumentClassifier()
    
    @patch('src.document_classifier.molecules.feature_extractor.FeatureExtractor.extract_features')
    @patch('src.document_classifier.molecules.classifier_logic.ClassifierLogic.classify')
    def test_classify_document(self, mock_classify, mock_extract_features):
        """Test the full document classification process."""
        # Setup
        test_path = '/path/to/test.pdf'
        test_features = {
            'mime_type': 'application/pdf',
            'has_text_layer': True
        }
        expected_classification = 'Text-based PDF'
        
        mock_extract_features.return_value = test_features
        mock_classify.return_value = expected_classification
        
        # Execute
        result = self.classifier.classify_document(test_path)
        
        # Assert
        self.assertEqual(result, expected_classification)
        mock_extract_features.assert_called_once_with(test_path)
        mock_classify.assert_called_once_with(test_features)
    
    @patch('src.document_classifier.molecules.feature_extractor.FeatureExtractor.extract_features')
    def test_classify_document_feature_extraction_error(self, mock_extract_features):
        """Test error handling during feature extraction."""
        # Setup
        test_path = '/path/to/test.pdf'
        mock_extract_features.side_effect = ValueError("Error extracting features")
        
        # Execute & Assert
        with self.assertRaises(ValueError):
            self.classifier.classify_document(test_path)
    
    @patch('src.document_classifier.molecules.feature_extractor.FeatureExtractor.extract_features')
    @patch('src.document_classifier.molecules.classifier_logic.ClassifierLogic.classify')
    def test_classify_document_classification_error(self, mock_classify, mock_extract_features):
        """Test error handling during classification."""
        # Setup
        test_path = '/path/to/test.pdf'
        test_features = {
            'mime_type': 'application/pdf',
            'has_text_layer': True
        }
        
        mock_extract_features.return_value = test_features
        mock_classify.side_effect = KeyError("Missing required feature")
        
        # Execute & Assert
        with self.assertRaises(KeyError):
            self.classifier.classify_document(test_path)


if __name__ == '__main__':
    unittest.main()
