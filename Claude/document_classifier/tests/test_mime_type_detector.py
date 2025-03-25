import unittest
import os
import io
from unittest.mock import patch, MagicMock

# Import the atom to test
from src.document_classifier.atoms.mime_type_detector import detect_mime_type


class TestMimeTypeDetector(unittest.TestCase):
    """Tests for the MIME type detector atom."""
    
    @patch('magic.from_file')
    def test_detect_mime_type_from_file_path(self, mock_from_file):
        """Test detecting MIME type from a file path."""
        # Setup
        mock_from_file.return_value = 'application/pdf'
        test_path = '/path/to/test.pdf'
        
        # Mock os.path.exists to return True
        with patch('os.path.exists', return_value=True):
            # Execute
            result = detect_mime_type(test_path)
            
            # Assert
            self.assertEqual(result, 'application/pdf')
            mock_from_file.assert_called_once_with(test_path, mime=True)
    
    @patch('magic.from_buffer')
    def test_detect_mime_type_from_file_object(self, mock_from_buffer):
        """Test detecting MIME type from a file object."""
        # Setup
        mock_from_buffer.return_value = 'text/plain'
        test_file = io.BytesIO(b'Test content')
        
        # Execute
        result = detect_mime_type(test_file)
        
        # Assert
        self.assertEqual(result, 'text/plain')
        mock_from_buffer.assert_called_once()
    
    def test_detect_mime_type_file_not_found(self):
        """Test detecting MIME type with a non-existent file path."""
        # Setup
        test_path = '/path/to/nonexistent.pdf'
        
        # Mock os.path.exists to return False
        with patch('os.path.exists', return_value=False):
            # Execute & Assert
            with self.assertRaises(FileNotFoundError):
                detect_mime_type(test_path)
    
    def test_detect_mime_type_invalid_input(self):
        """Test detecting MIME type with an invalid input type."""
        # Execute & Assert
        with self.assertRaises(ValueError):
            detect_mime_type(123)  # Integer is not a valid input


if __name__ == '__main__':
    unittest.main()
