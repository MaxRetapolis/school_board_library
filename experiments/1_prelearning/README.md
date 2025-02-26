# Pre-Learning Experiment for School Board Document Processing

This project processes a collection of school board documents to extract valuable information and build a knowledge graph. The goal is to assist new school board members by transforming complex institutional knowledge into an accessible format.

## Objectives

- **Document Ingestion**: Read and index documents from the `raw_documents` folder.
- **Text Preprocessing**: Clean and normalize text data for improved extraction.
- **Entity Extraction**: Identify key entities such as participants, events, and topics using NLP techniques.
- **Relationship Extraction**: Determine relationships between entities using dependency parsing and pattern matching.
- **Data Structuring**: Organize extracted data into structured formats and serialize to JSON.
- **Knowledge Graph Construction**: Build a knowledge graph using a graph database to represent entities and relationships.

## Implementation Steps

1. **Document Ingestion** (`step1_read_documents.py`): Index available files and convert them to plain text.
2. **Text Preprocessing** (`step2_preprocess_documents.py`): Clean and normalize the text files.
3. **Entity Extraction** (`step3_extract_entities.py`): Extract entities from the preprocessed text and save them as JSON.
4. **Relationship Extraction** (`step4_extract_relationships.py`): Extract relationships between entities and save them as JSON.
5. **Knowledge Graph Update** (`step5_update_knowledge_graph.py`): Structure the extracted data and update the knowledge graph.

## Technologies Used

- **Python**: Scripting and processing documents.
- **Natural Language Processing (NLP)**: Extracting entities and relationships.
- **Graph Databases**: Storing and querying the knowledge graph (e.g., Neo4j).

---

This project follows an iterative approach to refine the extraction and processing pipeline, ensuring accurate and useful knowledge representation for new school board members.
