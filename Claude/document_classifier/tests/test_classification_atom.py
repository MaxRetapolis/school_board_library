import unittest

# Import the atom to test
from Claude.document_classifier.atoms.classification_atom import classify_document


class TestClassificationAtom(unittest.TestCase):
    """Tests for the classification atom."""
    
    def test_classify_text_based_pdf(self):
        """Test classifying a text-based PDF."""
        # Setup
        features = {
            'mime_type': 'application/pdf',
            'has_text_layer': True
        }
        
        # Execute
        result = classify_document(features)
        
        # Assert
        self.assertEqual(result, 'Text-based PDF')
    
    def test_classify_image_based_pdf(self):
        """Test classifying an image-based PDF."""
        # Setup
        features = {
            'mime_type': 'application/pdf',
            'has_text_layer': False
        }
        
        # Execute
        result = classify_document(features)
        
        # Assert
        self.assertEqual(result, 'Image-based document')
    
    def test_classify_image_file(self):
        """Test classifying an image file."""
        # Setup
        features = {
            'mime_type': 'image/jpeg',
            'has_text_layer': None
        }
        
        # Execute
        result = classify_document(features)
        
        # Assert
        self.assertEqual(result, 'Image-based document')
    
    def test_classify_text_based_non_pdf(self):
        """Test classifying a text-based non-PDF document."""
        # Setup
        features = {
            'mime_type': 'text/plain',
            'has_text_layer': None
        }
        
        # Execute
        result = classify_document(features)
        
        # Assert
        self.assertEqual(result, 'Text-based non-PDF')
    
    def test_classify_unknown(self):
        """Test classifying an unknown document type."""
        # Setup
        features = {
            'mime_type': 'application/zip',
            'has_text_layer': None
        }
        
        # Execute
        result = classify_document(features)
        
        # Assert
        self.assertEqual(result, 'Unknown')
    
    def test_classify_missing_mime_type(self):
        """Test classifying with missing MIME type."""
        # Setup
        features = {
            'has_text_layer': True
        }
        
        # Execute & Assert
        with self.assertRaises(KeyError):
            classify_document(features)


if __name__ == '__main__':
    unittest.main()
