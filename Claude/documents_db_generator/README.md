# School Board Documents Usage Database Generator

This Python application generates a simulated SQLite database containing usage statistics for various school board meeting documents over a 3-month period. The database includes both meeting-related and non-meeting documents, each with associated metadata and usage data from bots and people.

## Features

- Generates bi-weekly meeting dates over a specified period
- Creates metadata for meeting-related documents (agendas, minutes) and non-meeting documents
- Simulates usage statistics from both bot and human users
- Stores all data in an SQLite database in a dedicated `/database` directory
- Uses an atomic and composable architecture for modularity and reusability
- Includes a query tool for analyzing the generated data
- Centralized configuration system for easy customization

## Architecture

The program is designed with an atomic and composable architecture, where each functional block is implemented as a separate, reusable Python function:

1. **Generate Meeting Dates**: Creates bi-weekly meeting dates for a specified period
2. **Generate Document Metadata**: Produces metadata for meeting-related and non-meeting documents
3. **Generate Pool of Bots and People**: Creates lists of bot and people names as usage sources
4. **Generate Usage Data**: Simulates daily usage statistics for each document
5. **Store Data in SQLite**: Saves the usage data into an SQLite database

## Requirements

- Python 3.x
- No external dependencies (uses only standard libraries: `datetime`, `random`, `sqlite3`, `argparse`, `os`, `sys`)

## Installation & Setup

```bash
# Clone the repository
git clone <repository-url>
cd school-board-documents-db-generator

# Run all in one step with the provided script
./run.sh
```

The script will:
1. Create a `/database` directory if it doesn't exist
2. Generate the database
3. Run example queries to demonstrate functionality

## Usage

### Generating the Database

```bash
# Run the generator directly
python3 src/usage_db_generator.py
```

The program will generate an SQLite database file in the `/database` directory configured in `src/config.py`.

### Querying the Database

```bash
# Get top documents by total hits
python3 src/query_usage_db.py --query top_documents

# Get daily summary of hits
python3 src/query_usage_db.py --query daily_summary

# Get detailed information for a specific document
python3 src/query_usage_db.py --query document_detail --document "Agenda_2023-01-15"

# Get summary by document type
python3 src/query_usage_db.py --query type_summary

# Get summary by document format
python3 src/query_usage_db.py --query format_summary

# Filter by document type or format
python3 src/query_usage_db.py --query top_documents --type "Agenda"
python3 src/query_usage_db.py --query top_documents --format "PDF"

# Filter by date range
python3 src/query_usage_db.py --query top_documents --start-date 2023-08-01 --end-date 2023-08-31
```

## Database Schema

The generated database contains a single table named `usage` with the following columns:

- `document_name` (TEXT): Name of the document
- `document_type` (TEXT): Type of document (e.g., "Agenda", "Meeting Minutes")
- `document_format` (TEXT): Format of the document (e.g., "PDF", "Audio")
- `date` (TEXT): Date of usage in YYYY-MM-DD format
- `bot_hits` (INTEGER): Number of hits from bots
- `people_hits` (INTEGER): Number of hits from people
- `total_hits` (INTEGER): Total number of hits (bot_hits + people_hits)

## Configuration

All settings are centralized in the `src/config.py` file. You can customize:

- Database location
- Meeting dates range
- Usage data dates range
- Document types and formats
- Number of bots and people
- Number of non-meeting documents
- Database settings (chunk size for batch inserts)
- Query settings (default query type, limit for top documents)

## Running Tests

```bash
# Run the test suite
python3 -m unittest tests/test_usage_db_generator.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.