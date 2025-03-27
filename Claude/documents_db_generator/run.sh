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

# Run the usage database generator
echo "Generating usage database..."
python3 src/usage_db_generator.py

# Check if database was created successfully
if [ ! -f "usage.db" ]; then
    echo "Error: Failed to create usage.db"
    exit 1
fi

echo
echo "Database generated successfully at usage.db"
echo

# Run some example queries
echo "Running example queries..."
echo

echo "1. Top 10 documents by total hits:"
python3 src/query_usage_db.py --query top_documents

echo
echo "2. Daily summary for August 2023:"
python3 src/query_usage_db.py --query daily_summary --start-date 2023-08-01 --end-date 2023-08-31

echo
echo "Done!"