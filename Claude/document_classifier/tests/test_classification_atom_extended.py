import unittest

# Import the atom to test
from Claude.document_classifier.atoms.classification_atom import classify_document


class TestClassificationAtomExtended(unittest.TestCase):
    """Extended tests for the classification atom with new categories."""
    
    def test_classify_pdf_with_images(self):
        """Test classifying a PDF with text and images."""
        # Setup
        features = {
            'mime_type': 'application/pdf',
            'has_text_layer': True,
            'needs_ocr': True
        }
        
        # Execute
        result = classify_document(features)
        
        # Assert
        self.assertEqual(result, 'PDF-Text-With-Images')
    
    def test_classify_vtt_file(self):
        """Test classifying a VTT file."""
        # Setup
        features = {
            'mime_type': 'text/vtt',
            'has_text_layer': None
        }
        
        # Execute
        result = classify_document(features)
        
        # Assert
        self.assertEqual(result, 'Plain-Text-Special-Format')
    
    def test_classify_srt_file(self):
        """Test classifying an SRT file."""
        # Setup
        features = {
            'mime_type': 'text/srt',
            'has_text_layer': None
        }
        
        # Execute
        result = classify_document(features)
        
        # Assert
        self.assertEqual(result, 'Plain-Text-Special-Format')
    
    def test_classify_binary_with_text_content(self):
        """Test classifying a binary file that actually contains text."""
        # Setup
        features = {
            'mime_type': 'application/octet-stream',
            'has_text_layer': None,
            'is_text': True,
            'using_fallback_mime': True
        }
        
        # Execute
        result = classify_document(features)
        
        # Assert
        self.assertEqual(result, 'Text-based non-PDF')
    
    def test_classify_with_fallbacks(self):
        """Test classifying with fallback implementations."""
        # Setup
        features = {
            'mime_type': 'application/pdf',
            'has_text_layer': True,
            'needs_ocr': True,
            'using_fallback_mime': True,
            'using_fallback_pdf': True
        }
        
        # Execute
        result = classify_document(features)
        
        # Assert
        self.assertEqual(result, 'PDF-Text-With-Images')


if __name__ == '__main__':
    unittest.main()