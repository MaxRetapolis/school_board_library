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

# Path to the JSON file containing the list of available converted files
AVAILABLE_FILES_JSON = r"C:\school_board_library\experiments\1_prelearning\data\2_AVAILABLE_CONVERTED_FILES.JSON"

# Directory to save the extracted entities
ENTITIES_DIR = r"C:\school_board_library\experiments\1_prelearning\data\entities"
os.makedirs(ENTITIES_DIR, exist_ok=True)

# Directory to save log files
LOGS_DIR = r"C:\school_board_library\experiments\1_prelearning\data\logs"
os.makedirs(LOGS_DIR, exist_ok=True)

# Path to save the aggregated extracted entities
EXTRACTED_ENTITIES_FILE = os.path.join(ENTITIES_DIR, "extracted_entities.json")

# Number of lines per chunk
LINES_PER_CHUNK = 10  # Reduced from 20 to 10

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
    parser = argparse.ArgumentParser(description="Extract entities from school board meeting documents.")
    
    # Only keep --number_of_files and --model arguments
    parser.add_argument(
        '--number_of_files',
        choices=['1', 'all'],
        default='1',
        help="Number of files to process: '1' for a single file or 'all' to process all available files."
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
            logging.warning(f"No entries found in available files JSON: {json_path}")
            print(f"⚠️ No entries found in available files JSON: {json_path}")
        
        logging.info(f"Loaded {len(available_files)} available converted file(s).")
        print(f"✅ Loaded {len(available_files)} available converted file(s).")
        return available_files
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from '{json_path}': {e}")
        print(f"❌ Error decoding JSON from '{json_path}': {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error reading '{json_path}': {e}")
        print(f"❌ Unexpected error reading '{json_path}': {e}")
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
        
        if not os.path.isfile(converted_path):
            logging.warning(f"Converted file not found: {converted_path}. Skipping '{original_file}'.")
            print(f"⚠️ Converted file not found: {converted_path}. Skipping '{original_file}'.")
            continue
        
        valid_selected_files.append(file_info)
    
    logging.info(f"{len(valid_selected_files)} out of {len(selected_files)} selected file(s) are valid and will be processed.")
    print(f"✅ {len(valid_selected_files)} out of {len(selected_files)} selected file(s) are valid and will be processed.")
    
    return valid_selected_files

def split_text_into_chunks(file_path, lines_per_chunk):
    """
    Splits the text file into chunks of specified number of lines with overlap.
    Each new chunk starts with 2 lines from the previous chunk.
    """
    overlap = 2  # Number of overlapping lines
    chunks = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            current_chunk = []
            previous_lines = []
            for line in f:
                current_chunk.append(line.strip())
                if len(current_chunk) == lines_per_chunk:
                    # Prepend the overlapping lines from the previous chunk
                    if previous_lines:
                        chunk = '\n'.join(previous_lines + current_chunk)
                    else:
                        chunk = '\n'.join(current_chunk)
                    chunks.append(chunk)
                    # Update previous_lines to the last 2 lines of the current chunk
                    previous_lines = current_chunk[-overlap:]
                    current_chunk = []
            if current_chunk:
                if previous_lines:
                    chunk = '\n'.join(previous_lines + current_chunk)
                else:
                    chunk = '\n'.join(current_chunk)
                chunks.append(chunk)
        logging.info(f"Split '{file_path}' into {len(chunks)} chunk(s) with overlap.")
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

def parse_ollama_response(response, source_file):
    """
    Parses the Ollama response and converts it into the defined JSON structure.
    """
    try:
        data = json.loads(response)
        entities = data.get("entities", [])
        parsed_entities = []
        for entity in entities:
            entity_type = entity.get("type", "").strip()
            entity_name = entity.get("name", entity.get("value", "")).strip()
            if entity_type and entity_name:
                parsed_entities.append({"type": entity_type, "name": entity_name})
        return {"source_file": source_file, "entities": parsed_entities}
    except json.JSONDecodeError as e:
        logging.error(f"JSON decoding failed: {e}")
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

def extract_entities(selected_files):
    """
    Extracts entities from the selected documents.
    """
    all_entities = []
    total_lines_processed = 0  # Initialize line counter
    
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
        
        if os.path.isfile(entities_file):
            logging.info(f"Entities already extracted for '{original_file}'. Skipping (use --overwrite to reprocess).")
            print(f"ℹ️ Entities already extracted for '{original_file}'. Skipping (use --overwrite to reprocess).")
            continue
        
        # Split the document into chunks
        chunks = split_text_into_chunks(processed_file, LINES_PER_CHUNK)
        
        if not chunks:
            logging.warning(f"No chunks created for '{original_file}'. Skipping this file.")
            print(f"⚠️ No chunks created for '{original_file}'. Skipping this file.")
            continue
        
        logging.info(f"Split '{processed_file}' into {len(chunks)} chunk(s).")
        print(f"✅ Split '{processed_file}' into {len(chunks)} chunk(s).")
        
        document_entities = []
        
        for idx, chunk in enumerate(chunks, start=1):
            logging.info(f"🔄 Processing Chunk {idx}/{len(chunks)} of '{original_file}'")
            print(f"🔄 Processing Chunk {idx}/{len(chunks)} of '{original_file}'")
            
            # Clean the chunk to remove problematic characters
            cleaned_chunk = clean_text(chunk)
            
            # Update lines processed
            lines_in_chunk = len(chunk.split('\n'))
            total_lines_processed += lines_in_chunk
            
            # Prepare the prompt with cleaned text
            prompt = (PROMPT_TEMPLATE.replace("<source_file>", os.path.basename(processed_file)) +
                      "\n\nText to analyze:\n\n" + cleaned_chunk)
            logging.info(f"Ollama API prompt for Chunk {idx}: {prompt}")  # Log the full prompt sent
            
            # Call Ollama API
            response = call_ollama(prompt)
            if response:
                # Log the full API response
                logging.info(f"Ollama API response for Chunk {idx}: {response}")
                
                entities = parse_ollama_response(response, os.path.basename(processed_file))
                if entities["entities"]:
                    # Filter out seed entities
                    filtered_entities = [
                        entity for entity in entities["entities"]
                        if entity["type"] not in SEED_ENTITY_TYPES
                    ]
                    document_entities.extend(filtered_entities)
                    logging.info(f"✅ Extracted {len(filtered_entities)} entities from Chunk {idx}.")
                    print(f"✅ Extracted {len(filtered_entities)} entities from Chunk {idx}.")
                    # Print the list of extracted entities
                    entity_names = [entity.get("name", "") for entity in filtered_entities]
                    print(f"Entities: {entity_names}")
                else:
                    logging.warning(f"No entities found in response for Chunk {idx} of '{original_file}'.")
                    print(f"⚠️ No entities found in response for Chunk {idx} of '{original_file}'.")
            else:
                logging.error(f"❌ No response received from Ollama for Chunk {idx} of '{original_file}'.")
                print(f"❌ No response received from Ollama for Chunk {idx} of '{original_file}'.")
        
        if not document_entities:
            logging.warning(f"No entities extracted for '{original_file}'.")
            print(f"⚠️ No entities extracted for '{original_file}'.")
            continue
        
        # Remove duplicate entities within the document
        unique_entities = []
        seen = set()
        for entity in document_entities:
            entity_type = entity.get("type", "").strip()
            entity_name = entity.get("name", "").strip()
            if not entity_type or not entity_name:
                continue
            entity_tuple = (entity_type, entity_name)
            if entity_tuple not in seen:
                seen.add(entity_tuple)
                unique_entities.append(entity)
        
        if not unique_entities:
            logging.warning(f"No unique entities found for '{original_file}'.")
            print(f"⚠️ No unique entities found for '{original_file}'.")
            continue
        
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
    
    return all_entities, total_lines_processed  # Return lines processed

def aggregate_all_entities(all_entities):
    """
    Aggregates all entities into a single JSON file.
    """
    try:
        with open(EXTRACTED_ENTITIES_FILE, 'w', encoding='utf-8') as f:
            json.dump({"entities": all_entities}, f, indent=4)
        logging.info(f"📄 Successfully aggregated and saved {len(all_entities)} entities to '{EXTRACTED_ENTITIES_FILE}'.")
        print(f"📄 Successfully aggregated and saved {len(all_entities)} entities to '{EXTRACTED_ENTITIES_FILE}'.")
    except Exception as e:
        logging.error(f"❌ Failed to write aggregated entities to '{EXTRACTED_ENTITIES_FILE}': {e}")
        print(f"❌ Failed to write aggregated entities to '{EXTRACTED_ENTITIES_FILE}': {e}")

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
    
    # Extract entities from the selected files
    all_entities, total_lines = extract_entities(files_to_process)  # Removed overwrite parameter
    
    # Aggregate all entities into a single JSON file
    aggregated_entities = []
    try:
        for entity_file in os.listdir(ENTITIES_DIR):
            if entity_file.startswith("entities-") and entity_file.endswith(".json"):
                with open(os.path.join(ENTITIES_DIR, entity_file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "entities" in data and isinstance(data["entities"], list):
                        aggregated_entities.extend(data["entities"])
    except Exception as e:
        logging.error(f"❌ Failed to aggregate entities: {e}")
        print(f"❌ Failed to aggregate entities: {e}")
        
    # Call the aggregate_all_entities function directly
    aggregate_all_entities(aggregated_entities)
    
    # End benchmarking
    end_time = datetime.now()
    duration = end_time - start_time
    time_per_line = duration.total_seconds() / total_lines if total_lines > 0 else 0
    
    # Create benchmark file
    benchmark_filename = os.path.join(
        LOGS_DIR,        f"benchmark_{sanitize_filename(OLLAMA_MODEL)}_{end_time.strftime('%Y%m%d_%H%M%S')}.txt"  # Changed extension to .txt and added timestamp after model name
    )
    try:
        with open(benchmark_filename, 'w', encoding='utf-8') as bf:
            bf.write(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            bf.write(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            bf.write(f"Number of Lines Processed: {total_lines}\n")
            bf.write(f"Time per Line (seconds): {time_per_line:.6f}\n")
            bf.write(f"Model Used: {OLLAMA_MODEL}\n")
        logging.info(f"📄 Benchmark data saved to '{benchmark_filename}'.")
        print(f"📄 Benchmark data saved to '{benchmark_filename}'.")
    except Exception as e:
        logging.error(f"❌ Failed to write benchmark data to '{benchmark_filename}': {e}")
        print(f"❌ Failed to write benchmark data to '{benchmark_filename}': {e}")

if __name__ == "__main__":
    main()