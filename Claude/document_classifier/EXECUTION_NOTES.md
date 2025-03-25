# Document Classifier Execution Notes

## Dependencies

The document classifier requires the following Python packages to be installed:

1. **python-magic**: Used for MIME type detection
   - Install with `pip install python-magic`
   - On Windows, also install `python-magic-bin`: `pip install python-magic-bin`

2. **PyPDF2**: Used for PDF text extraction
   - Install with `pip install PyPDF2`

## Common Exceptions During Execution

When running the document classifier, you may encounter these common exceptions:

### Import Errors

```
ImportError: No module named 'magic'
```
**Solution**: Install the python-magic package with `pip install python-magic`. On Windows, also install `python-magic-bin`.

```
ImportError: No module named 'PyPDF2'
```
**Solution**: Install the PyPDF2 package with `pip install PyPDF2`.

### File Processing Errors

```
FileNotFoundError: File not found: [file_path]
```
**Solution**: Ensure the file path is correct and the file exists.

```
ValueError: Invalid or corrupted PDF file
```
**Solution**: The PDF file is corrupted or not a valid PDF. Try with a different PDF file.

```
ValueError: Error extracting features: [error message]
```
**Solution**: This is a general error during feature extraction. Check the specific error message for more details.

## Testing Environment

We've created a test runner script (`test_runner.py`) in the `main` directory that helps identify missing dependencies and documents exceptions. You can run it with:

```bash
python Claude/document_classifier/main/test_runner.py
```

This script will:
1. Check for required dependencies
2. Verify that the inbound and outbound directories exist
3. Attempt to import and initialize the DocumentClassifier
4. Try to classify a sample document

The script logs detailed information about each step, making it easier to identify issues.

## Folder Structure

The document classifier uses the following folder structure:

- `Claude/inbound/`: Contains input documents to be classified
- `Claude/outbound/`: Contains processed documents, organized by type:
  - `Classified/PDF-Text/`: Text-based PDF files
  - `Classified/Text-Only/`: Text-based non-PDF files
  - `Classified/PDF-Images/`: Image-based documents
  - `Classified/PDF-Unknown/`: Documents that couldn't be classified
  - `In_Processing/`: Documents currently being processed

## Notes for Production Deployment

1. The system requires a Python environment with the necessary dependencies installed.
2. Make sure the directory structure exists and has appropriate permissions.
3. For large document sets, consider adding batch processing capabilities.
4. The classification is based on document features, not content analysis, so accuracy depends on the structure of the documents.