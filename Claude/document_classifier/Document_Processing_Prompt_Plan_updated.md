# Document Processing and Classification for School Board Library Copilot - Updated Plan

## Introduction

This document outlines the process for assessing, standardizing, and classifying incoming documents for the School Board Library Copilot project. The system classifies documents into specific categories to guide subsequent processing, with particular attention to identifying documents that require OCR.

## Document Processing Pipeline

### Format Assessment and Classification

- **Description**: Analyzes incoming documents to determine their type, content characteristics, and processing requirements.
- **Input**: Raw documents from the `/data/raw_documents` folder.
- **Output**: Classified documents organized in `/data/documents/Classified/<category>` directories.
- **Categories**:
  - **PDF-Text**: PDFs with extractable text content (text layers).
  - **PDF-Images**: PDFs that primarily contain images with minimal text.
  - **PDF-Text-Images**: PDFs with both text and significant image content.
  - **PDF-Unknown**: PDFs whose content type cannot be clearly determined.
  - **Text-Only**: Pure text files, including special formats like VTT subtitle files.

### Implementation Enhancements

The implemented system includes several enhancements to the original plan:

- **Content Sampling**: Examines document content to make classification decisions beyond just MIME type.
- **OCR Need Detection**: Uses file characteristics like size and content density to determine if a PDF likely needs OCR.
- **VTT Files Support**: Added special handling for subtitle/transcript files (VTT, SRT).
- **Graceful Degradation**: Fallback methods when optional dependencies (python-magic, PyPDF2) are not available.
- **Size-Based Heuristics**: Uses file size thresholds to estimate document complexity.

## Implementation Structure

### Document Classifier System

- **Configuration**: Directory paths, classification rules, and file type mappings.
- **Logging Setup**: Structured logging for operations and errors.
- **File Handler**: Manages file operations between directories.
- **Document Classifier**: Core logic for determining document types.
- **Pipeline Coordinator**: Orchestrates the overall classification process.
- **Index Manager**: Tracks processed documents and prevents duplicates.

### Code Organization

- **src/2 - Document Classifier/**: Main implementation folder
  - `config.py`: Configuration settings
  - `document_classifier.py`: Core classification logic
  - `file_handler.py`: File movement and handling
  - `index_manager.py`: Document tracking
  - `logging_setup.py`: Logging configuration
  - `pipeline_coordinator.py`: Process orchestration
  - `test_pipeline.py` and `test_pipeline_extended.py`: Testing modules

## Classification Logic

### Enhanced Rules

- **PDF-Text**: 
  - PDFs with text layers (extractable text)
  - Small PDF files (<100KB) with high text density
  
- **PDF-Images**: 
  - PDFs without text layers
  - Large PDF files (>1MB) with low text-to-image ratio
  
- **PDF-Text-Images**: 
  - PDFs with text layers and significant image content
  - Medium-sized PDFs (100KB-1MB)
  
- **PDF-Unknown**: 
  - PDFs that don't match the above criteria
  - PDFs with inconsistent content indicators
  
- **Text-Only**: 
  - Plain text files (TXT)
  - Subtitle files (VTT, SRT)
  - Other text-based formats (CSV, MD)

### Implementation Details

- **Text Layer Detection**: Examines PDF content to determine if text can be extracted.
- **MIME Type Detection**: Uses python-magic or fallback extension-based detection.
- **OCR Need Assessment**: Uses file size, text density, and other heuristics.
- **VTT/SRT Classification**: Special handling for transcript files.
- **Content Sampling**: Examines file content to make deterministic classifications.

## Operational Flow

1. **Document Arrival**: Documents are placed in `/data/raw_documents`.
2. **Initial Processing**: System identifies document type by extension and inspects content.
3. **Feature Extraction**: System extracts characteristics (MIME type, text presence, size metrics).
4. **Classification**: Documents are categorized using defined rules.
5. **Organization**: Classified documents are moved to appropriate subdirectories.
6. **Indexing**: Document details are recorded in the index for tracking and duplication prevention.

## System Robustness

- **Dependency Fallbacks**: System can operate without optional libraries.
- **Error Handling**: Comprehensive error handling for file access, processing, and classification.
- **Logging**: Detailed logging at all stages for troubleshooting.
- **Duplicate Detection**: Prevention of duplicate document processing.

## Performance and Scalability

The implemented system successfully processed 52 documents, classifying them as follows:
- PDF-Text: 9 files
- PDF-Images: 14 files
- PDF-Text-Images: 31 files
- PDF-Unknown: 8 files
- Text-Only: 8 files

The system is ready for integration with OCR processing in the next phase of development.

## Future Enhancements

- **Enhanced OCR Detection**: More sophisticated algorithms to determine OCR need.
- **Metadata Extraction**: Pulling author, date, and other metadata from documents.
- **Content-Based Classification**: Using NLP to categorize documents by topic.
- **Processing Queue**: Adding a queue system for handling large document volumes.
- **OCR Integration**: Direct integration with OCR processing systems.