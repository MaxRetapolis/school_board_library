import unittest
import io
from unittest.mock import patch, MagicMock, mock_open

# Import the atom to test
from Claude.document_classifier.atoms.pdf_text_layer_detector import has_text_layer


class TestPdfTextLayerDetector(unittest.TestCase):
    """Tests for the PDF text layer detector atom."""
    
    @patch('PyPDF2.PdfReader')
    def test_has_text_layer_with_text(self, mock_pdf_reader):
        """Test checking for text layer in a PDF with text."""
        # Setup
        mock_page = MagicMock()
        mock_page.extract_text.return_value = 'Some text content'
        
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance
        
        test_path = '/path/to/test_with_text.pdf'
        
        # Mock os.path.exists to return True
        with patch('os.path.exists', return_value=True):
            # Execute
            result = has_text_layer(test_path)
            
            # Assert
            self.assertTrue(result)
            mock_page.extract_text.assert_called_once()
    
    @patch('PyPDF2.PdfReader')
    def test_has_text_layer_without_text(self, mock_pdf_reader):
        """Test checking for text layer in a PDF without text."""
        # Setup
        mock_page = MagicMock()
        mock_page.extract_text.return_value = ''  # Empty text
        
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance
        
        test_path = '/path/to/test_without_text.pdf'
        
        # Mock os.path.exists to return True
        with patch('os.path.exists', return_value=True):
            # Execute
            result = has_text_layer(test_path)
            
            # Assert
            self.assertFalse(result)
            mock_page.extract_text.assert_called_once()
    
    @patch('PyPDF2.PdfReader')
    def test_has_text_layer_empty_pdf(self, mock_pdf_reader):
        """Test checking for text layer in an empty PDF."""
        # Setup
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = []  # No pages
        mock_pdf_reader.return_value = mock_reader_instance
        
        test_path = '/path/to/empty.pdf'
        
        # Mock os.path.exists to return True
        with patch('os.path.exists', return_value=True):
            # Execute
            result = has_text_layer(test_path)
            
            # Assert
            self.assertFalse(result)
    
    def test_has_text_layer_corrupted_pdf(self):
        """Test checking for text layer in a corrupted PDF."""
        # Setup
        test_path = '/path/to/corrupted.pdf'
        
        # Mock os.path.exists to return True
        with patch('os.path.exists', return_value=True):
            # Mock PyPDF2.PdfReader to raise PdfReadError
            with patch('PyPDF2.PdfReader', side_effect=Exception('Error reading PDF')):
                # Execute & Assert
                with self.assertRaises(ValueError):
                    has_text_layer(test_path)


if __name__ == '__main__':
    unittest.main()
