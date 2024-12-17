# School Board Document Processing Pipeline

## Overview

This repository contains a document processing pipeline designed to extract entities and relationships from school board meeting transcripts and build a structured knowledge graph. The pipeline leverages local Language Learning Models (LLMs) through Ollama to ensure data security and control.

## TLDR and Current State ##
My goal is to build a scalable "deep knowledge" extraction process that would derive ontology from the documents and use it to co-index both documents and ontology for improved retrieval.
I figured out necessary prompts and a two step knowledge extraction process. Figuring out how to scale this process staying within the free tier of the SOTA models.

## Pipeline Components

1. **Document Indexing** (`step1_read_documents.py`): Reads and indexes documents from the inbound directory.
2. **Text Preprocessing and OCR** (`step2_preprocess_documents.py`): Cleans and normalizes text files.
3. **Entity Extraction** (`step3_extract_entities.py`): Extracts entities from the preprocessed text and saves them as JSON.
4. **Relationship Extraction** (`step4_extract_relationships.py`): Extracts relationships between entities and saves them as JSON.
5. **Knowledge Graph Update** (`step5_update_knowledge_graph.py`): Structures the extracted data and updates the knowledge graph.

# Experiment 1: Initial Pre-Learning Pipeline

- Implemented a basic document processing pipeline with these components:
  - Document indexing (`step1_read_documents.py`)
  - Text preprocessing and OCR capabilities (`step2_preprocess_documents.py`)
  - Entity extraction using LLM (`step3_extract_entities.py`)
- Established the foundation for processing school board documents.
- Set up OCR processing for PDF documents using Tesseract.
- Created a structured approach for entity extraction.

## Experiment 1 - Lessons Learned

1. **TXT as the Preferred Format**:
   - Plain text (TXT) files have proven to be the most effective format for deriving components of a knowledge graph. Converting various document formats into plain text is a solvable and relatively straightforward problem, facilitating consistent and accurate data extraction.

2. **Challenges with Large Scripts**:
   - The initial approach of building fully functional steps quickly turned into a debugging challenge, akin to a game of whack-a-mole. Once the script exceeded 500 lines, maintaining and troubleshooting the code became increasingly difficult. This highlights the importance of modularizing code and keeping scripts manageable in size.

3. **Effective Use of LLama3.2's Context Window**:
   - LLama3.2's 128K context window can be effectively utilized to load both the prompt and most of the document at once. This capability suggests that chunking documents into smaller parts was premature and unnecessary, as the model can handle larger inputs efficiently.

# Experiment 2: Modularization with Ollama

Building upon the initial pipeline, Experiment 2 focused on enhancing the system's scalability, maintainability, and efficiency through modularization and the integration of Ollama's local LLM capabilities. This phase addressed the challenges encountered in Experiment 1 by restructuring the codebase, implementing robust logging, and optimizing the document processing workflow.

## Key Improvements

1. **Modular Code Structure**:
   - **`tokenizer.py`**: Handles text tokenization, including counting tokens, words, lines, and characters.
   - **`ollama_call_external_prompt.py`**: Manages interactions with Ollama for processing prompts and context files.
   - **`ollama_index_txt_json_converter.py`**: Converts parsed text from Ollama into structured JSON formats.
   - **`ollama_event_indexer.py`**: Indexes events from Ollama's output for knowledge graph integration.
   - **`inbound_file_indexer_tokenizer.py`**: Indexes and tokenizes inbound documents, compiling statistics into a JSON index.
   - **Benefit:** Enhances code maintainability, allows parallel development, and simplifies testing of individual components.

2. **Token-Based Processing Approach**:
   - Utilized the `tiktoken` library to tokenize documents, enabling efficient handling of large texts.
   - Leveraged LLama3.2's extensive 128K context window to process larger inputs without necessitating premature document chunking.

## Experiment 2 - Lessons Learned

1. **Optimizing Model Output for Post-Processing**:
   - **Challenge:** Deriving entities directly into a structured JSON format using models proved to be highly time-consuming and yielded suboptimal results despite numerous iterations.
   - **Solution:** Adopted a two-step approach where the model first generates text files with a predictable structure. These structured text outputs are then efficiently parsed into JSON using Python tools.
   - **Benefit:** Streamlines entity extraction, reduces development time, and enhances data reliability by separating generation from structuring.

2. **Implementing a Multi-Pass Knowledge Extraction Approach**:
   - **Challenge:** Single-pass extraction strategies were insufficient for capturing the complexity needed for a comprehensive knowledge graph.
   - **Solution:** Developed a multi-pass methodology:
     1. **Summarization Pass:** Summarize documents to identify a common set of ontology objects.
     2. **Focused Extraction Pass:** Re-summarize each document with prompts emphasizing these objects.
     3. **Relationship Derivation Pass:** Re-analyze summaries to derive individual objects and their relationships.
   - **Benefit:** Enhances depth and accuracy of knowledge extraction, ensuring comprehensive capture of entities and their interrelations.

3. **Customizing Prompts for Diverse Document Types**:
   - **Challenge:** Using uniform prompts for varied documents like transcripts and meeting summaries led to poor extraction quality.
   - **Solution:** Developed customized prompts tailored to specific document types, ensuring alignment with their unique structures and content.
   - **Benefit:** Significantly improves extraction accuracy by adapting prompt design to the inherent features of each document type.

## Current Pipeline Components

1. **Tokenizer (`tokenizer.py`)**
   - **Function:** Reads and tokenizes text files, counting tokens, words, lines, and characters.
   - **Benefit:** Prepares documents for efficient entity extraction and indexing.

2. **Ollama Prompt Caller (`ollama_call_external_prompt.py`)**
   - **Function:** Sends prompts to Ollama's LLM and retrieves responses.
   - **Benefit:** Facilitates interaction with Ollama for processing documents.

3. **TXT to JSON Converter (`ollama_index_txt_json_converter.py`)**
   - **Function:** Converts Ollama's text outputs into structured JSON.
   - **Benefit:** Transforms raw outputs for downstream processing.

4. **Event Indexer (`ollama_event_indexer.py`)**
   - **Function:** Indexes events from JSON outputs for the knowledge graph.
   - **Benefit:** Organizes extracted events for easy retrieval and analysis.

5. **Inbound File Indexer (`inbound_file_indexer_tokenizer.py`)**
   - **Function:** Indexes and tokenizes inbound documents, compiling statistics into JSON.
   - **Benefit:** Provides an overview for batch processing and monitoring.

# Experiment 3: Ontology and Summarization Optimization

Experiment 3 aims to refine the ontology definition and document summarization processes to enhance the accuracy and efficiency of the knowledge extraction pipeline. This phase focuses on developing specialized prompts, optimizing summarization strategies for large documents, and ensuring high-quality outputs.

## Key Objectives

1. **Developing Ontology-Defining Prompts**:
   - Create a collection of prompts to accurately define ontology elements such as events, processes, and other relevant categories, leveraging the existing prompt framework.

2. **Customized Summarization Prompts for Diverse Documents**:
   - Design tailored prompts for summarizing and normalizing different types of documents (e.g., transcripts, meeting notes) to capture essential information effectively.

3. **Optimizing Summarization for Large Documents**:
   - Explore strategies to summarize documents exceeding the 128K token limit of LLama3.2.
   - Evaluate the impact of utilizing the full context window versus chunking documents into smaller segments (e.g., 60K tokens) on summary quality.

## Experiment 3 - Lessons Learned

1. **Re-summarizing original documents WITH ontology looks very promising**:
   - **Challenge:** Local Models (Llama 3.2, Llama 3.3), and earlier SOTA models (GPT-4o) have a token limit of 128K tokens. This limit restricts the ability to summarize large documents effectively. They also struggle producing high quality json ontologies.
   - **Solution:** Manually processed documents through GPT O1 and Gemini 2.0 using a 2 step approach. First, summarize the document to identify the ontology. Second, re-summarize the document with prompts emphasizing the ontology. This approach has shown to be very effective in extracting entities and relationships from large documents. A two step approach shows a 10% increase in quality of document summarization.
   - **Improved solution:** Migrated to JSON-LD (Linked Data) format for the ontology and extended existing Schema.org ontologies to be as specific to the education domain as possible. This, anekdotally, improved quality of document summarization by another 10 %.
   - **Benefit:** An approach that can be automated through a prompt chain and can be used to extract entities and relationships from large documents as well as re-summarize them en-masse.
   - **Potential Concern:** Using SOTA models will be expensive, around $3 per document. Need to figure out how to stay within the free tier of OpenAI and Gemini.
