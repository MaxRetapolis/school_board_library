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

1. Document Storage ELT Process - "shallow knowledge" creation
2. Ontology Extraction ELT Process
3. Document re-summarization with Ontology - "deep knowledge"
4. Entities Reconciliation - "deep knowledge" (borrow best ideas from Senzing)
5. Building links between documents, ontology, and metadata
6. Building a search engine on top of the indexed data - supporting multi-modal queries (text, ontology, metadata)

# 1. Document Storage ELT Process - "shallow knowledge"

## 1.1 Document Storage ELT Process

### `inbound_directory`

- **Role:** The designated entry point for all new documents.
  
- **Rationale:**  
  Using a directory as the entry point is a simple, standard, and universally understood mechanism for adding files to a system. It's easy to integrate with other systems and requires no special tools or protocols. This approach decouples the document source from the processing pipeline. It allows users to manually drop files in, or any process to write data in, without the process needing to know where the data is coming from. A file system watcher can then be used by the downstream process to be notified when new data has arrived.

### Document Class

- **Role:** Represents a single document throughout the pipeline, encapsulating content, metadata, and processing status.
  
- **Rationale:**  
  The Document class is crucial for maintaining data integrity and simplifying data flow. By encapsulating all relevant information about a document in a single object, we avoid the need to pass multiple variables between functions, reducing the risk of errors and making the code easier to understand. It's also very extensible; if later on there is more relevant data to the document, this can be easily added into the class. This promotes the single responsibility principle at a document level and facilitates efficient tracking of the document's journey through the pipeline.

### ExtractorFactory

- **Role:** Creates the appropriate Extractor instance based on the document type.
  
- **Rationale:**  
  The ExtractorFactory implements the Factory design pattern, which is ideal for abstracting the creation of related objects. This decouples the pipeline from the specific Extractor implementations. Adding support for a new document type becomes as simple as creating a new Extractor class and updating the factory, without modifying any other part of the pipeline. It promotes loose coupling and enhances the system's extensibility.

## 1.2. Extraction

### `Extractor` (Abstract Base Class)

- **Role:** Defines the interface for all content and metadata extractors.
  
- **Rationale:**  
  An abstract base class enforces a consistent interface across all Extractor implementations. This ensures that every extractor provides the necessary methods (`extract_content`, `extract_metadata`), making them interchangeable and promoting code predictability. It also allows for polymorphism, where the Pipeline can treat all extractors uniformly. Using ABCs also allows for much easier testing and validation, as you can test that each concrete implementation of the ABC matches the required interface.

### Concrete Extractor Classes (e.g., `PDFExtractor`, `DOCXExtractor`, `ImageExtractor`, `CSVExtractor`)

- **Role:** Implement the actual extraction logic for a specific document type.
  
- **Rationale:**  
  Separating extraction logic by document type is fundamental for modularity. Each Extractor class focuses on a single, well-defined task, making them easier to develop, test, and maintain. This approach also allows for the use of specialized libraries tailored to each document format (e.g., PyMuPDF for PDF, python-docx for DOCX). Specialization at the Extractor level also ensures better performance as each document can be processed in an optimal way for its type.

### MetadataManager

- **Role:** Handles metadata extraction, storage, and management.
  
- **Rationale:**  
  Centralizing metadata handling in a dedicated class provides several benefits. It separates concerns, keeping extraction logic clean and focused. It allows for consistent metadata formatting and validation across all document types. A dedicated manager also simplifies future enhancements, such as adding support for more sophisticated metadata or integrating with a metadata database. Centralizing this logic also prevents duplication of metadata extraction and transformation code across different Extractor classes.

## 1.3. Load (Raw)

### StorageManager

- **Role:** Manages the storage of both raw and transformed documents.
  
- **Rationale:**  
  The StorageManager abstracts the underlying storage mechanism, decoupling the pipeline from the specifics of file system operations or cloud storage. This makes it easy to switch between different storage backends (e.g., local file system, AWS S3, Azure Blob Storage) without impacting other parts of the system. It also provides a single point of control for managing document storage, improving consistency and reducing redundancy. Having a dedicated manager, rather than managing storage logic in multiple locations, makes it easy to implement additional features like backups or storage optimizations centrally.

## 1.4. Transformation

### `Transformer` (Abstract Base Class)

- **Role:** Defines the interface for content transformation classes.
  
- **Rationale:**  
  Similar to the Extractor ABC, the Transformer ABC ensures consistency across all transformation implementations. This allows the pipeline to apply transformations in a uniform way, regardless of their specific logic. It promotes code reusability and makes it easier to add new transformation steps to the pipeline. Using an ABC also ensures each concrete transformer implements the expected interface.

### Concrete Transformer Classes (e.g., `TextNormalizer`, `TableToTextConverter`)

- **Role:** Implement specific transformation logic.
  
- **Rationale:**  
  Isolating transformation logic into separate classes promotes modularity and maintainability. Each Transformer focuses on a single task, making them easier to understand, test, and modify independently. This approach also allows for the creation of reusable transformation components that can be applied in different combinations or even in other pipelines. Specialized transformers also ensure they are focused on a single task, meaning they are more efficient and effective at that task.

### DocumentClassifier

- **Role:** Assigns a `document_type` to the document.
  
- **Rationale:**  
  Encapsulating document classification logic in a dedicated class promotes modularity and allows for easy modification or replacement of the classification mechanism. The classifier could start with simple rules based on file extensions or keywords and later be upgraded to use machine learning models without affecting other parts of the system. This separation also allows for independent testing and optimization of the classification process. A dedicated class also allows for easy addition of new document types or modification of the classification logic for existing ones.

## 1.5. Load (Transformed)

### StorageManager

- **Role:** Handles storing the transformed content, as described in the "Load (Raw)" section.
  
- **Rationale:**  
  Reusing the StorageManager for both raw and transformed data simplifies the architecture and ensures consistent storage management practices.

## 1.6. Pipeline Orchestration

### Pipeline

- **Role:** The main orchestrator that controls the entire ELT process.
  
- **Rationale:**  
  The Pipeline class is essential for coordinating the interactions between all other components. It provides a central point of control for the workflow, making the overall process easier to understand and manage. The Pipeline also handles error handling and logging, ensuring that the system operates reliably. By abstracting the workflow into a dedicated class, we can easily modify the pipeline's behavior (e.g., adding or removing steps) without affecting the individual components. A dedicated orchestrator makes it easier to implement features like asynchronous processing or conditional execution of pipeline steps.

### Directories

- **`inbound_directory`:** Where new documents arrive.
- **`raw_documents_directory`:** Stores the original, unprocessed documents.
- **`staging_directory`:** Stores transformed content and final metadata.
  
- **Rationale:**  
  Using separate directories for different stages of the process provides a clear organizational structure and helps to prevent accidental modification or deletion of data. It also simplifies data management and allows for easy inspection of the data at each stage. Clearly defined directories also allow for better access control and security measures to be implemented.

## Design Principles

This design prioritizes modularity, making the system:

- **Maintainable:**  
  Each component has a clear responsibility, making it easy to locate and fix bugs or make changes.

- **Extensible:**  
  Adding new features (like supporting new document types or transformations) is straightforward and doesn't require modifying existing code.

- **Testable:**  
  Each module can be tested independently, ensuring the reliability of the entire system.

- **Reusable:**  
  Components like Transformers can be reused in other projects or pipelines.

- **Flexible:**  
  The system can be adapted to different storage backends or processing requirements with minimal effort.
