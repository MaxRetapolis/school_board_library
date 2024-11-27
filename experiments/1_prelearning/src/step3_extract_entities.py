import os
import sys
import json
import subprocess
import argparse
import logging
from pathlib import Path
from datetime import datetime
import time  # Add import for timing

# =======================
# Configuration Section
# =======================

# Correct the path to the JSON file to match the actual filename
AVAILABLE_FILES_JSON = r"C:\school_board_library\experiments\1_prelearning\data\2_available_converted_files.json"

# Directory to save the extracted entities
ENTITIES_DIR = r"C:\school_board_library\experiments\1_prelearning\data\entities"
os.makedirs(ENTITIES_DIR, exist_ok=True)

# Directory to save log files
LOGS_DIR = r"C:\school_board_library\experiments\1_prelearning\data\logs"
os.makedirs(LOGS_DIR, exist_ok=True)

# Path to save the aggregated extracted entities
EXTRACTED_ENTITIES_FILE = os.path.join(ENTITIES_DIR, "extracted_entities.json")

# Number of lines per chunk
LINES_PER_CHUNK = 20  # Changed from 10 to 20

# Number of characters per chunk
CHARS_PER_CHUNK = 1500  # Changed from 2500 to 1500 characters

# Overlap size in characters
OVERLAP_CHARS = 300  # Overlap decreased from 400 to 300 characters

# =======================
# Logging Configuration
# =======================

# Generate a timestamp for the log filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = os.path.join(LOGS_DIR, f'entity_extraction_{timestamp}.log')

# Configure logging to create a new log file each run with timestamp
logging.basicConfig(
    filename=log_filename,
    filemode='w',  # 'w' to overwrite each time
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# =======================
# Prompt and Entity Structure
# =======================

# Read the full content of 'prompt_entities.txt' and update PROMPT_TEMPLATE
def load_prompt_template(prompt_file_path):
    """
    Loads the prompt template from the specified file.
    """
    try:
        with open(prompt_file_path, 'r', encoding='utf-8') as prompt_file:
            prompt_content = prompt_file.read()
        return prompt_content
    except Exception as e:
        logging.error(f"Failed to load prompt template from '{prompt_file_path}': {e}")
        print(f"❌ Failed to load prompt template from '{prompt_file_path}': {e}")
        sys.exit(1)

# Set the path to 'prompt_entities.txt'
PROMPT_TEMPLATE_FILE = r"C:\school_board_library\experiments\1_prelearning\data\prompts\prompt_entities.txt"

# Load the prompt content
prompt_content = load_prompt_template(PROMPT_TEMPLATE_FILE)

# Remove the following lines to eliminate the JSON output instruction and fix the unterminated string:

# PROMPT_TEMPLATE = f"""{prompt_content}
# 
# At the end, please provide the extracted entities in the following JSON format:
# 
# {
#   "source_file": "<source_file>",
#   "entities": [
#     {"type": "<entity_type>", "name": "<entity_name>"},
#         {
#             "type": "Role",
#             "name": ""
#         },
#         {
#             "type": "Location",
#             "name": ""
#         },
#         {
#             "type": "Meeting Type",
#             "name": ""
#         },
#         {
#             "type": "Decision",
#             "name": ""
#         },
#         {
#             "type": "Document Type",
#             "name": ""
#         },
#         {
#             "type": "Vote Type",
#             "name": ""
#         },
#         {
#             "type": "Meeting Presence",
#             "name": ""
#         },
#         # Additional entities can be dynamically added here
#     ]
# }
# 
# """

# Replace with:

PROMPT_TEMPLATE = prompt_content

# =======================
# Utility Functions
# =======================

def parse_arguments():
    """
    Parses command-line arguments.
    """
    import argparse  # Ensure argparse is imported
    
    def positive_int_or_all(value):
        if value.lower() == 'all':
            return 'all'
        try:
            ivalue = int(value)
            if ivalue < 1:
                raise argparse.ArgumentTypeError("Number must be a positive integer or 'all'.")
            return ivalue
        except ValueError:
            raise argparse.ArgumentTypeError("Number must be a positive integer or 'all'.")
    
    parser = argparse.ArgumentParser(description="Extract entities from school board meeting documents.")
    
    # Updated --number_of_files argument to accept integers and 'all'
    parser.add_argument(
        '--number_of_files',
        type=positive_int_or_all,
        default=1,
        help="Number of files to process: specify a positive integer (e.g., '5') or 'all' to process all available files."
    )
    
    parser.add_argument(
        '--model',
        choices=['small', 'large'],
        default='small',
        help="Model size: 'small' for 1b model or 'large' for the latest model."
    )
    
    return parser.parse_args()

def load_available_files(json_path):
    """
    Loads the list of available converted files from the specified JSON.
    """
    if not os.path.isfile(json_path):
        logging.error(f"Available files JSON not found: {json_path}")
        print(f"❌ Available files JSON not found: {json_path}")
        sys.exit(1)
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            available_files = json.load(f)
        
        if not isinstance(available_files, list):
            logging.error(f"Available files JSON is not a list: {json_path}")
            print(f"❌ Available files JSON is not a list: {json_path}")
            sys.exit(1)
        
        if not available_files:
            logging.warning(f"No available files found in '{json_path}'. Exiting.")
            sys.exit(1)
        
        logging.info(f"Loaded {len(available_files)} available file(s) from '{json_path}'.")
        print(f"✅ Loaded {len(available_files)} available file(s) from '{json_path}'.")
        
        return available_files
    except Exception as e:
        logging.error(f"Failed to load available files from '{json_path}': {e}")
        print(f"❌ Failed to load available files from '{json_path}': {e}")
        sys.exit(1)

def select_files_to_process(available_files, num_files, process_all):
    """
    Selects the files to process based on the provided parameters.
    """
    if process_all:
        selected_files = available_files
        logging.info("Selected to process all available files.")
        print("✅ Selected to process all available files.")
    else:
        selected_files = available_files[:num_files]
        logging.info(f"Selected the first {num_files} file(s) to process.")
        print(f"✅ Selected the first {num_files} file(s) to process.")
    
    # Verify that each selected file exists
    valid_selected_files = []
    for file_info in selected_files:
        converted_path = file_info.get("converted_file_path")
        original_file = file_info.get("original_file_name", "Unknown File")
        
        if not converted_path:
            logging.warning(f"'converted_file_path' missing for '{original_file}'. Skipping this file.")
            print(f"⚠️ 'converted_file_path' missing for '{original_file}'. Skipping this file.")
            continue
        
        # Normalize the path to handle backslashes correctly
        normalized_path = os.path.normpath(converted_path)
        
        if not os.path.isfile(normalized_path):
            logging.warning(f"Converted file not found: {normalized_path}. Skipping '{original_file}'.")
            print(f"⚠️ Converted file not found: {normalized_path}. Skipping '{original_file}'.")
            continue
        
        valid_selected_files.append({
            "original_file_name": original_file,
            "converted_file_path": normalized_path
        })
    
    logging.info(f"{len(valid_selected_files)} out of {len(selected_files)} selected file(s) are valid and will be processed.")
    print(f"✅ {len(valid_selected_files)} out of {len(selected_files)} selected file(s) are valid and will be processed.")
    
    return valid_selected_files

def split_text_into_chunks(file_path, chars_per_chunk=CHARS_PER_CHUNK, overlap_chars=OVERLAP_CHARS):
    """
    Splits the text file into chunks of specified number of characters with overlap.
    Each chunk starts and ends on a complete word.
    """
    import string

    punctuation = set(string.punctuation)
    chunks = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        start = 0
        text_length = len(text)
        
        while (start < text_length):
            end = start + chars_per_chunk
            if end >= text_length:
                chunk = text[start:].strip()
                chunks.append((chunk, start, text_length))
                break
            else:
                # Move 'end' back to the last space or punctuation to avoid splitting words
                while end > start and text[end] not in punctuation and text[end] != ' ':
                    end -= 1
                if end == start:
                    # If no space or punctuation found, extend to the next space
                    end = text.find(' ', start + chars_per_chunk)
                    if end == -1:
                        end = text_length
                chunk = text[start:end].strip()
                chunks.append((chunk, start, end))
                
                # Determine the new start with overlap
                overlap_start = end - overlap_chars
                # Ensure overlap_start does not split a word
                while overlap_start > start and text[overlap_start] not in punctuation and text[overlap_start] != ' ':
                    overlap_start -= 1
                if overlap_start <= start:
                    overlap_start = end  # No valid overlap found, move to the end
                start = overlap_start
        logging.info(f"Split '{file_path}' into {len(chunks)} chunk(s) based on characters with overlap on word boundaries.")
        return chunks
    except Exception as e:
        logging.error(f"Error reading file '{file_path}': {e}")
        print(f"❌ Error reading file '{file_path}': {e}")
        return chunks  # Return whatever chunks were created before the error

# Define OLLAMA_MODEL globally
OLLAMA_MODEL = "llama3.2:1b"

def call_ollama(prompt):
    """
    Sends the prompt to Ollama and returns the response.
    """
    try:
        result = subprocess.run(
            ['ollama', 'run', OLLAMA_MODEL],
            input=prompt,
            text=True,
            capture_output=True,
            encoding='utf-8',  # Ensure UTF-8 encoding
            errors='replace',  # Replace undecodable characters
            check=True
        )
        if result.stdout:
            return result.stdout.strip()
        else:
            logging.error("Ollama returned no output.")
            return ""
    except subprocess.CalledProcessError as e:
        logging.error(f"Ollama command failed: {e.stderr}")
        print(f"❌ Ollama command failed: {e.stderr}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error during Ollama command: {e}")
        print(f"❌ Unexpected error during Ollama command: {e}")
        return None

def process_model_output(response, document_name, chunk_number):
    """
    Processes the raw model output and adds Document Name and Chunk Number.
    Converts it into a structured JSON format.
    Ensures that all attributes are captured without loss.
    """
    try:
        # Initialize the final entities list
        entities = []

        # Split the response into sections based on headings
        sections = re.split(r'\*\*([A-Za-z\s]+)\*\*', response)
        current_section = None

        for i in range(1, len(sections), 2):
            current_section = sections[i].strip()
            content = sections[i + 1].strip()
            
            # Split the content into individual entities
            entity_blocks = re.split(r'\n\d+\.', content)
            for block in entity_blocks:
                if block.strip() == '':
                    continue
                # Extract entity details using regex
                matches = re.findall(r'\* (.+?): (.+)', block)
                entity = {}
                for match in matches:
                    key, value = match
                    entity[key.strip()] = value.strip()
                # Assign the section as the entity type if not already set
                if current_section and 'type' not in entity:
                    entity['type'] = current_section
                if 'Event Name' in entity:
                    entity['name'] = entity.pop('Event Name')
                # Add Document Name and Chunk Number
                entity['Document Name'] = document_name
                entity['Chunk Number'] = chunk_number
                entities.append(entity)
        
        return {"entities": entities}
    except Exception as e:
        logging.error(f"Failed to process model output: {e}")
        return {"entities": []}

def parse_ollama_response(response, source_file, chunk_number):
    """
    Parses the Ollama response and converts it into the defined JSON structure.
    Utilizes the process_model_output function to handle non-JSON responses.
    """
    try:
        processed_data = process_model_output(response, source_file, chunk_number)
        entities = processed_data.get("entities", [])
        parsed_entities = []
        for entity in entities:
            entity_type = entity.get("type", "").strip()
            entity_name = entity.get("name", "").strip()
            if entity_type and entity_name:
                parsed_entities.append({"type": entity_type, "name": entity_name})
        # Log the parsed entities as JSON
        logging.info(f"Parsed Entities for Source '{source_file}': {json.dumps(parsed_entities)}")
        return {"source_file": source_file, "entities": parsed_entities}
    except Exception as e:
        logging.error(f"Error processing model output for '{source_file}': {e}")
        return {"source_file": source_file, "entities": []}

def sanitize_filename(filename):
    """
    Sanitizes the filename to create a valid JSON filename.
    """
    base_name = os.path.splitext(filename)[0]
    sanitized = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in base_name)
    return sanitized

def test_api_connectivity():
    """
    Tests the Ollama API connectivity by asking a sample question and printing the first 100 characters of the response.
    """
    test_prompt = "Who is Jason Bourne? reply in 30 words or less."
    print("🔍 Testing Ollama API connectivity...")
    try:
        # Corrected command: Removed '--prompt' and passed the prompt as a positional argument
        response = call_ollama(test_prompt)
        if response:
            print(f"✅ API Connectivity Test Successful. Response (first 100 chars): {response[:100]}")
            logging.info("API Connectivity Test Successful.")
        else:
            print("⚠️ API Connectivity Test returned an empty response.")
            logging.warning("API Connectivity Test returned an empty response.")
    except Exception as e:
        logging.error(f"Unexpected error during API connectivity test: {e}")
        print(f"❌ Unexpected error during API connectivity test: {e}")

# =======================
# Main Processing Function
# =======================

# Add a list of seed entity types to exclude
SEED_ENTITY_TYPES = [
    "Person Name",
    "Role",
    "Location",
    "Meeting Type",
    "Decision",
    "Document Type",
    "Vote Type",
    "Meeting Presence"
]

# Add a function to clean text by removing problematic characters
import re

def clean_text(text):
    """
    Cleans the input text by removing non-printable and non-ASCII characters.
    """
    # Remove non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    # Remove control characters
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    return text

import time  # Ensure time is imported for tracking chunk processing time

def extract_entities(selected_files):
    """
    Extracts entities from the selected documents.
    """
    all_entities = []
    total_chars_processed = 0  # Changed from lines to characters
    per_chunk_timings = []      # List to store timing info for each chunk
    
    for file_info in selected_files:
        processed_file = file_info.get("converted_file_path")
        
        if not processed_file or not os.path.isfile(processed_file):
            logging.warning(f"Processed file not found: {processed_file}. Skipping this file.")
            print(f"⚠️ Processed file not found: {processed_file}. Skipping this file.")
            continue
        
        original_file = file_info.get("original_file_name", os.path.basename(processed_file))
        logging.info(f"📄 Processing Document: {original_file}")
        print(f"📄 Processing Document: {original_file}")
        
        # Define a unique entities file per document with timestamp
        sanitized_name = sanitize_filename(os.path.basename(processed_file))
        entities_file = os.path.join(
            ENTITIES_DIR,
            f"entities-{sanitized_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        # Define the new entities_text file
        entities_text_file = os.path.join(
            ENTITIES_DIR,
            f"entities_text_{sanitized_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if os.path.isfile(entities_file):
            logging.info(f"Entities already extracted for '{original_file}'. Skipping (use --overwrite to reprocess).")
            print(f"ℹ️ Entities already extracted for '{original_file}'. Skipping (use --overwrite to reprocess).")
            continue
        
        # Split the document into chunks
        chunks = split_text_into_chunks(processed_file, chars_per_chunk=CHARS_PER_CHUNK, overlap_chars=OVERLAP_CHARS)
        
        if not chunks:
            logging.warning(f"No chunks created for '{original_file}'. Skipping this file.")
            print(f"⚠️ No chunks created for '{original_file}'. Skipping this file.")
            continue
        
        logging.info(f"Split '{processed_file}' into {len(chunks)} chunk(s).")
        print(f"✅ Split '{processed_file}' into {len(chunks)} chunk(s).")
        
        document_entities = []
        
        for idx, (chunk, start_char, end_char) in enumerate(chunks, start=1):
            logging.info(f"🔄 Processing Chunk {idx}/{len(chunks)} of '{original_file}'")
            print(f"🔄 Processing Chunk {idx}/{len(chunks)} of '{original_file}'")
            
            # Start timing for the chunk
            chunk_start_time = time.time()
            
            # Clean the chunk to remove problematic characters
            cleaned_chunk = clean_text(chunk)
            
            # Calculate chunk size in characters
            chunk_size = len(cleaned_chunk)
            total_chars_processed += chunk_size
            
            # Write chunk to documents_chunks folder
            document_base = sanitize_filename(os.path.splitext(original_file)[0])
            chunk_filename = f"{document_base}_chunk{idx}_{start_char}_{end_char}.txt"
            chunk_filepath = os.path.join(r"C:\school_board_library\experiments\1_prelearning\data\documents_chunks", chunk_filename)
            try:
                with open(chunk_filepath, 'w', encoding='utf-8') as chunk_file:
                    chunk_file.write(cleaned_chunk)
                logging.info(f"📄 Written chunk {idx} to '{chunk_filepath}'.")
                print(f"📄 Written chunk {idx} to '{chunk_filepath}'.")
            except Exception as e:
                logging.error(f"❌ Failed to write chunk {idx} to '{chunk_filepath}': {e}")
                print(f"❌ Failed to write chunk {idx} to '{chunk_filepath}': {e}")
            
            # Prepare the prompt with cleaned text and explicitly annotate Document Name and Chunk Details
            prompt = (
                PROMPT_TEMPLATE.replace("<source_file>", os.path.basename(processed_file)) +
                f"\n\n**Document Name:** {original_file}\n" +    # Added Document Name annotation
                f"**Chunk Number:** {idx}\n" +                   # Added Chunk Number annotation
                f"**Start Character:** {start_char}\n" +         # Added Start Character annotation
                f"**End Character:** {end_char}\n" +             # Added End Character annotation
                f"**Chunk File Name:** {chunk_filename}\n" +      # Added Chunk File Name annotation
                "\n\nText to analyze:\n\n" + cleaned_chunk
            )
            logging.info(f"Ollama API prompt for Chunk {idx}: {prompt}")  # Log the full prompt sent
            
            # Call Ollama API
            response = call_ollama(prompt)
            if response:
                # End timing for the chunk
                chunk_end_time = time.time()
                chunk_duration = chunk_end_time - chunk_start_time
                
                # Record timing information for the chunk
                time_per_char_chunk = round(chunk_duration / chunk_size, 6) if chunk_size > 0 else 0  # Calculated time per character
                per_chunk_timings.append({
                    "Chunk Number": idx,
                    "Chunk Size (chars)": chunk_size,
                    "Time Taken (seconds)": round(chunk_duration, 6),
                    "Time per Character (seconds)": time_per_char_chunk  # Added time per character
                })
                
                # Log the full API response
                logging.info(f"Ollama API response for Chunk {idx}: {response}")
                
                # Write the exact model output to the entities_text file
                try:
                    with open(entities_text_file, 'a', encoding='utf-8') as text_file:
                        text_file.write(f"---- Chunk File Name: {chunk_filename} ----\n")
                        text_file.write(f"---- Chunk {idx} ----\n")
                        text_file.write(f"---- Start Char: {start_char} ||| End Char: {end_char} ----\n")
                        text_file.write(response + "\n\n")
                    logging.info(f"📄 Written model output for Chunk {idx} to '{entities_text_file}'.")
                except Exception as e:
                    logging.error(f"❌ Failed to write model output to '{entities_text_file}': {e}")
                    print(f"❌ Failed to write model output to '{entities_text_file}': {e}")
                
                entities = parse_ollama_response(response, os.path.basename(processed_file), idx)
                if entities["entities"]:
                    # Filter out seed entities
                    filtered_entities = [
                        entity for entity in entities["entities"]
                        if entity["type"] not in SEED_ENTITY_TYPES
                    ]
                    document_entities.extend(filtered_entities)
                    logging.info(f"✅ Extracted {len(filtered_entities)} entities from Chunk {idx}.")
                    print(f"✅ Extracted {len(filtered_entities)} entities from Chunk {idx}.")
                    
                    # Extract event names
                    event_names = [entity["name"] for entity in filtered_entities if entity["type"] == "Event Name"]
                    logging.info(f"🔍 Event Names for Chunk {idx}: {event_names}")
                    print(f"🔍 Event Names: {event_names}")
                    print(f"📊 Number of Events: {len(event_names)}")
                    
                    # Print the list of extracted entities
                    entity_names = [entity.get("name", "") for entity in filtered_entities]
                    print(f"Entities: {entity_names}")
                    logging.info(f"\n\n-----------\nmodel {OLLAMA_MODEL} response\n{response}\n----------\n\n")
                else:
                    logging.warning(f"No entities found in response for Chunk {idx} of '{original_file}'.")
                    print(f"⚠️ No entities found in response for Chunk {idx} of '{original_file}'.")
        
        if not document_entities:
            logging.warning(f"No entities extracted for '{original_file}'.")
            print(f"⚠️ No entities extracted for '{original_file}'.")
            continue
        
        # Remove or comment out the deduplication code to retain all entities
        # unique_entities = []
        # seen = set()
        # for entity in document_entities:
        #     entity_type = entity.get("type", "").strip()
        #     entity_name = entity.get("name", "").strip()
        #     if not entity_type or not entity_name:
        #         continue
        #     entity_tuple = (entity_type, entity_name)
        #     if entity_tuple not in seen:
        #         seen.add(entity_tuple)
        #         unique_entities.append(entity)
        unique_entities = document_entities  # Retain all entities
        
        # Prepare the final JSON structure with source_file
        final_entities = {
            "source_file": os.path.basename(processed_file),
            "entities": unique_entities
        }
        
        # Save the extracted entities for the document
        try:
            with open(entities_file, 'w', encoding='utf-8') as f:
                json.dump(final_entities, f, indent=4)
            logging.info(f"📄 Successfully extracted and saved {len(unique_entities)} unique entities to '{entities_file}'.")
            print(f"📄 Successfully extracted and saved {len(unique_entities)} unique entities to '{entities_file}'.")
            all_entities.extend(unique_entities)
        except Exception as e:
            logging.error(f"❌ Failed to write extracted entities to '{entities_file}': {e}")
            print(f"❌ Failed to write extracted entities to '{entities_file}': {e}")
    
    return all_entities, total_chars_processed, per_chunk_timings  # Return chars processed and timings

# =======================
# Main Execution
# =======================

def main():
    """
    Main function to execute the entity extraction process.
    """
    global OLLAMA_MODEL  # Declare to modify the global variable

    # Start benchmarking
    start_time = datetime.now()
    
    # Test API connectivity before proceeding
    test_api_connectivity()
    
    args = parse_arguments()
    
    # Set OLLAMA_MODEL based on descriptive --model argument
    if args.model == 'small':
        OLLAMA_MODEL = "llama3.2:1b"
    elif args.model == 'large':
        OLLAMA_MODEL = "llama3.2:latest"
    
    print(f"Using Ollama model: {OLLAMA_MODEL}")  # Debugging statement
    
    available_files = load_available_files(AVAILABLE_FILES_JSON)
    
    if not available_files:
        logging.error("No available files to process. Exiting program.")
        print("❌ No available files to process. Exiting program.")
        sys.exit(1)
    
    # Select files to process based on --number_of_files
    if args.number_of_files == 'all':
        files_to_process = available_files
        logging.info("Selected to process all available files.")
        print("✅ Selected to process all available files.")
    else:
        selected_num = int(args.number_of_files)
        files_to_process = available_files[:selected_num]
        logging.info(f"Selected the first {selected_num} file(s) to process.")
        print(f"✅ Selected the first {selected_num} file(s) to process.")
    
    if not files_to_process:
        logging.error("No valid files selected for processing. Exiting program.")
        print("❌ No valid files selected for processing. Exiting program.")
        sys.exit(1)
    
    # Clear the documents_chunks folder before processing
    chunks_folder = r"C:\school_board_library\experiments\1_prelearning\data\documents_chunks"
    try:
        if os.path.exists(chunks_folder):
            for filename in os.listdir(chunks_folder):
                file_path = os.path.join(chunks_folder, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            logging.info(f"Cleared the documents_chunks folder: {chunks_folder}")
            print(f"✅ Cleared the documents_chunks folder: {chunks_folder}")
        else:
            os.makedirs(chunks_folder)
            logging.info(f"Created the documents_chunks folder: {chunks_folder}")
            print(f"✅ Created the documents_chunks folder: {chunks_folder}")
    except Exception as e:
        logging.error(f"❌ Failed to clear or create documents_chunks folder '{chunks_folder}': {e}")
        print(f"❌ Failed to clear or create documents_chunks folder '{chunks_folder}': {e}")
        sys.exit(1)
    
    # Extract entities from the selected files
    all_entities, total_chars, per_chunk_timings = extract_entities(files_to_process)  # Modified return values
    
    # Aggregate all entities into a single JSON file
    # aggregated_entities = []
    # try:
    #     for entity_file in os.listdir(ENTITIES_DIR):
    #         if entity_file.startswith("entities-") and entity_file.endsWith(".json"):
    #             with open(os.path.join(ENTITIES_DIR, entity_file), 'r', encoding='utf-8') as f:
    #                 data = json.load(f)
    #                 if "entities" in data and isinstance(data["entities"], list):
    #                     aggregated_entities.extend(data["entities"])
    # except Exception as e:
    #     logging.error(f"❌ Failed to aggregate entities: {e}")
    #     print(f"❌ Failed to aggregate entities: {e}")
    
    # Call the aggregate_all_entities function directly
    # aggregate_all_entities(aggregated_entities)
    
    # End benchmarking
    end_time = datetime.now()
    duration = end_time - start_time
    total_elapsed_time = duration.total_seconds()  # Added total elapsed time
    time_per_char = duration.total_seconds() / total_chars if total_chars > 0 else 0  # Changed to characters
    
    # Create benchmark file
    benchmark_filename = os.path.join(
        LOGS_DIR,        f"benchmark_{sanitize_filename(OLLAMA_MODEL)}_{end_time.strftime('%Y%m%d_%H%M%S')}.txt"  # Changed extension to .txt and added timestamp after model name
    )
    try:
        with open(benchmark_filename, 'w', encoding='utf-8') as bf:
            bf.write(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            bf.write(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            bf.write(f"Total Elapsed Time (seconds): {total_elapsed_time:.6f}\n")  # Added total elapsed time
            bf.write(f"Number of Characters Processed: {total_chars}\n")
            bf.write(f"Time per Character (seconds): {time_per_char:.6f}\n")
            bf.write(f"Model Used: {OLLAMA_MODEL}\n")
            bf.write("\nPer Chunk Timings:\n")
            bf.write("Chunk Number | Chunk Size (chars) | Time Taken (seconds) | Time per Character (seconds)\n")  # Updated header
            bf.write("-----------------------------------------------------------------------------\n")
            for timing in per_chunk_timings:
                bf.write(f"{timing['Chunk Number']} | {timing['Chunk Size (chars)']} | {timing['Time Taken (seconds)']} | {timing['Time per Character (seconds)']}\n")  # Added time per character
        logging.info(f"📄 Benchmark data saved to '{benchmark_filename}'.")
        print(f"📄 Benchmark data saved to '{benchmark_filename}'.")
    except Exception as e:
        logging.error(f"❌ Failed to write benchmark data to '{benchmark_filename}': {e}")
        print(f"❌ Failed to write benchmark data to '{benchmark_filename}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)