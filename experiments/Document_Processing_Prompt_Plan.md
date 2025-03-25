Below is a cleaned-up and properly formatted Markdown document based on the provided content. It is designed to be detailed enough for another coding LLM model to develop the code for the Document Classifier while avoiding unnecessary repetition. The document is structured logically with clear sections, headings, lists, and concise descriptions to guide implementation efficiently.

---

# Document Processing and Classification for School Board New Member Copilot

## Introduction

This document outlines the process for assessing, standardizing, and classifying incoming documents for the School Board New Member Copilot project. The goal is to convert documents into a uniform format and classify them into one of four categories—'Text-based PDF', 'Text-based non-PDF', 'Image-based document', or 'Unknown'—to guide subsequent processing.

## Document Processing Pipeline

### Format Assessment and Standardization

- **Description**: Assesses the format of each incoming document and converts it into a uniform, machine-readable format (e.g., PDF) as needed.
- **Input**: Raw documents from the `/inbound` folder.
- **Output**: Standardized documents in a consistent format.
- **Details**: Involves scanning physical documents, applying OCR to non-digital files, and converting various file types (e.g., DOCX, TXT) into a single target format.

### Document Classifier

- **Purpose**: Determines the type of each incoming document to guide further processing.
- **Functionality**: Classifies documents into four categories:
  - 'Text-based PDF': PDFs with extractable text.
  - 'Text-based non-PDF': Editable text files like DOCX or TXT.
  - 'Image-based document': Image files (e.g., JPG, PNG) or PDFs without text layers.
  - 'Unknown': Files that don’t match defined criteria.
- **Components**:
  - **Feature Extractor Molecule**: Extracts MIME type and, for PDFs, text layer status.
  - **Classifier Logic Molecule**: Applies classification rules using extracted features.

## Atoms

### MIME Type Detector Atom

- **Description**: Identifies the MIME type of a file using the `python-magic` library.
- **Input**: File path (str) or file object.
- **Output**: MIME type string (e.g., "application/pdf", "image/jpeg").

### PDF Text Layer Detector Atom

- **Description**: Checks if a PDF has extractable text using `PyPDF2`.
- **Input**: PDF file path (str) or file object.
- **Output**: `True` if text is present, `False` otherwise.

### Classification Atom

- **Description**: Classifies a document based on its features.
- **Input**: Dictionary with `'mime_type'` (str) and `'has_text_layer'` (bool or None).
- **Output**: Classification string ('Text-based PDF', 'Text-based non-PDF', 'Image-based document', or 'Unknown').

## Classification Rules

- **'Text-based PDF'**: `'mime_type'` is "application/pdf" and `'has_text_layer'` is `True`.
- **'Image-based document'**: `'mime_type'` is "application/pdf" and `'has_text_layer'` is `False`, or `'mime_type'` is in ["image/jpeg", "image/png", "image/tiff", "image/bmp"].
- **'Text-based non-PDF'**: `'mime_type'` is in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain", "application/rtf"].
- **'Unknown'**: Any case not matching the above rules.

## Coding Standards

### Code Structure

- **Folders**:
  - `atoms/`: Standalone functions (e.g., `mime_type_detector.py`).
  - `molecules/`: Classes combining atoms (e.g., `feature_extractor.py`).
  - `main/`: Application entry point (e.g., `document_classifier.py`).
  - `tests/`: Unit tests (e.g., `test_mime_type_detector.py`).
  - `configs/`: Configuration files (e.g., `classifier_config.yaml`).
- **Program Names**: Reflect functionality (e.g., `pdf_text_layer_detector.py`, `classifier_logic.py`).

### Best Practices

- **Configuration Section**: Start each program with a configuration dictionary or class (e.g., `CONFIG = {"input_path": "./documents/"}`).
- **Program Length**: Limit to 200 lines; split larger programs into smaller units.
- **Type Hints**: Use for all functions (e.g., `def detect_mime_type(file_path: str) -> str:`).
- **Docstrings**: Include for every function and class, detailing purpose, parameters, returns, and exceptions.
- **Error Handling**: Use try-except blocks for robust error management.
- **Logging**: Use the `logging` module instead of `print()` statements.
- **Testing**: Write unit tests for each component.

## Prompt Plan for LLM

This section provides a step-by-step guide for an LLM to create Python code for the `DocumentClassifier` and its components.

### Step 1: Create the MIME Type Detector Atom

- **Function**: `detect_mime_type`
- **Input**: File path (str) or file object.
- **Output**: MIME type string (e.g., "application/pdf").
- **Library**: `python-magic` (`import magic`).
- **Details**: Handle both file paths and file objects; include error handling for invalid inputs (e.g., raise `FileNotFoundError`).

### Step 2: Create the PDF Text Layer Detector Atom

- **Function**: `has_text_layer`
- **Input**: PDF file path (str) or file object.
- **Output**: `True` if text is extractable, `False` otherwise.
- **Library**: `PyPDF2` (`import PyPDF2`).
- **Details**: Check all pages with `PdfReader.extract_text()`; handle non-PDFs or corrupted files with exceptions.

### Step 3: Create the Classification Atom

- **Function**: `classify_document`
- **Input**: Dictionary with `'mime_type'` (str) and `'has_text_layer'` (bool or None).
- **Output**: Classification string.
- **Details**: Apply classification rules; handle `'has_text_layer'` as `None` for non-PDFs; raise `KeyError` for missing keys.

### Step 4: Create the Feature Extractor Molecule

- **Class**: `FeatureExtractor`
- **Method**: `extract_features`
- **Input**: File path (str) or file object.
- **Output**: Dictionary with `'mime_type'` and `'has_text_layer'` (bool or None).
- **Details**: Use `detect_mime_type` and, for PDFs, `has_text_layer`; set `'has_text_layer'` to `None` for non-PDFs.

### Step 5: Create the Classifier Logic Molecule

- **Class**: `ClassifierLogic`
- **Method**: `classify`
- **Input**: Features dictionary.
- **Output**: Classification string.
- **Details**: Call `classify_document` with the features; propagate any exceptions.

### Step 6: Create the Document Classifier

- **Class**: `DocumentClassifier`
- **Method**: `classify_document`
- **Input**: File path (str) or file object.
- **Output**: Classification string.
- **Details**: Initialize `FeatureExtractor` and `ClassifierLogic` in `__init__`; chain their methods to classify the document.

### Additional Instructions

- **Error Handling**: Use try-except blocks; raise specific exceptions (e.g., `ValueError` for corrupted files) with clear messages.
- **Type Hints**: Apply to all functions and methods (e.g., `from typing import Union, Dict` for flexible inputs).
- **Docstrings**: Document each component with purpose, parameters, returns, and exceptions.
- **Testing**: Include test cases for:
  - Text-based PDF (e.g., PDF with text).
  - Text-based non-PDF (e.g., TXT file).
  - Image-based document (e.g., JPG or textless PDF).
  - Unknown type (e.g., ZIP file).
  Example:
  ```python
  classifier = DocumentClassifier()
  print(classifier.classify_document("sample.pdf"))  # Expected: 'Text-based PDF'
  print(classifier.classify_document("image.jpg"))   # Expected: 'Image-based document'
  ```

---

This Markdown document provides a clear, concise, and structured guide for a coding LLM to implement the Document Classifier. It includes all necessary details—components, rules, coding standards, and a step-by-step plan—while minimizing redundancy to optimize token usage. The use of Markdown formatting enhances readability and ensures the LLM can easily parse and follow the instructions to develop the code.