#!/usr/bin/env python3
"""
Configuration settings for the School Board Documents Usage Database Generator

This module contains all configurable parameters for the database generator
and query tool, including file paths, database settings, and generation options.
"""

import os
from datetime import date

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_DIR = os.path.join(BASE_DIR, "database")
DATABASE_FILE = os.path.join(DATABASE_DIR, "usage.db")

# Ensure database directory exists
os.makedirs(DATABASE_DIR, exist_ok=True)

# Data generation settings
MEETING_START_DATE = date(2022, 10, 1)
MEETING_END_DATE = date(2023, 10, 1)
MEETING_FREQUENCY_DAYS = 14  # bi-weekly

USAGE_START_DATE = date(2023, 7, 1)
USAGE_END_DATE = date(2023, 10, 1)

# Document types and formats
DOCUMENT_TYPES = [
    "Meeting Minutes", 
    "Agenda", 
    "Report", 
    "Presentation", 
    "Budget", 
    "Newsletter"
]

DOCUMENT_FORMATS = [
    "PDF", 
    "Audio", 
    "Video", 
    "Text"
]

# Generation volume settings
NON_MEETING_DOCUMENTS = 20
NUM_BOTS = 10
NUM_PEOPLE = 100

# Database settings
CHUNK_SIZE = 1000  # Number of records per batch insert

# Query settings
DEFAULT_QUERY_TYPE = "top_documents"
TOP_DOCUMENTS_LIMIT = 10