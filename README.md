# School Board Document Processing Pipeline

## Overview

My belief is that 60 % of copilot use cases can be solved with "shallow" knowledge (1-pass summarization and out of the box tools such as LlamaIndex), while 40 % will require "deep" knowledge with drastically higher requirements for quality of answers and incorporation of expert feedback. By focusing on the "deep" knowledge I bet on companies behind SOTA models commoditizing simpler use cases and solving them at a very low cost. I also bet on the fact that "deep" knowledge will be much harder to commoditize and will require a lot of human input to get right. Finally, it is just fun working on harder problems.

I am rewriting the pipeline based on the learnings from three experiments ran in Late Nov/ early Dec (see the experiments folder).
This readme file will describe in detail the components as I build them.

## Design Principles ##
1. Modularity, linearity, databus/ document storage
2. Lazy/ greedy approach - LLM first, proper code solutions second
3. Standing on the shoulders of giants - modify schema.org ontologies, use SOTA models, 3rd party libraries
4. ELT - Extract, Load, Transform for each building block: documents, metadata, ontology
5. Multi-pass knowledge building - derive entities and relationships from documents, then re-summarize documents with ontology, then index documents, ontlology, and metadata together
6. Multi-pass querying - map query to ontology, query separately ontology and text, then combine results

## Pipeline Components

1. Document Storage ELT Process - "shallow knowledge"
2. Ontology Extraction ELT Process
3. Document re-summarization with Ontology - "deep knowledge"
4. Building links between documents, ontology, and metadata
5. Building a search engine on top of the indexed data - supporting multi-modal queries (text, ontology, metadata)


# Step 1 - Document Storage ELT Process

## Goal

Create a document storage system where diverse document types are represented uniformly as plain text, images with OCR text, and linked metadata, ready for further processing (such as ontology extraction).

## ELT Steps for Source Documents

### 1. Extract

#### Document Intake

- **Create an inbound directory** to receive all source documents.
- **Develop an `extractor.py` script** that monitors this directory.
  - This script will identify the file type (e.g., `.txt`, `.pdf`, `.pptx`, `.jpg`, `.png`, `.csv`, `.xlsx`) of each new document.

#### Initial Metadata

- **Extract basic file metadata**:
  - Filename
  - File type
  - Creation date
  - Modification date
  - File size
- **Store metadata** in a temporary `metadata_temp.json` file associated with each document.

### 2. Load

#### Raw Document Storage

- **Create a `raw_documents` directory**.
- **Move the original files** from `inbound` to `raw_documents`, preserving the original file structure or creating a new structure based on the source or document type. This serves as an archive of the original documents.

#### Staging Area

- **Create a `staging` directory**. This is where temporary files will be placed during the transformation process.

### 3. Transform

#### Text Documents (`.txt`, `.docx`, `.pdf` with text layer)

- **Extract Text Content**:
  - Use libraries like `textract` or `PyMuPDF`.
- **Normalize the Text**:
  - Convert to lowercase
  - Remove extra whitespace
  - Handle special characters (based on specific needs)
- **Save the Normalized Text**:
  - Save as a `.txt` file in the `staging` directory, named after the original file (e.g., `document123.txt`).
- **Update `metadata_temp.json`**:
  - Add:
    ```json
    {
      "text_path": "path/to/staging/document123.txt",
      "status": "text_extracted"
    }
    ```

#### Presentations (`.pptx`)

- **Extract Text from Slides**:
  - Use a library like `python-pptx`.
  - Concatenate text from all slides, adding separators to indicate slide breaks.
- **Normalize the Text** (as above).
- **Save the Extracted Text**:
  - Save as a `.txt` file in `staging`.
- **Update `metadata_temp.json`** similarly to text documents.

#### Tables (`.csv`, `.xlsx`)

- **Read Tables**:
  - Use libraries like `pandas` or `openpyxl`.
- **Convert to Plain Text Representation**:
  - Consider different formats:
    - CSV-like: comma-separated values
    - Markdown tables: for better readability
    - Plain text with fixed-width columns
- **Save the Tables**:
  - Save each table as a separate `.txt` file in `staging`.
- **Update `metadata_temp.json`**:
  - Include an array of table paths in `staging`, along with metadata about each table (e.g., number of rows, columns).

#### Images (`.jpg`, `.png`, `.pdf` with scanned images)

- **Perform OCR**:
  - Use Tesseract OCR (via the `pytesseract` wrapper) to extract text.
- **Save OCR Text**:
  - Save the extracted OCR text as a `.txt` file in `staging`.
- **Save Image Copy**:
  - Save a copy of the image in a `staging/images` subdirectory.
- **Update `metadata_temp.json`**:
  - Add:
    ```json
    {
      "image_path": "path/to/staging/images/image123.jpg",
      "ocr_text_path": "path/to/staging/image123.txt",
      "status": "ocr_completed"
    }
    ```

#### Document Metadata Refinement

- **Refine Initial Metadata in `metadata_temp.json`**:
  - Add:
    - `document_id`: a unique identifier
    - `document_type`: based on refined categorization (e.g., "meeting minutes", "agenda", "report"). This may require initial rules or heuristics based on filename or content.
    - `is_ocr_required`: indicates which documents needed OCR
- **Save Refined Metadata**:
  - Save as `metadata.json` in the `staging` directory.

### Normalized Document Storage (Output)

After the Transform step, your `staging` directory will contain:

- **`.txt` Files**:
  - Normalized plain text representation of text documents, presentations, tables, and image OCR.
- **`images` Subdirectory**:
  - Copies of images that underwent OCR.
- **`metadata.json`**:
  - Structured metadata for each document, linking to the text and image files in the `staging` directory.

## Next Steps (Looking Ahead)

### Chunking

- **Decide on a Chunking Strategy**:
  - Fixed-size, semantic, etc.
- **Create a `chunker.py` Script**:
  - Split the normalized text into chunks.

### Co-indexing

- **Create an Index**:
  - Use a database or search engine.
  - Link document metadata, text chunks, and image OCR data.
  - Enable efficient retrieval.

---

