Below is a detailed prompt designed for Claude 3.7 to generate a Python program that meets the user's requirements. The prompt includes all necessary descriptors, detailed instructions, and optimizations to ensure clarity and completeness. It is structured to be passed directly to Claude 3.7 for code generation.

---

## Prompt for Claude 3.7

**Task**: Develop a Python program that generates a simulated usage file stored as an SQLite database. The database will contain usage statistics for various school board meeting documents over a 3-month period. The documents include both meeting-related and non-meeting documents, each with associated metadata (including document type and format) and usage data from bots and people. The program must use an atomic and composable architecture with clearly defined, reusable functional blocks and a centralized configuration system.

**Requirements**:
- Implement the program using an **atomic and composable architecture**, where each functional block is a separate, reusable Python function.
- Create a **centralized configuration module** to store all configurable parameters.
- Store the database in a dedicated **/database** directory.
- Ensure that each function is modular, with clear inputs and outputs, allowing for independent testing and reuse.
- Integrate all functional blocks into a cohesive system that produces an SQLite database as the final output.
- Use Python 3.x and standard libraries (`datetime`, `random`, `sqlite3`, `os`, `sys`, `argparse`)—no external dependencies.
- Include optimizations for efficiency, such as batching database inserts, and ensure consistent handling of dates as `datetime.date` objects.
- Provide a robust command-line query tool for analyzing the generated data.

**Functional Blocks**:
1. **Generate Meeting Dates**: Create bi-weekly meeting dates for a specified period.
2. **Generate Document Metadata**: Produce metadata for meeting-related and non-meeting documents, including document type and format.
3. **Generate Pool of Bots and People**: Create lists of bot and people names as usage sources.
4. **Generate Usage Data**: Simulate daily usage statistics for each document over 3 months.
5. **Store Data in SQLite**: Save the usage data into an SQLite database in the /database directory.
6. **Query Database**: Provide a command-line tool for querying the database with multiple query types and filtering options.

**Instructions**:

### Block 0: Configuration Module

**Purpose**: Provide a centralized place for all configurable parameters.

**Implementation Details**:
- Create a `config.py` module containing:
  - File paths (base directory, database directory, database file path)
  - Date settings (meeting start/end dates, usage start/end dates)
  - Document types and formats lists
  - Generation volume settings (number of bots, people, non-meeting documents)
  - Database settings (chunk size for batch inserts)
  - Query settings (default query type, limit for top documents)
- Use `os.path` functions to construct absolute paths
- Create a function to ensure the database directory exists

**Example Code**:
```python
#!/usr/bin/env python3
"""
Configuration settings for the School Board Documents Usage Database Generator
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
```

### Block 1: Generate Meeting Dates

**Purpose**: Generate a list of bi-weekly meeting dates between two dates.

**Input**:
- `start_date`: A `datetime.date` object (e.g., `datetime.date(2022, 10, 1)`).
- `end_date`: A `datetime.date` object (e.g., `datetime.date(2023, 10, 1)`).
- `frequency_days`: An integer for the interval between meetings (e.g., 14 for bi-weekly).

**Output**:
- A list of `datetime.date` objects representing meeting dates.

**Implementation Details**:
- Use the `datetime` module's `date` and `timedelta` classes.
- Initialize an empty list `meeting_dates`.
- Set `current_date = start_date`.
- Use a `while` loop to increment `current_date` by `frequency_days` until it exceeds `end_date`.
- Append each `current_date` to `meeting_dates`.
- Return the list.

**Example Code**:
```python
from datetime import date, timedelta

def generate_meeting_dates(start_date, end_date, frequency_days):
    """
    Generate a list of bi-weekly meeting dates between two dates.
    
    Args:
        start_date: A datetime.date object for the start date
        end_date: A datetime.date object for the end date
        frequency_days: An integer for the interval between meetings
        
    Returns:
        A list of datetime.date objects representing meeting dates
    """
    meeting_dates = []
    current_date = start_date
    while current_date <= end_date:
        meeting_dates.append(current_date)
        current_date += timedelta(days=frequency_days)
    return meeting_dates
```

**Notes**:
- Ensure `start_date` and `end_date` are `datetime.date` objects to maintain consistency.
- Use docstrings to document function purpose, parameters, and return values.

---

### Block 2: Generate Document Metadata

**Purpose**: Create metadata for meeting-related and non-meeting documents.

**Input**:
- `meeting_dates`: A list of `datetime.date` objects from Block 1.
- `document_types`: A list of strings (e.g., `["Meeting Minutes", "Agenda", "Report"]`).
- `formats`: A list of strings (e.g., `["PDF", "Audio"]`).
- `num_non_meeting`: An integer for the number of non-meeting documents (default: 20).

**Output**:
- A list of tuples: `(document_type, format, document_name, document_date)`.

**Implementation Details**:
- Import `random` and `datetime.timedelta`.
- Initialize an empty list `metadata`.
- **Meeting-Related Documents**:
  - For each `date` in `meeting_dates`, generate entries for "Agenda" and "Meeting Minutes" (if in `document_types`).
  - Create a `document_name` like `"Agenda_YYYY-MM-DD"` using `date.strftime('%Y-%m-%d')`.
  - Randomly select a `format` from `formats` using `random.choice`.
  - Append `(document_type, format, document_name, date)` to `metadata`.
- **Non-Meeting Documents**:
  - Generate `num_non_meeting` documents.
  - Calculate the date range: `min_date = min(meeting_dates)`, `max_date = max(meeting_dates)`.
  - Compute `date_range = (max_date - min_date).days`.
  - For each document:
    - Pick a random `document_type` from `document_types`.
    - Pick a random `format` from `formats`.
    - Generate a random date: `min_date + timedelta(days=random.randint(0, date_range))`.
    - Create a `document_name` like `"Report_YYYY-MM-DD"`.
    - Append the tuple to `metadata`.
- Return `metadata`.

**Example Code**:
```python
import random
from datetime import timedelta

def generate_document_metadata(meeting_dates, document_types, formats, num_non_meeting=20):
    """
    Create metadata for meeting-related and non-meeting documents.
    
    Args:
        meeting_dates: A list of datetime.date objects
        document_types: A list of strings (e.g., "Meeting Minutes", "Agenda", "Report")
        formats: A list of strings (e.g., "PDF", "Audio")
        num_non_meeting: An integer for the number of non-meeting documents
        
    Returns:
        A list of tuples: (document_type, format, document_name, document_date)
    """
    metadata = []
    # Meeting-related documents
    for date in meeting_dates:
        for doc_type in ["Agenda", "Meeting Minutes"]:
            if doc_type in document_types:
                name = f"{doc_type}_{date.strftime('%Y-%m-%d')}"
                fmt = random.choice(formats)
                metadata.append((doc_type, fmt, name, date))
    
    # Non-meeting documents
    min_date = min(meeting_dates)
    max_date = max(meeting_dates)
    date_range = (max_date - min_date).days
    for _ in range(num_non_meeting):
        doc_type = random.choice(document_types)
        fmt = random.choice(formats)
        random_days = random.randint(0, date_range)
        doc_date = min_date + timedelta(days=random_days)
        name = f"{doc_type}_{doc_date.strftime('%Y-%m-%d')}"
        metadata.append((doc_type, fmt, name, doc_date))
    
    return metadata
```
   
**Notes**:
- Use `strftime('%Y-%m-%d')` for consistent date formatting in names.
- Include comprehensive docstrings that document the function's purpose, parameters, and return values.

---

### Block 3: Generate Pool of Bots and People

**Purpose**: Create static pools of bot and people names for usage simulation.

**Input**:
- `num_bots`: An integer for the number of bots (default: 10).
- `num_people`: An integer for the number of people (default: 100).

**Output**:
- A tuple of two lists: `bot_names` (list of strings) and `people_names` (list of strings).

**Implementation Details**:
- Import `random`.
- **Bot Names**:
  - Generate simple bot names like `"Bot1"`, `"Bot2"`, etc., up to `num_bots`.
  - Use a list comprehension for efficiency.
- **People Names**:
  - Define comprehensive lists of first_names (at least 20) and last_names (at least 20).
  - Use a list comprehension to create `num_people` names by combining random `first_names` and `last_names` (e.g., `"Alice Smith"`).
- Return `(bot_names, people_names)`.

**Example Code**:
```python
import random

def generate_bots_and_people(num_bots=10, num_people=100):
    """
    Create static pools of bot and people names for usage simulation.
    
    Args:
        num_bots: An integer for the number of bots
        num_people: An integer for the number of people
        
    Returns:
        A tuple of two lists: bot_names and people_names
    """
    bot_names = [f"Bot{i}" for i in range(1, num_bots + 1)]
    
    first_names = ["Alice", "Bob", "Charlie", "Dana", "Eve", "Frank", "Grace", "Heidi", 
                  "Ivan", "Julia", "Kevin", "Linda", "Michael", "Nancy", "Oscar", 
                  "Patricia", "Quentin", "Rachel", "Samuel", "Tina"]
    
    last_names = ["Smith", "Jones", "Brown", "Taylor", "Wilson", "Davis", "Miller", 
                 "Moore", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", 
                 "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez"]
    
    people_names = [f"{random.choice(first_names)} {random.choice(last_names)}" 
                   for _ in range(num_people)]
    
    return bot_names, people_names
```

**Notes**:
- Provide large enough name pools to simulate realistic user diversity.
- Document the function with comprehensive docstrings.

---

### Block 4: Generate Usage Data

**Purpose**: Simulate daily usage statistics for each document.

**Input**:
- `document_metadata`: A list of `(type, format, name, date)` tuples from Block 2.
- `start_date`: A `datetime.date` object (e.g., `datetime.date(2023, 7, 1)`).
- `end_date`: A `datetime.date` object (e.g., `datetime.date(2023, 10, 1)`).
- `bot_names`: A list of bot name strings from Block 3.
- `people_names`: A list of people name strings from Block 3.

**Output**:
- A list of tuples: `(document_name, document_type, document_format, date, bot_hits, people_hits, total_hits)`.

**Implementation Details**:
- Import `random` and `datetime.timedelta`.
- Generate a list `date_list` of all dates from `start_date` to `end_date` using a `while` loop and `timedelta(days=1)`.
- For each `(doc_type, doc_format, doc_name, doc_date)` in `document_metadata`:
  - For each `date` in `date_list`:
    - Randomly select `num_bots` (0 to min(5, len(bot_names))) using `random.randint`.
    - Randomly select `num_people` (0 to min(10, len(people_names))) using `random.randint`.
    - Select `bots = random.sample(bot_names, num_bots)` and `people = random.sample(people_names, num_people)`.
    - Compute `bot_hits = sum(random.randint(1, 50) for _ in bots)`.
    - Compute `people_hits = sum(random.randint(1, 50) for _ in people)`.
    - Compute `total_hits = bot_hits + people_hits`.
    - Append `(doc_name, doc_type, doc_format, date, bot_hits, people_hits, total_hits)` to `usage_data`.
- Return `usage_data`.

**Example Code**:
```python
from datetime import date, timedelta
import random

def generate_usage_data(document_metadata, start_date, end_date, bot_names, people_names):
    """
    Simulate daily usage statistics for each document.
    
    Args:
        document_metadata: A list of (type, format, name, date) tuples
        start_date: A datetime.date object 
        end_date: A datetime.date object
        bot_names: A list of bot name strings
        people_names: A list of people name strings
        
    Returns:
        A list of tuples: (document_name, document_type, document_format, date, bot_hits, people_hits, total_hits)
    """
    usage_data = []
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)
    
    for doc_type, doc_format, doc_name, _ in document_metadata:
        for date in date_list:
            num_bots = random.randint(0, min(5, len(bot_names)))
            num_people = random.randint(0, min(10, len(people_names)))
            bots = random.sample(bot_names, num_bots)
            people = random.sample(people_names, num_people)
            bot_hits = sum(random.randint(1, 50) for _ in bots)
            people_hits = sum(random.randint(1, 50) for _ in people)
            total_hits = bot_hits + people_hits
            usage_data.append((doc_name, doc_type, doc_format, date, bot_hits, people_hits, total_hits))
    
    return usage_data
```

**Optimization**:
- Use `random.sample` instead of `random.choice` to avoid duplicate selections within a day.
- Include document type and format in the output for better querying capabilities.

---

### Block 5: Store Data in SQLite

**Purpose**: Store usage data in an SQLite database.

**Input**:
- `usage_data`: A list of `(document_name, document_type, document_format, date, bot_hits, people_hits, total_hits)` tuples from Block 4.
- `db_path`: A string for the full path to the database file.

**Output**:
- An SQLite database file with a table `usage`.

**Implementation Details**:
- Import `sqlite3` and `os`.
- Ensure the database directory exists using `os.makedirs`.
- Connect to `db_path` using `sqlite3.connect`.
- Create a cursor object.
- Execute a `CREATE TABLE IF NOT EXISTS` statement for `usage` with columns:
  - `document_name` (TEXT)
  - `document_type` (TEXT)
  - `document_format` (TEXT)
  - `date` (TEXT)
  - `bot_hits` (INTEGER)
  - `people_hits` (INTEGER)
  - `total_hits` (INTEGER)
- Use `cursor.executemany` to insert `usage_data`, formatting dates as `'YYYY-MM-DD'`.
- Implement batch inserts using chunking for performance with large datasets.
- Add proper error handling with try-except blocks for database operations.
- Commit changes and close the connection.

**Example Code**:
```python
import sqlite3
import os

def store_in_sqlite(usage_data, db_path):
    """
    Store usage data in an SQLite database.
    
    Args:
        usage_data: A list of (document_name, document_type, document_format, date, bot_hits, people_hits, total_hits) tuples
        db_path: The full path to the database file
        
    Returns:
        None (creates an SQLite database file)
    """
    try:
        # Ensure database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage (
                document_name TEXT,
                document_type TEXT,
                document_format TEXT,
                date TEXT,
                bot_hits INTEGER,
                people_hits INTEGER,
                total_hits INTEGER
            )
        """)
        
        # Convert dates to string format for SQLite
        formatted_data = [
            (name, doc_type, doc_format, date.strftime('%Y-%m-%d'), b_hits, p_hits, t_hits)
            for name, doc_type, doc_format, date, b_hits, p_hits, t_hits in usage_data
        ]
        
        # Batch inserts for better performance
        chunk_size = 1000
        for i in range(0, len(formatted_data), chunk_size):
            chunk = formatted_data[i:i + chunk_size]
            cursor.executemany("""
                INSERT INTO usage (document_name, document_type, document_format, date, bot_hits, people_hits, total_hits)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, chunk)
        
        conn.commit()
        print(f"Database '{db_path}' created successfully.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()
```

**Optimization**:
- Use `executemany` for batch inserts to improve performance with large datasets.
- Use chunking for very large datasets to manage memory usage.
- Add proper error handling to make the function robust against I/O errors.
- Ensure the database directory exists before trying to create the database.

---

### Block 6: Query Database Tool

**Purpose**: Provide a command-line interface to query the usage database.

**Features**:
- Multiple query types:
  - `top_documents`: Get top N documents by total hits
  - `daily_summary`: Get daily summary of hits
  - `document_detail`: Get detailed information about a specific document
  - `type_summary`: Get summary by document type
  - `format_summary`: Get summary by document format
- Filtering options:
  - Date range filtering
  - Document name filtering
  - Document type filtering
  - Document format filtering
- Command-line arguments parsing using `argparse`
- Formatted output for readability

**Implementation Details**:
- Create a main query function that handles different query types
- Implement proper SQL queries for each type
- Add error handling for database operations
- Validate input parameters
- Format output for readability

**Example Code**:
```python
import argparse
import sqlite3
import sys
import os
from datetime import datetime

# Import configuration
from config import DATABASE_FILE, DEFAULT_QUERY_TYPE, TOP_DOCUMENTS_LIMIT

def execute_query(db_path, query_type, start_date=None, end_date=None, document=None, doc_type=None, doc_format=None):
    """
    Execute a query on the usage database based on the specified type.
    
    Args:
        db_path: Path to the SQLite database file
        query_type: Type of query to execute (top_documents, daily_summary, document_detail, 
                   type_summary, format_summary)
        start_date: Start date for filtering (YYYY-MM-DD)
        end_date: End date for filtering (YYYY-MM-DD)
        document: Document name for filtering
        doc_type: Document type for filtering
        doc_format: Document format for filtering
        
    Returns:
        Query results
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Implement different query types here
        # ...
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

def validate_date(date_str):
    """Validate that a date string is in YYYY-MM-DD format"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")

def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(description="Query the usage database")
    
    parser.add_argument('--db', default=DATABASE_FILE, 
                        help=f'Path to the SQLite database file (default: {DATABASE_FILE})')
    
    parser.add_argument('--query', 
                        choices=['top_documents', 'daily_summary', 'document_detail', 
                                'type_summary', 'format_summary'],
                        default=DEFAULT_QUERY_TYPE, 
                        help=f'Type of query to execute (default: {DEFAULT_QUERY_TYPE})')
    
    parser.add_argument('--start-date', type=validate_date, 
                        help='Start date for filtering (YYYY-MM-DD)')
    
    parser.add_argument('--end-date', type=validate_date,
                        help='End date for filtering (YYYY-MM-DD)')
    
    parser.add_argument('--document', help='Document name for filtering')
    
    parser.add_argument('--type', dest='doc_type', help='Document type for filtering')
    
    parser.add_argument('--format', dest='doc_format', help='Document format for filtering')
    
    args = parser.parse_args()
    
    # Check if the database file exists
    if not os.path.exists(args.db):
        print(f"Error: Database file '{args.db}' does not exist.")
        print(f"Please run the generator first to create the database.")
        sys.exit(1)
    
    execute_query(args.db, args.query, args.start_date, args.end_date, 
                 args.document, args.doc_type, args.doc_format)

if __name__ == "__main__":
    main()
```

### Shell Script for Running Everything

**Purpose**: Provide a convenient way to run the entire pipeline.

**Features**:
- Check for Python installation
- Create the database directory if it doesn't exist
- Run the generator
- Verify database creation was successful
- Run example queries to demonstrate functionality

**Example Code**:
```bash
#!/bin/bash
# Run script for School Board Documents Usage Database Generator

# Print header
echo "================================================"
echo "School Board Documents Usage Database Generator"
echo "================================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Get database path from config
DB_DIR="database"
DB_PATH="$DB_DIR/usage.db"

# Ensure database directory exists
mkdir -p "$DB_DIR"

# Run the usage database generator
echo "Generating usage database..."
python3 src/usage_db_generator.py

# Check if database was created successfully
if [ ! -f "$DB_PATH" ]; then
    echo "Error: Failed to create database at $DB_PATH"
    exit 1
fi

echo
echo "Database generated successfully at $DB_PATH"
echo

# Run some example queries
echo "Running example queries..."
echo

echo "1. Top 10 documents by total hits:"
python3 src/query_usage_db.py --db "$DB_PATH" --query top_documents

echo
echo "2. Daily summary for August 2023:"
python3 src/query_usage_db.py --db "$DB_PATH" --query daily_summary --start-date 2023-08-01 --end-date 2023-08-31

echo
echo "3. Summary by document type:"
python3 src/query_usage_db.py --db "$DB_PATH" --query type_summary

echo
echo "4. Summary by document format:"
python3 src/query_usage_db.py --db "$DB_PATH" --query format_summary

echo
echo "5. Detailed information for a specific document type (Agenda):"
python3 src/query_usage_db.py --db "$DB_PATH" --query type_summary --type "Agenda"

echo
echo "Done!"
```

### Integration

**Main Script**:
- Import configuration from config.py
- Combine all blocks into a single executable script.
- Use the configuration values for all parameters.

**Example Integration**:
```python
import random
import os
import sys

# Import configuration
from config import (
    DATABASE_FILE, MEETING_START_DATE, MEETING_END_DATE, MEETING_FREQUENCY_DAYS,
    USAGE_START_DATE, USAGE_END_DATE, DOCUMENT_TYPES, DOCUMENT_FORMATS,
    NON_MEETING_DOCUMENTS, NUM_BOTS, NUM_PEOPLE, CHUNK_SIZE
)

def main():
    """
    Main function to execute all blocks in sequence.
    """
    # Set random seed for reproducibility
    random.seed(42)
    
    # Block 1: Generate meeting dates
    meeting_dates = generate_meeting_dates(
        MEETING_START_DATE, 
        MEETING_END_DATE, 
        MEETING_FREQUENCY_DAYS
    )
    print(f"Generated {len(meeting_dates)} meeting dates")
    
    # Block 2: Generate document metadata
    metadata = generate_document_metadata(
        meeting_dates, 
        DOCUMENT_TYPES, 
        DOCUMENT_FORMATS, 
        num_non_meeting=NON_MEETING_DOCUMENTS
    )
    print(f"Generated metadata for {len(metadata)} documents")
    
    # Block 3: Generate bots and people
    bot_names, people_names = generate_bots_and_people(
        num_bots=NUM_BOTS, 
        num_people=NUM_PEOPLE
    )
    print(f"Generated {len(bot_names)} bots and {len(people_names)} people")
    
    # Block 4: Generate usage data for the configured period
    usage_data = generate_usage_data(
        metadata, 
        USAGE_START_DATE, 
        USAGE_END_DATE, 
        bot_names, 
        people_names
    )
    print(f"Generated {len(usage_data)} usage data entries")
    
    # Block 5: Store in SQLite
    store_in_sqlite(usage_data, DATABASE_FILE)

if __name__ == "__main__":
    main()
```

---

### Additional Features

1. **Test Suite**:
   - Create comprehensive unit tests for each functional block
   - Use Python's unittest module
   - Test each function in isolation
   - Include test cases for edge conditions

2. **Documentation**:
   - Create a detailed README.md file
   - Document the database schema, including the new document_type and document_format fields
   - Provide usage examples for the query tool
   - Explain configuration options

3. **Performance Optimizations**:
   - Use batch inserts for database operations
   - Implement chunking for large datasets
   - Use list comprehensions for efficient data processing
   - Add proper error handling for robustness

---

### Additional Notes

- **Reproducibility**: Add `random.seed(42)` at the start of the script for consistent output.
- **Error Handling**: Include try-except blocks around SQLite operations and other I/O operations to handle potential errors.
- **Scalability**: Process usage data in chunks to manage memory usage with large datasets.
- **Date Consistency**: Use `datetime.date` objects throughout and only convert to strings when needed for SQLite.
- **Modularity**: Organize the code in a modular way to allow for reuse and testing.
- **Configuration**: Use a centralized configuration file to make the program easily customizable.
- **Database Location**: Store the database in a dedicated /database directory to keep the project organized.
- **Command-line Interface**: Provide a robust CLI for querying the database with multiple query types and filtering options.

---