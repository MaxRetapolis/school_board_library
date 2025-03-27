Below is a detailed prompt designed for Claude 3.7 to generate a Python program that meets the user's requirements. The prompt includes all necessary descriptors, detailed instructions, and optimizations to ensure clarity and completeness. It is structured to be passed directly to Claude 3.7 for code generation.

---

## Prompt for Claude 3.7

**Task**: Develop a Python program that generates a simulated usage file stored as an SQLite database. The database will contain usage statistics for various school board meeting documents over a 3-month period. The documents include both meeting-related and non-meeting documents, each with associated metadata and usage data from bots and people. The program must use an atomic and composable architecture with clearly defined, reusable functional blocks.

**Requirements**:
- Implement the program using an **atomic and composable architecture**, where each functional block is a separate, reusable Python function.
- Ensure that each function is modular, with clear inputs and outputs, allowing for independent testing and reuse.
- Integrate all functional blocks into a cohesive system that produces an SQLite database as the final output.
- Use Python 3.x and standard libraries (`datetime`, `random`, `sqlite3`)—no external dependencies.
- Include optimizations for efficiency, such as batching database inserts, and ensure consistent handling of dates as `datetime.date` objects.

**Functional Blocks**:
1. **Generate Meeting Dates**: Create bi-weekly meeting dates for a specified period.
2. **Generate Document Metadata**: Produce metadata for meeting-related and non-meeting documents.
3. **Generate Pool of Bots and People**: Create lists of bot and people names as usage sources.
4. **Generate Usage Data**: Simulate daily usage statistics for each document over 3 months.
5. **Store Data in SQLite**: Save the usage data into an SQLite database.

**Instructions**:

### Block 1: Generate Meeting Dates

**Purpose**: Generate a list of bi-weekly meeting dates between two dates.

**Input**:
- `start_date`: A `datetime.date` object (e.g., `datetime.date(2022, 10, 1)`).
- `end_date`: A `datetime.date` object (e.g., `datetime.date(2023, 10, 1)`).
- `frequency_days`: An integer for the interval between meetings (e.g., 14 for bi-weekly).

**Output**:
- A list of `datetime.date` objects representing meeting dates.

**Implementation Details**:
- Use the `datetime` module’s `date` and `timedelta` classes.
- Initialize an empty list `meeting_dates`.
- Set `current_date = start_date`.
- Use a `while` loop to increment `current_date` by `frequency_days` until it exceeds `end_date`.
- Append each `current_date` to `meeting_dates`.
- Return the list.

**Example Code**:
```python
from datetime import date, timedelta

def generate_meeting_dates(start_date, end_date, frequency_days):
    meeting_dates = []
    current_date = start_date
    while current_date <= end_date:
        meeting_dates.append(current_date)
        current_date += timedelta(days=frequency_days)
    return meeting_dates
```

**Notes**:
- Ensure `start_date` and `end_date` are `datetime.date` objects to maintain consistency.

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
  - Define static lists: `first_names` (e.g., `["Alice", "Bob", "Charlie", "Dana", "Eve"]`) and `last_names` (e.g., `["Smith", "Jones", "Brown", "Taylor", "Wilson"]`).
  - Use a list comprehension to create `num_people` names by combining random `first_names` and `last_names` (e.g., `"Alice Smith"`).
- Return `(bot_names, people_names)`.

**Example Code**:
```python
import random

def generate_bots_and_people(num_bots=10, num_people=100):
    bot_names = [f"Bot{i}" for i in range(1, num_bots + 1)]
    first_names = ["Alice", "Bob", "Charlie", "Dana", "Eve"]
    last_names = ["Smith", "Jones", "Brown", "Taylor", "Wilson"]
    people_names = [f"{random.choice(first_names)} {random.choice(last_names)}" 
                    for _ in range(num_people)]
    return bot_names, people_names
```

**Notes**:
- Keep name pools simple but extensible; expand `first_names` and `last_names` if more variety is needed.

---

### Block 4: Generate Usage Data

**Purpose**: Simulate daily usage statistics for each闊

**Input**:
- `document_metadata`: A list of `(type, format, name, date)` tuples from Block 2.
- `start_date`: A `datetime.date` object (e.g., `datetime.date(2023, 7, 1)`).
- `end_date`: A `datetime.date` object (e.g., `datetime.date(2023, 10, 1)`).
- `bot_names`: A list of bot name strings from Block 3.
- `people_names`: A list of people name strings from Block 3.

**Output**:
- A list of tuples: `(document_name, date, bot_hits, people_hits, total_hits)`.

**Implementation Details**:
- Import `random` and `datetime.timedelta`.
- Generate a list `date_list` of all dates from `start_date` to `end_date` using a `while` loop and `timedelta(days=1)`.
- For each `(type, format, doc_name, doc_date)` in `document_metadata`:
  - For each `date` in `date_list`:
    - Randomly select `num_bots` (0 to min(5, len(bot_names))) using `random.randint`.
    - Randomly select `num_people` (0 to min(10, len(people_names))) using `random.randint`.
    - Select `bots = random.sample(bot_names, num_bots)` and `people = random.sample(people_names, num_people)`.
    - Compute `bot_hits = sum(random.randint(1, 50) for _ in bots)`.
    - Compute `people_hits = sum(random.randint(1, 50) for _ in people)`.
    - Compute `total_hits = bot_hits + people_hits`.
    - Append `(doc_name, date, bot_hits, people_hits, total_hits)` to `usage_data`.
- Return `usage_data`.

**Example Code**:
```python
from datetime import date, timedelta
import random

def generate_usage_data(document_metadata, start_date, end_date, bot_names, people_names):
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
```

**Optimization**:
- Use `random.sample` instead of `random.choice` to avoid duplicate selections within a day.

---

### Block 5: Store Data in SQLite

**Purpose**: Store usage data in an SQLite database.

**Input**:
- `usage_data`: A list of `(document_name, date, bot_hits, people_hits, total_hits)` tuples from Block 4.
- `db_name`: A string for the database file name (default: `"usage.db"`).

**Output**:
- An SQLite database file with a table `usage`.

**Implementation Details**:
- Import `sqlite3`.
- Connect to `db_name` using `sqlite3.connect`.
- Create a cursor object.
- Execute a `CREATE TABLE IF NOT EXISTS` statement for `usage` with columns:
  - `document_name` (TEXT)
  - `date` (TEXT)
  - `bot_hits` (INTEGER)
  - `people_hits` (INTEGER)
  - `total_hits` (INTEGER)
- Use `cursor.executemany` to insert `usage_data`, formatting dates as `'YYYY-MM-DD'`.
- Commit changes and close the connection.

**Example Code**:
```python
import sqlite3

def store_in_sqlite(usage_data, db_name="usage.db"):
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
    
    cursor.executemany("""
        INSERT INTO usage (document_name, date, bot_hits, people_hits, total_hits)
        VALUES (?, ?, ?, ?, ?)
    """, [(name, date.strftime('%Y-%m-%d'), b_hits, p_hits, t_hits)
          for name, date, b_hits, p_hits, t_hits in usage_data])
    
    conn.commit()
    conn.close()
```

**Optimization**:
- Use `executemany` for batch inserts to improve performance with large datasets.

---

### Integration

**Main Script**:
- Combine all blocks into a single executable script.
- Use example parameters to demonstrate functionality.

**Example Integration**:
```python
from datetime import date

def main():
    # Block 1: Meeting dates
    start_date = date(2022, 10, 1)
    end_date = date(2023, 10, 1)
    meeting_dates = generate_meeting_dates(start_date, end_date, 14)
    
    # Block 2: Document metadata
    doc_types = ["Meeting Minutes", "Agenda", "Report"]
    formats = ["PDF", "Audio"]
    metadata = generate_document_metadata(meeting_dates, doc_types, formats, num_non_meeting=20)
    
    # Block 3: Bots and people
    bot_names, people_names = generate_bots_and_people(num_bots=10, num_people=100)
    
    # Block 4: Usage data (3-month period)
    usage_start = date(2023, 7, 1)
    usage_end = date(2023, 10, 1)
    usage_data = generate_usage_data(metadata, usage_start, usage_end, bot_names, people_names)
    
    # Block 5: Store in SQLite
    store_in_sqlite(usage_data, "usage.db")

if __name__ == "__main__":
    main()
```

---

### Additional Notes

- **Reproducibility**: Add `random.seed(42)` at the top of the script if consistent output is desired.
- **Error Handling**: Optionally, add try-except blocks around SQLite operations to handle potential I/O errors.
- **Scalability**: For very large datasets, consider processing usage data in chunks to manage memory usage.
- **Date Consistency**: All dates must be `datetime.date` objects; convert strings if necessary using `datetime.strptime`.
- **Modularity**: Functions can be imported into other scripts by saving this as a `.py` module.

---

