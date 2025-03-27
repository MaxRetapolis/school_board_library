#!/usr/bin/env python3
"""
Database Usage Generator for School Board Documents

This script generates a simulated usage database for school board meeting documents,
containing usage statistics over a 3-month period. The database includes both meeting
and non-meeting documents with associated usage data from bots and people.

The program follows an atomic and composable architecture with clearly defined,
reusable functional blocks.
"""

from datetime import date, timedelta
import random
import sqlite3

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
        A list of tuples: (document_name, date, bot_hits, people_hits, total_hits)
    """
    usage_data = []
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)
    
    for _, _, doc_name, _ in document_metadata:
        for date in date_list:
            num_bots = random.randint(0, min(5, len(bot_names)))
            num_people = random.randint(0, min(10, len(people_names)))
            bots = random.sample(bot_names, num_bots)
            people = random.sample(people_names, num_people)
            bot_hits = sum(random.randint(1, 50) for _ in bots)
            people_hits = sum(random.randint(1, 50) for _ in people)
            total_hits = bot_hits + people_hits
            usage_data.append((doc_name, date, bot_hits, people_hits, total_hits))
    
    return usage_data

def store_in_sqlite(usage_data, db_name="usage.db"):
    """
    Store usage data in an SQLite database.
    
    Args:
        usage_data: A list of (document_name, date, bot_hits, people_hits, total_hits) tuples
        db_name: A string for the database file name
        
    Returns:
        None (creates an SQLite database file)
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            document_name TEXT,
            date TEXT,
            bot_hits INTEGER,
            people_hits INTEGER,
            total_hits INTEGER
        )
    """)
    
    # Convert dates to string format for SQLite
    formatted_data = [
        (name, date.strftime('%Y-%m-%d'), b_hits, p_hits, t_hits)
        for name, date, b_hits, p_hits, t_hits in usage_data
    ]
    
    # Batch inserts for better performance
    chunk_size = 1000
    for i in range(0, len(formatted_data), chunk_size):
        chunk = formatted_data[i:i + chunk_size]
        cursor.executemany("""
            INSERT INTO usage (document_name, date, bot_hits, people_hits, total_hits)
            VALUES (?, ?, ?, ?, ?)
        """, chunk)
    
    conn.commit()
    conn.close()
    print(f"Database '{db_name}' created successfully.")

def main():
    """
    Main function to execute all blocks in sequence.
    """
    # Set random seed for reproducibility (optional)
    random.seed(42)
    
    # Block 1: Generate meeting dates
    start_date = date(2022, 10, 1)
    end_date = date(2023, 10, 1)
    meeting_dates = generate_meeting_dates(start_date, end_date, 14)
    print(f"Generated {len(meeting_dates)} meeting dates")
    
    # Block 2: Generate document metadata
    doc_types = ["Meeting Minutes", "Agenda", "Report", "Presentation", "Budget", "Newsletter"]
    formats = ["PDF", "Audio", "Video", "Text"]
    metadata = generate_document_metadata(meeting_dates, doc_types, formats, num_non_meeting=20)
    print(f"Generated metadata for {len(metadata)} documents")
    
    # Block 3: Generate bots and people
    bot_names, people_names = generate_bots_and_people(num_bots=10, num_people=100)
    print(f"Generated {len(bot_names)} bots and {len(people_names)} people")
    
    # Block 4: Generate usage data (3-month period)
    usage_start = date(2023, 7, 1)
    usage_end = date(2023, 10, 1)
    usage_data = generate_usage_data(metadata, usage_start, usage_end, bot_names, people_names)
    print(f"Generated {len(usage_data)} usage data entries")
    
    # Block 5: Store in SQLite
    store_in_sqlite(usage_data, "usage.db")

if __name__ == "__main__":
    main()