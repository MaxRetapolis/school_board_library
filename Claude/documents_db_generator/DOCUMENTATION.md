# School Board Documents Usage Database Generator - Documentation

## Overview

This application generates a simulated SQLite database containing usage statistics for school board meeting documents over a three-month period. The database includes metadata for meeting-related documents (agendas, minutes) and non-meeting documents (reports, presentations), along with simulated daily usage data from both bots and human users.

The implementation follows an atomic and composable architecture, where each functional component is implemented as a separate, reusable Python function with clear inputs and outputs.

## Architecture

### Core Components

1. **Usage DB Generator (`src/usage_db_generator.py`)**
   - Main module that implements the core database generation functionality
   - Contains atomic functions for each stage of the generation process
   - Includes a runnable `main()` function that executes all components in sequence

2. **Query Tool (`src/query_usage_db.py`)**
   - Command-line tool for querying the generated database
   - Provides various query types: top documents, daily summaries, document details
   - Supports filtering by date range and document name

3. **Tests (`tests/test_usage_db_generator.py`)**
   - Unit tests for all core functions in the generator module
   - Ensures each component works as expected in isolation

4. **Run Script (`run.sh`)**
   - Shell script to run the entire process: generate database and run example queries
   - Provides a simple way to demonstrate the functionality

### Functional Blocks

The application is divided into five main functional blocks, each implemented as a separate function:

#### 1. Generate Meeting Dates

**Function**: `generate_meeting_dates(start_date, end_date, frequency_days)`

**Purpose**: Creates a list of meeting dates at specified intervals

**Implementation**:
- Takes start date, end date, and frequency (in days) as input
- Uses a while loop to increment the date by the frequency until it exceeds the end date
- Returns a list of datetime.date objects representing the meeting dates

#### 2. Generate Document Metadata

**Function**: `generate_document_metadata(meeting_dates, document_types, formats, num_non_meeting=20)`

**Purpose**: Creates metadata for both meeting-related and non-meeting documents

**Implementation**:
- For meeting dates, generates entries for meeting-related document types (agendas, minutes)
- Randomly generates additional non-meeting documents within the date range
- Returns a list of tuples: `(document_type, format, document_name, document_date)`

#### 3. Generate Pool of Bots and People

**Function**: `generate_bots_and_people(num_bots=10, num_people=100)`

**Purpose**: Creates static pools of bot and people names for usage simulation

**Implementation**:
- Generates simple bot names ("Bot1", "Bot2", etc.)
- Creates people names by combining random first and last names
- Returns a tuple of two lists: bot_names and people_names

#### 4. Generate Usage Data

**Function**: `generate_usage_data(document_metadata, start_date, end_date, bot_names, people_names)`

**Purpose**: Simulates daily usage statistics for each document

**Implementation**:
- For each document and date combination in the specified range:
  - Randomly selects a subset of bots and people who accessed the document
  - Generates random hit counts for each bot and person
  - Computes total hits (bot_hits + people_hits)
- Returns a list of tuples: `(document_name, date, bot_hits, people_hits, total_hits)`

#### 5. Store Data in SQLite

**Function**: `store_in_sqlite(usage_data, db_name="usage.db")`

**Purpose**: Stores the usage data in an SQLite database

**Implementation**:
- Creates an SQLite database with a table named "usage"
- Uses batch inserts for better performance
- Formats dates as strings in YYYY-MM-DD format for SQLite compatibility

## Database Schema

The generated database contains a single table named `usage` with the following columns:

- `document_name` (TEXT): Name of the document (e.g., "Agenda_2023-01-15")
- `date` (TEXT): Date of usage in YYYY-MM-DD format
- `bot_hits` (INTEGER): Number of hits from bots
- `people_hits` (INTEGER): Number of hits from people
- `total_hits` (INTEGER): Total number of hits (bot_hits + people_hits)

## Query Tool

The query tool (`src/query_usage_db.py`) provides a command-line interface to analyze the generated data. It supports three main query types:

### 1. Top Documents

**Query**: `--query top_documents`

**Purpose**: Lists the top 10 documents by total hits

**Output**: Document names and their total hit counts, sorted in descending order

### 2. Daily Summary

**Query**: `--query daily_summary`

**Purpose**: Provides a daily summary of hits across all documents

**Output**: Date, total bot hits, total people hits, and total hits for each day

### 3. Document Detail

**Query**: `--query document_detail --document <document_name>`

**Purpose**: Shows detailed usage statistics for a specific document

**Output**:
- Daily breakdown of bot hits, people hits, and total hits
- Summary statistics (total days, total hits by type, average daily hits)

All queries support optional date filtering using `--start-date` and `--end-date` parameters.

## Customization

The database generation can be customized by modifying parameters in the `main()` function:

- **Date Ranges**: Change the start and end dates for meetings or usage data
- **Document Types**: Add or remove document types (e.g., "Meeting Minutes", "Agenda", "Report")
- **Formats**: Add or remove document formats (e.g., "PDF", "Audio", "Video")
- **Volume**: Adjust the number of bots, people, or non-meeting documents

## Performance Considerations

The implementation includes several optimizations for better performance:

- **Batch Inserts**: Uses `executemany` for batch database inserts
- **List Comprehensions**: Uses efficient list comprehensions where appropriate
- **Sample vs. Choice**: Uses `random.sample` instead of multiple `random.choice` calls to avoid duplicates
- **Chunking**: Processes large datasets in chunks to manage memory usage

## Reproducibility

For consistent output across runs, you can uncomment the `random.seed(42)` line in the `main()` function. This will ensure that the random number generator produces the same sequence of values each time the script is run.