# School Board Library Document Management

## Overview
This project manages the storage, classification, and maintenance of documents for the school board library. It processes various document types, classifies them based on their content, and organizes them into designated folders.

## Configuration
All configuration settings are centralized in the [`config.py`](./config.py) file. Ensure that this file is properly set up before running the scripts.

## Modules
- `1_inbound_documents.py`: Handles the ingestion and initial processing of new documents.
- `2_Document_Classifier.py`: Classifies documents based on their content and moves them to appropriate folders.
- `file_operations.py`: Contains functions for file manipulation.
- `index_management.py`: Manages the document index.
- `logging_setup.py`: Configures logging for the application.
- `utils.py`: Provides utility functions used across the project.

## Setup
1. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2. Configure the `config.py` with appropriate paths and settings.
3. Run the scripts as needed:
    ```bash
    python 1_inbound_documents.py
    python 2_Document_Classifier.py
    ```

## Logging
Logs are stored in the `logs` folder as specified in the `config.py`. Check these logs for detailed information about the operations and any errors encountered.

## License
This project is licensed under the MIT License.

# Document Storage ELT Process: Building Blocks and High-Level Flow

This document outlines the key components and workflow of a modular and observable ELT (Extract, Load, Transform) pipeline for document storage.

## Overview of Building Blocks

### Directory Watcher

*   **Role:** Monitors the `inbound_directory` for new files.
*   **Key Features:**
    *   Simple event-based logic (e.g., filesystem events) to detect new documents.
    *   Emits an "ingestion event" whenever a new file arrives.
*   **Observability:** Logs each new file detected, provides metrics (e.g., files processed per hour).
*   **Rationale:**  Utilizes a standard and efficient mechanism (filesystem events) for new file detection, decoupling the arrival of documents from the rest of the pipeline. It provides a simple interface for triggering the processing workflow. Logging and metrics provide insight into the ingestion rate and potential bottlenecks.

### Document Class

*   **Role:** Represents a single document throughout the pipeline.
*   **Key Features:**
    *   Encapsulates content, metadata, and processing status.
    *   **Modularity:** A single source of truth for all document-related data.
*   **Observability:** Holds an "audit trail" or "event list" so each step can log actions taken on the document.
*   **Rationale:** This class is central to data management within the pipeline. Encapsulating all document data in a single object simplifies data flow, reduces errors, and enhances traceability by providing a detailed history of operations performed on the document.

### ExtractorFactory

*   **Role:** Decides which `Extractor` to instantiate based on file type or classification rules.
*   **Key Features:**
    *   **Lazy/Greedy Approach:**
        *   **Lazy:** Delegates actual extraction to specialized `Extractor`.
        *   **Greedy:** Might call a Large Language Model (LLM) or heuristic to guess document type if not obvious.
    *   **Modularity:** Adding a new `Extractor` is as simple as adding a new mapping in the factory.
*   **Rationale:** The `ExtractorFactory` abstracts the creation of `Extractor` instances, promoting loose coupling and extensibility. The lazy/greedy approach allows for flexibility in handling known and unknown document types, leveraging advanced techniques like LLMs when needed. This design makes adding support for new document types straightforward.

### Extractor (Abstract Base Class)

*   **Role:** Defines the interface (`extract_content`, `extract_metadata`) that all `Extractor`s must implement.
*   **Key Features:**
    *   **Modularity & Observability:**
        *   Each `Extractor` can log or emit metrics (e.g., time to extract, size of extracted content).
        *   Enables consistent extraction steps across multiple document types.
    *   **Standing on the Shoulders of Giants:**
        *   Implementation can leverage state-of-the-art libraries (PyMuPDF, python-docx, etc.).
*   **Rationale:**  The abstract base class ensures a uniform interface for all extractors, making them interchangeable and promoting code predictability. It also facilitates the integration of established libraries for specific document formats, improving efficiency and reliability. Observability features allow for monitoring the performance of each extractor.

### Concrete Extractors (e.g., `PDFExtractor`, `DOCXExtractor`, `ImageExtractor`, `CSVExtractor`)

*   **Role:** Specialized classes that perform the actual extraction logic for each document type.
*   **Key Features:**
    *   **Efficiency & Maintainability:** Each `Extractor` focuses on a single file format.
    *   **Observability:** Each `Extractor` logs extraction success/failure, metadata discovered.
*   **Rationale:** Specialization improves efficiency and maintainability by allowing each `Extractor` to focus on the nuances of a specific document format. Logging provides crucial insights into the extraction process, aiding in debugging and performance optimization.

### MetadataManager

*   **Role:** Central place for metadata handling (standardizing, storing, retrieving).
*   **Key Features:**
    *   **Modularity:** Avoid duplicating metadata logic in every `Extractor`.
    *   **Observability:**
        *   Tracks schema versions, extraction coverage (e.g., how many metadata fields were populated).
        *   Potential for hooking into an LLM for more advanced metadata generation if needed.
*   **Rationale:** Centralizing metadata management ensures consistency, avoids code duplication, and simplifies future enhancements. Observability features provide insights into metadata quality and completeness. The potential to integrate with LLMs opens up possibilities for richer metadata extraction.

### StorageManager (Raw Storage)

*   **Role:** Manages storing the original files and extracted content in a designated "raw" or "staging" area.
*   **Key Features:**
    *   **Databus/Document Storage:**
        *   Ensures each document is properly versioned and accessible for future steps.
    *   **Observability:** Logs storage events, errors, and throughput metrics (e.g., document size, storage location).
*   **Rationale:** The `StorageManager` abstracts the storage mechanism, making it easy to switch between different storage solutions. Versioning ensures data integrity and allows for potential rollback. Observability features provide insights into storage utilization and performance.

### Logging, Events, Metrics (Cross-Cutting Concern)

*   **Role:** Ensures each component creates sufficient logs, events, and metrics for observability.
*   **Key Features:**
    *   Centralized logging system (or a standard logging interface).
    *   Event bus or queue for asynchronous event processing/monitoring.
    *   Metrics aggregator (could be as simple as a stats collector or integrated with a monitoring tool).
*   **Rationale:** Observability is crucial for monitoring the health and performance of the pipeline. Centralized logging, an event bus, and a metrics aggregator enable effective monitoring, troubleshooting, and performance analysis.

## High-Level Flow

1.  **File Arrival & Detection**
    *   A file is dropped into the `inbound_directory`.
    *   `Directory Watcher` detects the file and emits an event.

2.  **Document Creation**
    *   A new `Document` object is initialized with:
        *   File path / raw binary data.
        *   Initial metadata (filename, file size, creation timestamp).
    *   The `Document` is logged in the system (creating a unique ID).

3.  **Extractor Selection**
    *   `ExtractorFactory` examines the file type (via extension, MIME type, or LLM-based guess).
    *   The factory returns the appropriate Concrete `Extractor`.

4.  **Document Extraction**
    *   The Concrete `Extractor` performs `extract_content` and `extract_metadata`.
    *   Extraction details are passed to the `MetadataManager`, which normalizes and stores metadata.
    *   **Observability:**
        *   Extraction logs (time taken, text length, any errors).
        *   Metrics (e.g., number of characters extracted, success/failure rates).

5.  **Raw Storage**
    *   `StorageManager` (for raw data) stores:
        *   The original file (untouched) in a `raw_documents_directory`.
        *   Any immediately extracted content or partial transformations in a `staging_directory`.
    *   **Observability:** Logs a "document stored" event and associated metadata.

6.  **Ready for Next Step**
    *   At this point, the document has been Extracted (basic "shallow knowledge") and stored.
    *   Further steps (Transformations, Ontology Extraction, etc.) can proceed in subsequent pipeline stages.

## Alignment with Key Design Principles

### Modularity, Linearity, Databus/Document Storage

*   Each component (`Directory Watcher`, `Extractor`, `MetadataManager`, `StorageManager`) has a focused role and well-defined interface.
*   The pipeline remains linear at this stage, flowing from file ingestion → extraction → storage, with a central `Document` object as the data bus.

### Observability

*   Every step emits logs, metrics, and relevant events (e.g., "new file detected," "extraction succeeded," "document stored").
*   This ensures that operational insights (e.g., performance bottlenecks, error rates) are accessible.

### Lazy/Greedy Approach

*   **Greedy** in that we may leverage LLM-based classification or advanced file-type detection if necessary.
*   **Lazy** in that deeper transformations and ontology derivation are deferred until after the initial extraction pass.

### Standing on the Shoulders of Giants

*   `Extractor`s can use best-in-class libraries (PyMuPDF, python-docx, etc.) to avoid reinventing the wheel.
*   The `MetadataManager` could adopt or extend schema.org data models for basic fields (e.g., schema:Document, schema:author).

### ELT

*   **Extract:** Done by the `Extractor` (pulling raw data and metadata).
*   **Load:** Initial load into a persistent storage (via `StorageManager`).
*   **Transform:** Full transformations happen later in the pipeline, but partial transformations (like basic text normalization) can happen here if needed.