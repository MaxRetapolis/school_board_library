# School Board Library Development Guide

## Commands
- Setup: `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
- Run tests: `python src/2\ -\ Document\ Classifier/test_pipeline.py`
- Run extended tests: `python src/2\ -\ Document\ Classifier/test_pipeline_extended.py`

## Code Style Guidelines
- **Imports**: Group imports by standard lib, third-party packages, then local modules
- **Typing**: Use type hints (from typing import List, Dict, etc.)
- **Naming**: 
  - snake_case for variables, functions, and modules
  - PascalCase for classes
  - UPPER_CASE for constants
- **Error Handling**: Use try/except with specific exceptions and proper logging
- **Documentation**: Use docstrings for all functions and classes
- **Modularity**: Follow the design principles in README.md - each component has a clear responsibility
- **Logging**: Use the logging_setup module for consistent logging
- **Configuration**: Use config.py for constants and configuration

## Architecture
The system follows an Extract-Load-Transform pipeline with components like Document, Extractor, Transformer, and StorageManager. See README.md for detailed architecture.