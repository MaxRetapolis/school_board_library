# School Board Library Copilot

## Overview

My belief is that 60 % of copilot use cases can be solved with "shallow" knowledge (1-pass summarization and out of the box tools such as LlamaIndex), while 40 % will require "deep" knowledge with drastically higher requirements for quality of answers and incorporation of expert feedback. By focusing on the "deep" knowledge I bet on companies behind SOTA models commoditizing simpler use cases and solving them at a very low cost. I also bet on the fact that "deep" knowledge will be much harder to commoditize and will require a lot of human input to get right. Finally, it is just fun working on harder problems.

I am rewriting the pipeline based on the learnings from three experiments ran in Late Nov/ early Dec (see the experiments folder).
This readme file will describe in detail the components as I build them.

## Design Principles ##
1. Modularity, linearity, databus/ document storage
2. Observability - every step should create events, metrics, log entries
3. Lazy/ greedy approach - LLM first, proper code solutions second
4. Standing on the shoulders of giants - modify schema.org ontologies, use SOTA models, 3rd party libraries
5. ELT - Extract, Load, Transform for each building block: documents, metadata, ontology
6. Multi-pass knowledge building - derive entities and relationships from documents, then re-summarize documents with ontology, then index documents, ontlology, and metadata together
7. Multi-pass querying - map query to ontology, query separately ontology and text, then combine results
8. Human discovery tools - ability to look at ontology, key statistics, understand performance of individual steps
9. Human feedback loop - ability to correct ontology, metadata, and document processing steps
10. Using LLM to benchmark output of key steps: summarization, ontology derivation, entitites reconciliation

## Pipeline Components

1. Document Storage ELT Process - "shallow knowledge"
2. Ontology Extraction ELT Process
3. Document re-summarization with Ontology - "deep knowledge"
4. Entities Reconciliation - "deep knowledge" (borrow best ideas from Senzing)
5. Building links between documents, ontology, and metadata
6. Building a search engine on top of the indexed data - supporting multi-modal queries (text, ontology, metadata)


# Step 1 - Document Storage ELT Process

## 1.1 Document Intake

-   **`inbound_directory`:** The entry point for new documents.
-   **`extractor_factory.py`:**
    -   Monitors the `inbound_directory`.
    -   Identifies the file type of each new document.
    -   Creates the appropriate `Extractor` instance based on the file type.

## 1.2 Initial Metadata Extraction

-   **`MetadataManager`:**
    -   `extract_basic_metadata(document)`: Extracts basic file metadata (filename, type, dates, size).
    -   `create_temp_metadata_file(document)`: Creates a temporary JSON file (e.g., `document_id_temp.json`) to store metadata during processing.

## 1.3 Document Class

''' import os
import uuid

class Document:
    def __init__(self, file_path, document_id=None):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.file_type = os.path.splitext(file_path)[1].lower()
        self.document_id = document_id or str(uuid.uuid4())  # Generate UUID if not provided
        self.metadata = {}
        self.content = {}  # Store extracted content of different types (text, table, etc.)
        self.status = "initialized"

    def update_metadata(self, new_metadata):
        self.metadata.update(new_metadata)

    def add_content(self, content_type, content_data):
        self.content[content_type] = content_data

    def set_status(self, status):
        self.status = status '''

## 1.4 Extractor Classes

''' from abc import ABC, abstractmethod

class Extractor(ABC):
    def __init__(self, document):
        self.document = document

    @abstractmethod
    def extract_content(self):
        pass

    @abstractmethod
    def extract_metadata(self):
        pass

class TextExtractor(Extractor):
    def extract_content(self):
        # Use libraries like textract, tika, or others
        text = self.extract_text(self.document.file_path)
        normalized_text = self.normalize_text(text)
        self.document.add_content("text", normalized_text)
        self.document.set_status("text_extracted")

    def extract_metadata(self):
        text_stats = self.calculate_text_stats(self.document.content["text"])
        self.document.update_metadata({"text_stats": text_stats})

    def extract_text(self, file_path):
        #Specific text extraction logic
        pass

    def normalize_text(self, text):
        # Apply text normalization (lowercase, whitespace removal, etc.)
        pass

    def calculate_text_stats(self, text):
        # Calculate word count, char count, etc.
        pass

class PDFExtractor(TextExtractor):
    def extract_text(self, file_path):
        # Use PyMuPDF or other PDF-specific library
        pass

class DOCXExtractor(TextExtractor):
    def extract_text(self, file_path):
        # Use python-docx library
        pass

class TXTExtractor(TextExtractor):
    def extract_text(self, file_path):
        with open(file_path, 'r') as f:
            return f.read()

class PPTXExtractor(TextExtractor):
    def extract_text(self, file_path):
        # Use python-pptx library
        pass

class ImageExtractor(Extractor):
    def extract_content(self):
        # Use pytesseract for OCR
        ocr_text = self.perform_ocr(self.document.file_path)
        self.document.add_content("ocr_text", ocr_text)
        self.document.set_status("ocr_completed")

    def extract_metadata(self):
        # No image-specific metadata for now, but could add dimensions, etc.
        pass

    def perform_ocr(self, file_path):
        # Perform OCR using Tesseract
        pass

class TableExtractor(Extractor):
    def extract_content(self):
        tables = self.extract_tables(self.document.file_path)
        self.document.add_content("tables", tables)
        self.document.set_status("tables_extracted")

    def extract_metadata(self):
        table_metadata = []
        for i, table in enumerate(self.document.content["tables"]):
            table_metadata.append({
                "table_index": i,
                "rows": len(table),
                "columns": len(table[0]) if table else 0
            })
        self.document.update_metadata({"table_stats": table_metadata})

    def extract_tables(self, file_path):
        # Specific table extraction logic
        pass

class CSVExtractor(TableExtractor):
    def extract_tables(self, file_path):
        # Use pandas or csv module
        pass

class XLSXExtractor(TableExtractor):
    def extract_tables(self, file_path):
        # Use pandas or openpyxl
        pass '''

# 2. Load
## 2.1 Raw Document Storage

### StorageManager:
- store_raw_document(document): Moves the original document from inbound to raw_documents.
- get_raw_document_path(document): Returns the path of a document in raw_documents.
## 2.2 Staging Area
- staging_directory: Used for temporary files during transformation.

# 3. Transform
## 3.1 Content-Specific Transformation

### Transformer Classes:
class Transformer(ABC):
    def __init__(self, document):
        self.document = document

    @abstractmethod
    def transform(self):
        pass

class TextNormalizer(Transformer):
    def transform(self):
        # Further text processing if needed (stemming, lemmatization, etc.)
        pass

class TableToTextConverter(Transformer):
    def transform(self):
        # Convert table data to different text formats (CSV, Markdown, etc.)
        for i, table in enumerate(self.document.content["tables"]):
            text_representation = self.convert_table(table)
            self.document.add_content(f"table_{i}_text", text_representation)

    def convert_table(self, table):
        # Convert table to desired text format
        pass

## 3.2 Metadata Refinement
### MetadataManager:
- update_metadata(document, new_metadata): Adds or updates metadata fields.
- finalize_metadata(document):
- Adds document_id.
- Determines document_type using DocumentClassifier.
- Sets is_ocr_required flag.
- save_metadata(document): Saves the final metadata as document_id.json in staging.

## 3.3 DocumentClassifier
### DocumentClassifier
- classify_document(document): Assigns a document_type based on rules or heuristics.

class DocumentClassifier:
    def classify_document(self, document):
        # Basic example: classify based on filename keywords
        if "meeting_minutes" in document.file_name.lower():
            return "meeting minutes"
        elif "agenda" in document.file_name.lower():
            return "agenda"
        elif "report" in document.file_name.lower():
            return "report"
        # Add more rules as needed
        else:
            return "unknown"

## 4. Pipeline Orchestration
### 4.1 The Pipeline Class

import os
import shutil
import uuid

class Pipeline:
    def __init__(self, inbound_dir, raw_documents_dir, staging_dir):
        self.inbound_dir = inbound_dir
        self.raw_documents_dir = raw_documents_dir
        self.staging_dir = staging_dir
        self.storage_manager = StorageManager(raw_documents_dir, staging_dir)
        self.metadata_manager = MetadataManager(staging_dir)
        self.document_classifier = DocumentClassifier()
        self.extractor_factory = ExtractorFactory()

    def run(self):
        for filename in os.listdir(self.inbound_dir):
            file_path = os.path.join(self.inbound_dir, filename)
            if os.path.isfile(file_path):
                try:
                    self.process_document(file_path)
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
                    # Implement error handling

    def process_document(self, file_path):
        document = Document(file_path)

        # 1. Extract
        extractor = self.extractor_factory.create_extractor(document)
        
        initial_metadata = self.metadata_manager.extract_basic_metadata(document)
        document.update_metadata(initial_metadata)
        self.metadata_manager.create_temp_metadata_file(document)

        extractor.extract_content()
        extractor.extract_metadata()

        # 2. Load (Raw)
        self.storage_manager.store_raw_document(document)

        # 3. Transform
        if "text" in document.content:
            text_normalizer = TextNormalizer(document)
            text_normalizer.transform()
        if "tables" in document.content:
            table_converter = TableToTextConverter(document)
            table_converter.transform()
        if "ocr_text" in document.content:
            # You might want to normalize OCR text as well
            pass

        # 3. Load (Transformed) & Metadata Finalization
        self.storage_manager.store_transformed_content(document)
        document.update_metadata({"document_type": self.document_classifier.classify_document(document)})
        document.update_metadata({"is_ocr_required": "ocr_text" in document.content})
        self.metadata_manager.finalize_metadata(document)
        self.metadata_manager.save_metadata(document)

        document.set_status("completed")

        # Clean up temp metadata file
        self.metadata_manager.delete_temp_metadata_file(document)

## 4.2 StorageManager

class StorageManager:
    def __init__(self, raw_documents_dir, staging_dir):
        self.raw_documents_dir = raw_documents_dir
        self.staging_dir = staging_dir

    def store_raw_document(self, document):
        destination_path = os.path.join(self.raw_documents_dir, document.file_name)
        shutil.copy(document.file_path, destination_path)  # Copy to preserve original
        document.update_metadata({"raw_path": destination_path})

    def get_raw_document_path(self, document):
        return document.metadata.get("raw_path")

    def store_transformed_content(self, document):
        for content_type, content_data in document.content.items():
            if content_type == "text" or content_type.startswith("table_") or content_type == "ocr_text":
                content_path = os.path.join(self.staging_dir, f"{document.document_id}_{content_type}.txt")
                with open(content_path, "w", encoding="utf-8") as f:
                    f.write(content_data)
                document.update_metadata({f"{content_type}_path": content_path})
            elif content_type == "image":
                content_path = os.path.join(self.staging_dir, f"{document.document_id}_{content_type}.{document.file_type}")
                shutil.copy(document.file_path, content_path)
                document.update_metadata({f"{content_type}_path": content_path})

## 4.3 MetadataManager

import json

class MetadataManager:
    def __init__(self, staging_dir):
        self.staging_dir = staging_dir

    def extract_basic_metadata(self, document):
        return {
            "file_name": document.file_name,
            "file_type": document.file_type,
            "creation_date": os.path.getctime(document.file_path),
            "modification_date": os.path.getmtime(document.file_path),
            "file_size": os.path.getsize(document.file_path),
        }

    def create_temp_metadata_file(self, document):
        temp_metadata_path = os.path.join(self.staging_dir, f"{document.document_id}_temp.json")
        with open(temp_metadata_path, "w") as f:
            json.dump(document.metadata, f, indent=4)

    def update_metadata(self, document, new_metadata):
        document.update_metadata(new_metadata)

    def finalize_metadata(self, document):
        # Add any final metadata fields if needed
        pass

    def save_metadata(self, document):
        metadata_path = os.path.join(self.staging_dir, f"{document.document_id}.json")
        with open(metadata_path, "w") as f:
            json.dump(document.metadata, f, indent=4)
    
    def delete_temp_metadata_file(self, document):
        temp_metadata_path = os.path.join(self.staging_dir, f"{document.document_id}_temp.json")
        if os.path.exists(temp_metadata_path):
            os.remove(temp_metadata_path)

## 4.4 ExtractorFactory

class ExtractorFactory:
    def create_extractor(self, document):
        if document.file_type == ".pdf":
            return PDFExtractor(document)
        elif document.file_type == ".docx":
            return DOCXExtractor(document)
        elif document.file_type == ".txt":
            return TXTExtractor(document)
        elif document.file_type == ".pptx":
            return PPTXExtractor(document)
        elif document.file_type == ".csv":
            return CSVExtractor(document)
        elif document.file_type == ".xlsx":
            return XLSXExtractor(document)
        elif document.file_type in [".jpg", ".jpeg", ".png", ".tif", ".tiff"]:
            return ImageExtractor(document)
        else:
            raise ValueError(f"Unsupported file type: {document.file_type}")

### Running the Pipeline
Create directories if they don't exist
inbound_directory = "inbound"
raw_documents_directory = "raw_documents"
staging_directory = "staging"

os.makedirs(inbound_directory, exist_ok=True)
os.makedirs(raw_documents_directory, exist_ok=True)
os.makedirs(staging_directory, exist_ok=True)

### Initialize and run the pipeline
pipeline = Pipeline(inbound_directory, raw_documents_directory, staging_directory)
pipeline.run()