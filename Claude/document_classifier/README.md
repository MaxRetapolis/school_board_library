# Document Classifier for School Board Library

This module provides a document classification system that categorizes documents based on their characteristics. It's designed to be part of the School Board New Member Copilot project, helping to organize and process various document types more efficiently.

## Classification Categories

Documents are classified into four categories:

- **Text-based PDF**: PDFs with extractable text
- **Text-based non-PDF**: Editable text files like DOCX or TXT
- **Image-based document**: Image files (JPG, PNG) or PDFs without extractable text
- **Unknown**: Files that don't match defined criteria

## Architecture

The system follows an atomic modular design with three layers:

1. **Atoms**: Basic, single-responsibility functions
   - `mime_type_detector.py`: Identifies the MIME type of a file
   - `pdf_text_layer_detector.py`: Checks if a PDF has extractable text
   - `classification_atom.py`: Applies classification rules to features

2. **Molecules**: Classes that combine atoms into more complex functionality
   - `feature_extractor.py`: Extracts relevant features from documents
   - `classifier_logic.py`: Applies classification logic to extracted features

3. **Main**: High-level components for end-users
   - `document_classifier.py`: Main interface for classifying documents
   - `example.py`: Example usage of the document classifier

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```python
from src.document_classifier.main.document_classifier import DocumentClassifier

# Initialize the classifier
classifier = DocumentClassifier()

# Classify a document
classification = classifier.classify_document('/path/to/document.pdf')
print(f"Document classified as: {classification}")
```

## Running Tests

To run the unit tests:

```bash
# From the project root
pytest src/document_classifier/tests/

# Or individually
pytest src/document_classifier/tests/test_document_classifier.py
```

## Configuration

The system's behavior can be customized through the configuration file:
- `configs/classifier_config.py`: Contains settings for MIME types, paths, and classification rules