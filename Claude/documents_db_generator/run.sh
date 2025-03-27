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

# Define database path directly in the script
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
# Get a sample document for detailed view
echo "5. Detailed information for a specific document type (Agenda):"
python3 src/query_usage_db.py --db "$DB_PATH" --query type_summary --type "Agenda"

echo
echo "Done!"