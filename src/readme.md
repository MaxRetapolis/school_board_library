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