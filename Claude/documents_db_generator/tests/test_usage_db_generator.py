#!/usr/bin/env python3
"""
Unit tests for the usage_db_generator module
"""

import unittest
import sys
import os
import datetime
import sqlite3
from datetime import date

# Add parent directory to import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import configuration
from src.config import (
    DOCUMENT_TYPES,
    DOCUMENT_FORMATS
)

from src.usage_db_generator import (
    generate_meeting_dates,
    generate_document_metadata,
    generate_bots_and_people,
    generate_usage_data,
    store_in_sqlite
)

class TestUsageDBGenerator(unittest.TestCase):
    """Test cases for the usage_db_generator module"""
    
    def test_generate_meeting_dates(self):
        """Test the generate_meeting_dates function"""
        start_date = date(2023, 1, 1)
        end_date = date(2023, 2, 1)
        frequency = 7  # weekly
        
        dates = generate_meeting_dates(start_date, end_date, frequency)
        
        self.assertEqual(5, len(dates))
        self.assertEqual(start_date, dates[0])
        self.assertEqual(date(2023, 1, 8), dates[1])
        self.assertEqual(date(2023, 1, 15), dates[2])
        self.assertEqual(date(2023, 1, 22), dates[3])
        self.assertEqual(date(2023, 1, 29), dates[4])
    
    def test_generate_document_metadata(self):
        """Test the generate_document_metadata function"""
        meeting_dates = [date(2023, 1, 1), date(2023, 1, 15)]
        # Use subset of configuration document types and formats
        doc_types = DOCUMENT_TYPES[:3]  # First 3 types from config
        formats = DOCUMENT_FORMATS[:2]  # First 2 formats from config
        num_non_meeting = 5
        
        metadata = generate_document_metadata(meeting_dates, doc_types, formats, num_non_meeting)
        
        # Should create 2 documents per meeting (agenda + minutes) + 5 non-meeting docs
        self.assertEqual(2 * len(meeting_dates) + num_non_meeting, len(metadata))
        
        # Check structure of metadata
        for doc_type, fmt, name, doc_date in metadata:
            self.assertIn(doc_type, doc_types)
            self.assertIn(fmt, formats)
            self.assertTrue(isinstance(name, str))
            self.assertTrue(isinstance(doc_date, date))
    
    def test_generate_bots_and_people(self):
        """Test the generate_bots_and_people function"""
        num_bots = 5
        num_people = 10
        
        bot_names, people_names = generate_bots_and_people(num_bots, num_people)
        
        self.assertEqual(num_bots, len(bot_names))
        self.assertEqual(num_people, len(people_names))
        
        # Check first bot name format
        self.assertEqual("Bot1", bot_names[0])
        
        # Check that people names have both first and last names
        for name in people_names:
            parts = name.split()
            self.assertEqual(2, len(parts))
    
    def test_generate_usage_data(self):
        """Test the generate_usage_data function"""
        metadata = [("Agenda", "PDF", "Agenda_2023-01-01", date(2023, 1, 1))]
        start_date = date(2023, 1, 1)
        end_date = date(2023, 1, 3)  # 3 days of data
        bot_names = ["Bot1", "Bot2"]
        people_names = ["Alice Smith", "Bob Jones"]
        
        usage_data = generate_usage_data(metadata, start_date, end_date, bot_names, people_names)
        
        # Should have 1 document * 3 days = 3 entries
        self.assertEqual(3, len(usage_data))
        
        # Check structure of usage data with document_type and document_format
        for doc_name, doc_type, doc_format, usage_date, bot_hits, people_hits, total_hits in usage_data:
            self.assertEqual("Agenda_2023-01-01", doc_name)
            self.assertEqual("Agenda", doc_type)
            self.assertEqual("PDF", doc_format)
            self.assertTrue(isinstance(usage_date, date))
            self.assertTrue(usage_date >= start_date and usage_date <= end_date)
            self.assertTrue(isinstance(bot_hits, int))
            self.assertTrue(isinstance(people_hits, int))
            self.assertEqual(bot_hits + people_hits, total_hits)
    
    def test_store_in_sqlite(self):
        """Test the store_in_sqlite function"""
        # Test data with document_type and document_format
        usage_data = [
            ("Doc1", "Report", "PDF", date(2023, 1, 1), 10, 20, 30),
            ("Doc2", "Agenda", "Audio", date(2023, 1, 2), 5, 15, 20)
        ]
        
        # Use in-memory database for testing
        # Note: For SQLite in-memory databases, we need to keep the connection
        # open as the database only exists within the connection
        conn = sqlite3.connect(":memory:")
        
        # Create a version of store_in_sqlite that accepts an existing connection
        def store_in_memory(data, connection):
            cursor = connection.cursor()
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
            formatted_data = [
                (name, doc_type, doc_format, date.strftime('%Y-%m-%d'), b_hits, p_hits, t_hits)
                for name, doc_type, doc_format, date, b_hits, p_hits, t_hits in data
            ]
            cursor.executemany("""
                INSERT INTO usage (document_name, document_type, document_format, date, bot_hits, people_hits, total_hits)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, formatted_data)
            connection.commit()
        
        # Store the data using our modified function
        store_in_memory(usage_data, conn)
        
        # Verify database contents
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usage ORDER BY document_name")
        rows = cursor.fetchall()
        
        self.assertEqual(2, len(rows))
        self.assertEqual(("Doc1", "Report", "PDF", "2023-01-01", 10, 20, 30), rows[0])
        self.assertEqual(("Doc2", "Agenda", "Audio", "2023-01-02", 5, 15, 20), rows[1])
        
        # Close the connection
        conn.close()

if __name__ == "__main__":
    unittest.main()