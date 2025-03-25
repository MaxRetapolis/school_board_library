import unittest
import os
import io
import tempfile
from unittest.mock import patch, MagicMock

# Import the fallback implementations
from Claude.document_classifier.atoms.fallback_mime_detector import detect_mime_type_fallback, sample_is_text
from Claude.document_classifier.atoms.fallback_pdf_detector import has_text_layer_fallback
from Claude.document_classifier.atoms.pdf_ocr_detector import needs_ocr_fallback


class TestFallbackImplementations(unittest.TestCase):
    """Tests for the fallback implementations."""
    
    def test_detect_mime_type_fallback_pdf(self):
        """Test detecting a PDF file with the fallback detector."""
        # Create a temporary file with a .pdf extension
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp:
            temp.write(b'PDF content')
            temp_path = temp.name
        
        try:
            # Execute
            result = detect_mime_type_fallback(temp_path)
            
            # Assert
            self.assertEqual(result, 'application/pdf')
        finally:
            # Clean up
            os.unlink(temp_path)
    
    def test_detect_mime_type_fallback_vtt(self):
        """Test detecting a VTT file with the fallback detector."""
        # Create a temporary file with a .vtt extension
        with tempfile.NamedTemporaryFile(suffix='.vtt', delete=False) as temp:
            temp.write(b'WEBVTT\n\n00:00:01.000 --> 00:00:05.000\nSubtitle text')
            temp_path = temp.name
        
        try:
            # Execute
            result = detect_mime_type_fallback(temp_path)
            
            # Assert
            self.assertEqual(result, 'text/vtt')
        finally:
            # Clean up
            os.unlink(temp_path)
    
    def test_has_text_layer_fallback(self):
        """Test the fallback PDF text layer detection."""
        # Create a temporary file with a .pdf extension
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp:
            temp.write(b'PDF content')
            temp_path = temp.name
        
        try:
            # Execute
            result = has_text_layer_fallback(temp_path)
            
            # Assert
            self.assertTrue(result)  # It should return True for any PDF
        finally:
            # Clean up
            os.unlink(temp_path)
    
    def test_has_text_layer_fallback_non_pdf(self):
        """Test the fallback PDF text layer detection with a non-PDF file."""
        # Create a temporary file with a .txt extension
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp:
            temp.write(b'Plain text content')
            temp_path = temp.name
        
        try:
            # Execute
            result = has_text_layer_fallback(temp_path)
            
            # Assert
            self.assertFalse(result)  # It should return False for non-PDFs
        finally:
            # Clean up
            os.unlink(temp_path)
    
    def test_needs_ocr_fallback_large_file(self):
        """Test OCR need detection for a large file."""
        # Mock a large file
        with patch('os.path.getsize', return_value=1024 * 1024):  # 1MB
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp:
                temp_path = temp.name
            
            try:
                # Execute
                result = needs_ocr_fallback(temp_path)
                
                # Assert
                self.assertTrue(result)  # Large files should need OCR
            finally:
                # Clean up
                os.unlink(temp_path)
    
    def test_needs_ocr_fallback_small_file(self):
        """Test OCR need detection for a small file."""
        # Create a small file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp:
            temp.write(b'Small PDF content')
            temp_path = temp.name
        
        try:
            # Execute
            result = needs_ocr_fallback(temp_path)
            
            # Assert
            self.assertFalse(result)  # Small files should not need OCR
        finally:
            # Clean up
            os.unlink(temp_path)
    
    def test_sample_is_text_text_file(self):
        """Test text content sampling with a text file."""
        # Create a text file
        with tempfile.NamedTemporaryFile(suffix='.unknown', delete=False) as temp:
            temp.write(b'This is a text file with ASCII content.')
            temp_path = temp.name
        
        try:
            # Execute
            result = sample_is_text(temp_path)
            
            # Assert
            self.assertTrue(result)  # Should detect as text
        finally:
            # Clean up
            os.unlink(temp_path)
    
    def test_sample_is_text_binary_file(self):
        """Test text content sampling with a binary file."""
        # Create a binary file
        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as temp:
            # Write some binary content
            binary_data = bytes([i for i in range(256)])
            temp.write(binary_data)
            temp_path = temp.name
        
        try:
            # Execute
            result = sample_is_text(temp_path)
            
            # Assert
            self.assertFalse(result)  # Should detect as binary
        finally:
            # Clean up
            os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()