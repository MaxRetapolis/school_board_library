# Document Classifier Execution Notes

## Dependencies

The document classifier requires the following Python packages to be installed for optimal performance:

1. **python-magic**: Used for MIME type detection
   - Install with `pip install python-magic`
   - On Windows, also install `python-magic-bin`: `pip install python-magic-bin`
   - On Linux, can be installed with `apt-get install python3-magic`

2. **PyPDF2**: Used for PDF text extraction
   - Install with `pip install PyPDF2`
   - On Linux, can be installed with `apt-get install python3-pypdf2`

## Enhanced Features

The document classifier now includes several enhanced features:

1. **Expanded Classification Categories**
   - `PDF-Text-With-Images`: PDFs that contain both text and images that may need OCR
   - `Plain-Text-Special-Format`: Special text formats like WebVTT (.vtt) subtitle files

2. **OCR Need Detection**
   - The system now detects PDFs that likely need OCR processing
   - Large PDFs are flagged as potentially containing images requiring OCR
   - When the full PDF analysis libraries are available, this will be more accurate

3. **Text Content Sampling**
   - For unknown file types, the system samples file content to check if it's text-based
   - This allows detection of text files with non-standard extensions
   - Uses a heuristic that checks for a high percentage of printable ASCII characters

## Fallback Implementations

The document classifier includes fallback implementations to handle missing dependencies:

1. **Fallback MIME Type Detection**
   - If `python-magic` is not available, the system uses Python's built-in `mimetypes` module
   - This approach is less accurate but allows the classifier to function
   - File types are determined based on file extensions
   - Now includes detection for .vtt and .srt subtitle files

2. **Fallback PDF Text Layer Detection**
   - If `PyPDF2` is not available, a simple extension-based detection is used
   - All files with `.pdf` extension are assumed to be text-based PDFs
   - This is less accurate but allows for basic classification
   
3. **Fallback OCR Need Detection**
   - Uses file size heuristics to identify PDFs that might need OCR
   - Large PDFs (over 500KB) are assumed to potentially contain images

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
  - `Classified/PDF-Mixed/`: PDFs containing both text and images that may need OCR
  - `Classified/Text-Special/`: Special text formats like WebVTT (.vtt) subtitle files
  - `Classified/PDF-Unknown/`: Documents that couldn't be classified
  - `In_Processing/`: Documents currently being processed

## Using the Classifier

The document classifier can be used in two ways:

1. **Using the API**: Import and use the `DocumentClassifier` class directly in your code
   ```python
   from Claude.document_classifier.main.document_classifier import DocumentClassifier
   
   classifier = DocumentClassifier()
   classification = classifier.classify_document('/path/to/document.pdf')
   print(f"Document classified as: {classification}")
   ```

2. **Using the Command-Line Script**: Run the classification script to process files from the inbound directory
   ```bash
   python Claude/document_classifier/main/classify_inbound.py
   ```
   This script:
   - Reads files from `Claude/inbound`
   - Classifies each file
   - Moves files to the appropriate subdirectory under `Claude/outbound/Classified/`
   - Provides a summary of classification results

You can modify the script to process all files or a specific number by changing the `max_files` parameter.

## Notes for Production Deployment

1. The system requires a Python environment with the necessary dependencies installed, but can now operate with fallback implementations if dependencies are missing.
2. Make sure the directory structure exists and has appropriate permissions.
3. For large document sets, the `classify_inbound.py` script provides batch processing capabilities.
4. Classification is more accurate with the required dependencies, but will still function with basic accuracy using fallbacks.
5. Log output provides details about which implementation (optimal or fallback) is being used.
6. In production, consider expanding the fallback implementations for better accuracy without dependencies.