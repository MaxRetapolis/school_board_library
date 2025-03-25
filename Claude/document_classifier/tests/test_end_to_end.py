import unittest
import os
import tempfile
import shutil
from pathlib import Path

# Import the document classifier
from Claude.document_classifier.main.document_classifier import DocumentClassifier


class TestEndToEnd(unittest.TestCase):
    """End-to-end tests for the document classifier."""
    
    def setUp(self):
        """Set up test files."""
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        
        # Create test files
        self.create_test_files()
        
        # Initialize the classifier
        self.classifier = DocumentClassifier()
    
    def tearDown(self):
        """Clean up after the test."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)
    
    def create_test_files(self):
        """Create test files for different formats."""
        # PDF file
        self.pdf_path = os.path.join(self.test_dir, 'test.pdf')
        with open(self.pdf_path, 'wb') as f:
            f.write(b'%PDF-1.5\nTest PDF content')
        
        # VTT file
        self.vtt_path = os.path.join(self.test_dir, 'test.vtt')
        with open(self.vtt_path, 'wb') as f:
            f.write(b'WEBVTT\n\n00:00:01.000 --> 00:00:05.000\nSubtitle text')
        
        # Text file
        self.txt_path = os.path.join(self.test_dir, 'test.txt')
        with open(self.txt_path, 'w') as f:
            f.write('This is a plain text file.')
        
        # Create a binary file
        self.bin_path = os.path.join(self.test_dir, 'test.bin')
        with open(self.bin_path, 'wb') as f:
            f.write(bytes([i % 256 for i in range(1000)]))
        
        # Create a large PDF file (for OCR detection)
        self.large_pdf_path = os.path.join(self.test_dir, 'large.pdf')
        with open(self.large_pdf_path, 'wb') as f:
            f.write(b'%PDF-1.5\n' + b'X' * 1000000)  # 1MB of content
    
    def test_classify_pdf(self):
        """Test classifying a PDF file."""
        # Execute
        result = self.classifier.classify_document(self.pdf_path)
        
        # Assert
        self.assertEqual(result, 'Text-based PDF')
    
    def test_classify_vtt(self):
        """Test classifying a VTT file."""
        # Execute
        result = self.classifier.classify_document(self.vtt_path)
        
        # Assert
        self.assertEqual(result, 'Plain-Text-Special-Format')
    
    def test_classify_txt(self):
        """Test classifying a text file."""
        # Execute
        result = self.classifier.classify_document(self.txt_path)
        
        # Assert
        self.assertEqual(result, 'Text-based non-PDF')
    
    def test_classify_binary(self):
        """Test classifying a binary file."""
        # Execute
        result = self.classifier.classify_document(self.bin_path)
        
        # Assert
        self.assertEqual(result, 'Unknown')
    
    def test_classify_large_pdf(self):
        """Test classifying a large PDF file that might need OCR."""
        # Execute
        result = self.classifier.classify_document(self.large_pdf_path)
        
        # Due to fallback OCR detection being based on file size,
        # large files should be classified as PDF-Text-With-Images
        self.assertEqual(result, 'PDF-Text-With-Images')


if __name__ == '__main__':
    unittest.main()