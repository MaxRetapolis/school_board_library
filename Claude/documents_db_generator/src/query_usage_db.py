#!/usr/bin/env python3
"""
Query tool for the usage database

This script provides a simple command-line interface to query the usage database
generated by usage_db_generator.py.
"""

import argparse
import sqlite3
import sys
import os
from datetime import datetime

# Import configuration
# Add current directory to path to allow importing config module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import (
    DATABASE_FILE, 
    DEFAULT_QUERY_TYPE,
    TOP_DOCUMENTS_LIMIT
)

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
        
        if query_type == "top_documents":
            # Query for top documents by total hits
            query = """
                SELECT document_name, SUM(total_hits) as total
                FROM usage
            """
            params = []
            
            # Add filtering if provided
            conditions = []
            if start_date:
                conditions.append("date >= ?")
                params.append(start_date)
            if end_date:
                conditions.append("date <= ?")
                params.append(end_date)
            if doc_type:
                conditions.append("document_type = ?")
                params.append(doc_type)
            if doc_format:
                conditions.append("document_format = ?")
                params.append(doc_format)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += f"""
                GROUP BY document_name
                ORDER BY total DESC
                LIMIT {TOP_DOCUMENTS_LIMIT}
            """
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            print(f"\nTop {TOP_DOCUMENTS_LIMIT} Documents by Total Hits:")
            print("=" * 50)
            print(f"{'Document Name':<40} {'Total Hits':>10}")
            print("-" * 50)
            for doc_name, total in results:
                print(f"{doc_name:<40} {total:>10}")
            
        elif query_type == "daily_summary":
            # Query for daily summary of hits
            query = """
                SELECT date, SUM(bot_hits) as bot_total, SUM(people_hits) as people_total, 
                       SUM(total_hits) as grand_total
                FROM usage
            """
            params = []
            
            # Add filtering if provided
            conditions = []
            if start_date:
                conditions.append("date >= ?")
                params.append(start_date)
            if end_date:
                conditions.append("date <= ?")
                params.append(end_date)
            if document:
                conditions.append("document_name = ?")
                params.append(document)
            if doc_type:
                conditions.append("document_type = ?")
                params.append(doc_type)
            if doc_format:
                conditions.append("document_format = ?")
                params.append(doc_format)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += """
                GROUP BY date
                ORDER BY date
            """
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            print("\nDaily Summary of Hits:")
            print("=" * 70)
            print(f"{'Date':<12} {'Bot Hits':>15} {'People Hits':>15} {'Total Hits':>15}")
            print("-" * 70)
            for date_str, bot_total, people_total, grand_total in results:
                print(f"{date_str:<12} {bot_total:>15} {people_total:>15} {grand_total:>15}")
            
        elif query_type == "document_detail":
            # Query for detailed information about a specific document
            if not document:
                print("Error: Document name must be provided for document_detail query")
                return
                
            # Get document metadata and total hits by date
            query = """
                SELECT date, document_type, document_format, bot_hits, people_hits, total_hits
                FROM usage
                WHERE document_name = ?
            """
            params = [document]
            
            # Add filtering if provided
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
            if doc_type:
                query += " AND document_type = ?"
                params.append(doc_type)
            if doc_format:
                query += " AND document_format = ?"
                params.append(doc_format)
            
            query += " ORDER BY date"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            if not results:
                print(f"No data found for document: {document}")
                return
                
            # First row contains metadata that we'll use for header
            first_row = results[0]
            doc_type = first_row[1]
            doc_format = first_row[2]
                
            print(f"\nDetail for Document: {document}")
            print(f"Type: {doc_type}   Format: {doc_format}")
            print("=" * 80)
            print(f"{'Date':<12} {'Type':<15} {'Format':<10} {'Bot Hits':>10} {'People Hits':>12} {'Total Hits':>10}")
            print("-" * 80)
            for date_str, type_str, format_str, bot_hits, people_hits, total_hits in results:
                print(f"{date_str:<12} {type_str:<15} {format_str:<10} {bot_hits:>10} {people_hits:>12} {total_hits:>10}")
            
            # Calculate summary statistics
            cursor.execute("""
                SELECT 
                    COUNT(date) as days,
                    SUM(bot_hits) as total_bot_hits,
                    SUM(people_hits) as total_people_hits,
                    SUM(total_hits) as grand_total,
                    AVG(total_hits) as avg_daily_hits
                FROM usage
                WHERE document_name = ?
            """, [document])
            
            summary = cursor.fetchone()
            if summary:
                days, total_bot, total_people, grand_total, avg_hits = summary
                print("\nSummary Statistics:")
                print(f"Days with activity: {days}")
                print(f"Total bot hits: {total_bot}")
                print(f"Total people hits: {total_people}")
                print(f"Grand total hits: {grand_total}")
                print(f"Average daily hits: {avg_hits:.2f}")
        
        elif query_type == "type_summary":
            # Query for summary by document type
            query = """
                SELECT document_type, COUNT(DISTINCT document_name) as doc_count, 
                       SUM(bot_hits) as bot_total, SUM(people_hits) as people_total, 
                       SUM(total_hits) as grand_total
                FROM usage
            """
            params = []
            
            # Add filtering if provided
            conditions = []
            if start_date:
                conditions.append("date >= ?")
                params.append(start_date)
            if end_date:
                conditions.append("date <= ?")
                params.append(end_date)
            if document:
                conditions.append("document_name = ?")
                params.append(document)
            if doc_type:
                conditions.append("document_type = ?")
                params.append(doc_type)
            if doc_format:
                conditions.append("document_format = ?")
                params.append(doc_format)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += """
                GROUP BY document_type
                ORDER BY grand_total DESC
            """
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            print("\nSummary by Document Type:")
            print("=" * 90)
            print(f"{'Document Type':<20} {'Doc Count':>10} {'Bot Hits':>15} {'People Hits':>15} {'Total Hits':>15}")
            print("-" * 90)
            for doc_type, doc_count, bot_total, people_total, grand_total in results:
                print(f"{doc_type:<20} {doc_count:>10} {bot_total:>15} {people_total:>15} {grand_total:>15}")
                
        elif query_type == "format_summary":
            # Query for summary by document format
            query = """
                SELECT document_format, COUNT(DISTINCT document_name) as doc_count, 
                       SUM(bot_hits) as bot_total, SUM(people_hits) as people_total, 
                       SUM(total_hits) as grand_total
                FROM usage
            """
            params = []
            
            # Add filtering if provided
            conditions = []
            if start_date:
                conditions.append("date >= ?")
                params.append(start_date)
            if end_date:
                conditions.append("date <= ?")
                params.append(end_date)
            if document:
                conditions.append("document_name = ?")
                params.append(document)
            if doc_type:
                conditions.append("document_type = ?")
                params.append(doc_type)
            if doc_format:
                conditions.append("document_format = ?")
                params.append(doc_format)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += """
                GROUP BY document_format
                ORDER BY grand_total DESC
            """
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            print("\nSummary by Document Format:")
            print("=" * 90)
            print(f"{'Document Format':<20} {'Doc Count':>10} {'Bot Hits':>15} {'People Hits':>15} {'Total Hits':>15}")
            print("-" * 90)
            for doc_format, doc_count, bot_total, people_total, grand_total in results:
                print(f"{doc_format:<20} {doc_count:>10} {bot_total:>15} {people_total:>15} {grand_total:>15}")
                
        else:
            print(f"Unknown query type: {query_type}")
            
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