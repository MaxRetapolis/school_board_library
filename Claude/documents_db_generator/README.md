# School Board Documents Usage Database Generator

This Python application generates a simulated SQLite database containing usage statistics for various school board meeting documents over a 3-month period. The database includes both meeting-related and non-meeting documents, each with associated metadata and usage data from bots and people.

## Features

- Generates bi-weekly meeting dates over a specified period
- Creates metadata for meeting-related documents (agendas, minutes) and non-meeting documents
- Simulates usage statistics from both bot and human users
- Stores all data in an SQLite database
- Uses an atomic and composable architecture for modularity and reusability
- Includes a query tool for analyzing the generated data

## Architecture

The program is designed with an atomic and composable architecture, where each functional block is implemented as a separate, reusable Python function:

1. **Generate Meeting Dates**: Creates bi-weekly meeting dates for a specified period
2. **Generate Document Metadata**: Produces metadata for meeting-related and non-meeting documents
3. **Generate Pool of Bots and People**: Creates lists of bot and people names as usage sources
4. **Generate Usage Data**: Simulates daily usage statistics for each document
5. **Store Data in SQLite**: Saves the usage data into an SQLite database

## Requirements

- Python 3.x
- No external dependencies (uses only standard libraries: `datetime`, `random`, `sqlite3`, `argparse`)

## Usage

### Generating the Database

```bash
# Clone the repository
git clone <repository-url>
cd school-board-documents-db-generator

# Run the generator
python src/usage_db_generator.py
```

The program will generate an SQLite database file named `usage.db` in the current directory.

### Querying the Database

```bash
# Get top 10 documents by total hits
python src/query_usage_db.py --query top_documents

# Get daily summary of hits
python src/query_usage_db.py --query daily_summary

# Get detailed information for a specific document
python src/query_usage_db.py --query document_detail --document "Agenda_2023-01-15"

# Filter by date range
python src/query_usage_db.py --query top_documents --start-date 2023-08-01 --end-date 2023-08-31
```

## Database Schema

The generated database contains a single table named `usage` with the following columns:

- `document_name` (TEXT): Name of the document
- `date` (TEXT): Date of usage in YYYY-MM-DD format
- `bot_hits` (INTEGER): Number of hits from bots
- `people_hits` (INTEGER): Number of hits from people
- `total_hits` (INTEGER): Total number of hits (bot_hits + people_hits)

## Customization

You can modify the following parameters in the `main()` function:

- Date ranges for meetings and usage data
- Document types and formats
- Number of bots and people
- Number of non-meeting documents

## License

This project is licensed under the MIT License - see the LICENSE file for details.