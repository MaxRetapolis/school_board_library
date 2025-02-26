import os
import sys
import json
import subprocess
import argparse
import logging
from pathlib import Path
from datetime import datetime
import re
import time  # Add import for timing
import tiktoken  # Add import for tiktoken

# Initialize tiktoken encoding
enc = tiktoken.get_encoding("cl100k_base")  # Use the appropriate encoding for your model

# =======================
# Configuration Section
# =======================

AVAILABLE_FILES_JSON = r"C:\school_board_library\experiments\1_prelearning\data\2_available_converted_files.json"
os.makedirs(os.path.dirname(ENTITIES_INDEX_FILE), exist_ok=True)
os.makedirs(os.path.dirname(BENCHMARKING_FILE), exist_ok=True)

# Generate a timestamp for filenames
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Update ENTITIES_INDEX_FILE to include timestamp and save in the entities folder
entities_index_filename = f"entities_index_{timestamp}.json"
ENTITIES_INDEX_FILE = os.path.join(os.path.dirname(ENTITIES_INDEX_FILE), entities_index_filename)

# Add paths for additional files
MODEL_OUTPUTS_FILE = os.path.join(os.path.dirname(ENTITIES_INDEX_FILE), f"model_outputs_index_{timestamp}.txt")
ENTITIES_INDEX_TEXT_FILE = os.path.join(os.path.dirname(ENTITIES_INDEX_FILE), f"entities_index_text_{timestamp}.txt")

# =======================
# Logging Configuration
# =======================

log_filename = f"entity_extraction_index_{timestamp}.log"  # Define log_filename

# Configure logging to file and console with detailed formatting
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(rf"C:\school_board_library\experiments\1_prelearning\data\logs\{log_filename}"),
        logging.StreamHandler(sys.stdout)
    ]
)

TOKEN_WINDOW = 128000  # Adjusted to model's maximum token limit
MAX_SEQUENCE_LENGTH = 128000  # Adjusted to model's maximum token limit
OUTBOUND_TOKEN_LIMIT = 10000  # Reserve 10,000 tokens for output

# =======================
# Load Prompt
# =======================

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
        print(f"Failed to load prompt template from '{prompt_file_path}': {e}")
        sys.exit(1)

PROMPT_TEMPLATE = load_prompt_template(PROMPT_TEMPLATE_FILE)

# =======================
# Utility Functions
# =======================

def parse_arguments():
    """
    Parses command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Extract and index entities from documents.")
    parser.add_argument(
        '--number_of_files',
        type=int,
        default=1,
        help="Number of files to process. Use a positive integer or 'all' to process all files."
    )
    # Add the --model argument
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
        print(f"Available files JSON not found: {json_path}")
        sys.exit(1)
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            available_files = json.load(f)
        
        if not isinstance(available_files, list):
            logging.error(f"Available files JSON is not a list: {json_path}")
            print(f"Available files JSON is not a list: {json_path}")
            sys.exit(1)
        
        if not available_files:
            logging.warning(f"No available files found in '{json_path}'. Exiting.")
            print("No available files found. Exiting.")
            sys.exit(1)
        
        logging.info(f"Loaded {len(available_files)} available file(s) from '{json_path}'.")
        print(f"Loaded {len(available_files)} available file(s) from '{json_path}'.")
        
        return available_files
    except Exception as e:
        logging.error(f"Failed to load available files from '{json_path}': {e}")
        print(f"Failed to load available files from '{json_path}': {e}")
        sys.exit(1)

def call_ollama(prompt, model, operation="entity_extraction"):
    """
    Sends the prompt to the model and returns the response.
    The 'operation' parameter specifies the purpose of the call (e.g., 'token_counting', 'entity_extraction').
    """
    try:
        if operation == "token_counting":
            logging.debug("Calling Ollama for token counting with model '{}'.".format(model))
            print("📊 Estimating number of tokens using model '{}'.".format(model))  # Updated print statement
        else:
            logging.debug("Calling Ollama for entity extraction with model '{}'.".format(model))
            print("🔄 Calling Ollama for entity extraction with model '{}'.".format(model))  # Existing print statement
        
        result = subprocess.run(
            ['ollama', 'run', model],
            input=prompt,
            text=True,
            capture_output=True,
            encoding='utf-8',
            errors='replace',
            check=True,
            timeout=60
        )
        
        if operation == "token_counting":
            logging.debug("Ollama responded successfully for token counting.")
            print("✅ Token count estimation received successfully.")  # Updated print statement
        else:
            logging.debug("Ollama responded successfully for entity extraction.")
            print("✅ Ollama responded successfully.")  # Existing print statement
        
        if result.stdout:
            return result.stdout.strip()
        else:
            logging.error("Ollama returned no output.")
            print("❌ Ollama returned no output.")  # Existing print statement
            return ""
    except subprocess.TimeoutExpired:
        logging.error("Ollama command timed out.")
        print("❌ Ollama command timed out.")  # Existing print statement
        return None
    except subprocess.CalledProcessError as e:
        logging.error(f"Ollama command failed: {e.stderr}")
        print(f"❌ Ollama command failed: {e.stderr}")  # Existing print statement
        return None
    except Exception as e:
        logging.error(f"Unexpected error during Ollama command: {e}")
        print(f"❌ Unexpected error during Ollama command: {e}")  # Existing print statement
        return None

def parse_ollama_response(response):
    """
    Parses the model's response and extracts entities into a structured format.
    """
    try:
        entities = []
        pattern = r'Entity ID: (\d+)\s*-\s*Entity Name: (.*?)\s*-\s*Entity Type: (.*?)\s*-\s*Description: (.*?)(?=\nEntity ID: \d+|\Z)'
        matches = re.findall(pattern, response, re.DOTALL)
        for match in matches:
            entity = {
                "Entity ID": int(match[0]),  # We'll overwrite this with a continuous ID
                "Entity Name": match[1].strip(),
                "Entity Type": match[2].strip(),
                "Description": match[3].strip()
            }
            entities.append(entity)
        return entities
    except Exception as e:
        logging.error(f"Error parsing model response: {e}")
        return []

def sanitize_filename(filename):
    """
    Sanitizes the filename to create a valid JSON filename.
    """
    base_name = os.path.splitext(filename)[0]
    sanitized = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in base_name)
    return sanitized

import re  # Ensure 're' is imported for regex operations

# Update count_tokens function to use tiktoken
def count_tokens(text, model):
    """
    Counts the number of tokens using tiktoken encoding.
    """
    try:
        encoding = enc  # Use the initialized tiktoken encoding
        token_count = len(encoding.encode(text))
        logging.debug(f"Locally counted {token_count} tokens.")
        print(f"✅ Locally counted {token_count} tokens.")
        return token_count
    except Exception as e:
        logging.error(f"Error during local token counting: {e}")
        print(f"❌ Error during local token counting: {e}")
        return 0

# Update calculate_available_tokens function to pass the model name to count_tokens
def calculate_available_tokens(prompt_text, model):  # Added 'model' parameter
    """
    Calculates the number of tokens available for chunking after accounting for the prompt and buffer.
    """
    logging.debug("Starting token count estimation for available tokens calculation.")
    print("📊 Calculating available tokens for chunking.")  # New print statement
    prompt_tokens = count_tokens(prompt_text, model)  # Pass model name
    buffer = 10000  # Reserve 10,000 tokens for output
    available_tokens = TOKEN_WINDOW - prompt_tokens - buffer
    logging.info(f"Available tokens for chunking: {available_tokens}")
    print(f"✅ Available tokens for chunking calculated: {available_tokens}")  # New print statement
    return available_tokens

# Update chunk_document function to pass the model name to count_tokens
def chunk_document(text, max_tokens, model):  # Added 'model' parameter
    """
    Splits the document text into chunks that do not exceed the max_tokens limit using tiktoken token counts.
    """
    logging.debug("Starting document chunking based on available tokens.")
    print("✂️ Chunking document based on available tokens.")  # New print statement
    chunks = []
    current_chunk = ""
    for word in text.split():
        tentative_chunk = current_chunk + " " + word
        if count_tokens(tentative_chunk, model) <= max_tokens:  # Pass model name
            current_chunk = tentative_chunk
        else:
            chunks.append(current_chunk.strip())
            current_chunk = word
    if current_chunk:
        chunks.append(current_chunk.strip())
    logging.info(f"Document split into {len(chunks)} chunk(s).")
    print(f"✅ Document split into {len(chunks)} chunk(s).")  # New print statement
    return chunks

def save_benchmarking_data(benchmark_data):
    """
    Saves the benchmarking data to the benchmarking file.
    """
    try:
        with open(BENCHMARKING_FILE, 'w', encoding='utf-8') as f:
            json.dump(benchmark_data, f, indent=4)
        logging.info(f"Saved benchmarking data to '{BENCHMARKING_FILE}'.")
        print(f"Saved benchmarking data to '{BENCHMARKING_FILE}'.")
    except Exception as e:
        logging.error(f"Failed to save benchmarking data: {e}")
        print(f"Failed to save benchmarking data: {e}")

# =======================
# Main Processing Function
# =======================

def extract_entities_index(selected_files, model):
    """
    Extracts and indexes entities from the selected documents.
    Combines entities into a single JSON index with continuous IDs.
    """
    all_entities = []
    all_model_outputs = []  # To store all model outputs for the text file
    entity_id_counter = 1  # Start entity IDs from 1

    available_tokens = calculate_available_tokens(PROMPT_TEMPLATE, model)  # Uses local tokenizer
    logging.info(f"Available tokens for chunking: {available_tokens}")

    total_inbound_tokens = 0
    total_outbound_tokens = 0
    per_chunk_metrics = []

    logging.info("Starting entity extraction process.")
    print("🔍 Starting entity extraction process.")  # Added print statement

    for file_info in selected_files:
        processed_file = file_info.get("converted_file_path")
        if not processed_file or not os.path.isfile(processed_file):
            logging.warning(f"Processed file not found: {processed_file}. Skipping this file.")
            print(f"Processed file not found: {processed_file}. Skipping this file.")
            continue

        original_file = file_info.get("original_file_name", os.path.basename(processed_file))
        logging.info(f"Processing Document: {original_file}")
        print(f"Processing Document: {original_file}")

        # Read the entire document
        try:
            with open(processed_file, 'r', encoding='utf-8') as f:
                document_text = f.read()
        except Exception as e:
            logging.error(f"Error reading file '{processed_file}': {e}")
            print(f"Error reading file '{processed_file}': {e}")
            continue

        # Chunk the document
        chunks = chunk_document(document_text, available_tokens, model)  # Uses local tokenizer
        for chunk_index, chunk in enumerate(chunks, start=1):
            # Prepare the prompt with the chunk
            prompt = PROMPT_TEMPLATE.replace("[Insert the document text here]", chunk)
            inbound_tokens = count_tokens(prompt, model)  # Uses local tokenizer
            total_inbound_tokens += inbound_tokens

            logging.info(f"Prepared prompt for chunk {chunk_index} of '{original_file}' with {inbound_tokens} inbound tokens.")
            print(f"Prepared prompt for chunk {chunk_index} of '{original_file}'.")

            # Start timing for the chunk
            chunk_start_time = time.time()

            # Call the model for entity extraction only
            response = call_ollama(prompt, model, operation="entity_extraction")  # Only for entity extraction
            
            outbound_tokens = 0
            if response:
                outbound_tokens = count_tokens(response, model)  # Uses local tokenizer
                total_outbound_tokens += outbound_tokens
                all_model_outputs.append(response)  # Store model output

                logging.info(f"Received response for chunk {chunk_index} of '{original_file}' with {outbound_tokens} outbound tokens.")
                # Parse the response
                entities = parse_ollama_response(response)
                for entity in entities:
                    entity['Entity ID'] = entity_id_counter
                    entity['Source Document'] = original_file
                    entity_id_counter += 1
                    all_entities.append(entity)
                logging.info(f"Extracted {len(entities)} entities from chunk {chunk_index} of '{original_file}'.")
                print(f"Extracted {len(entities)} entities from chunk {chunk_index} of '{original_file}'.")
            else:
                logging.info(f"No outbound tokens since there was no model response for chunk {chunk_index} of '{original_file}'.")
                print(f"No response from model for chunk {chunk_index} of '{original_file}'.")

            # End timing for the chunk
            chunk_end_time = time.time()
            chunk_duration = chunk_end_time - chunk_start_time

            # Record metrics for the chunk
            per_chunk_metrics.append({
                "Source Document": original_file,
                "Chunk Index": chunk_index,
                "Inbound Tokens": inbound_tokens,
                "Outbound Tokens": outbound_tokens,
                "Processing Time (s)": round(chunk_duration, 2)
            })

            # Log per-chunk token metrics
            logging.debug(f"Chunk {chunk_index} Metrics: Inbound Tokens = {inbound_tokens}, Outbound Tokens = {outbound_tokens}, Processing Time = {chunk_duration:.2f}s")

    if all_entities:
        # Save the combined entities index with timestamp
        try:
            with open(ENTITIES_INDEX_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_entities, f, indent=4)
            logging.info(f"Saved combined entities index to '{ENTITIES_INDEX_FILE}'.")
            print(f"Saved combined entities index to '{ENTITIES_INDEX_FILE}'.")
        except Exception as e:
            logging.error(f"Failed to save combined entities index: {e}")
            print(f"Failed to save combined entities index: {e}")
            sys.exit(1)

        # Save all model outputs to a text file
        try:
            with open(MODEL_OUTPUTS_FILE, 'w', encoding='utf-8') as f:
                for output in all_model_outputs:
                    f.write(output + "\n\n")
            logging.info(f"Saved all model outputs to '{MODEL_OUTPUTS_FILE}'.")
            print(f"Saved all model outputs to '{MODEL_OUTPUTS_FILE}'.")
        except Exception as e:
            logging.error(f"Failed to save model outputs: {e}")
            print(f"Failed to save model outputs: {e}")
            sys.exit(1)

        # Create a text-only copy of the entities index
        try:
            with open(ENTITIES_INDEX_TEXT_FILE, 'w', encoding='utf-8') as f:
                for entity in all_entities:
                    f.write(f"Entity ID: {entity['Entity ID']}\n")
                    f.write(f"Entity Name: {entity['Entity Name']}\n")
                    f.write(f"Entity Type: {entity['Entity Type']}\n")
                    f.write(f"Description: {entity['Description']}\n")
                    f.write(f"Source Document: {entity['Source Document']}\n\n")
            logging.info(f"Saved text-only entities index to '{ENTITIES_INDEX_TEXT_FILE}'.")
            print(f"Saved text-only entities index to '{ENTITIES_INDEX_TEXT_FILE}'.")
            
            # Generate a brief entities index file with '_index_' in the filename
            brief_entities_index_filename = f"entities_brief_index_{timestamp}.txt"
            ENTITIES_BRIEF_INDEX_FILE = os.path.join(os.path.dirname(ENTITIES_INDEX_FILE), brief_entities_index_filename)
            with open(ENTITIES_BRIEF_INDEX_FILE, 'w', encoding='utf-8') as f:
                for entity in all_entities:
                    f.write(f"Entity ID: {entity['Entity ID']}, Name: {entity['Entity Name']}, Type: {entity['Entity Type']}\n")
            logging.info(f"Saved brief entities index to '{ENTITIES_BRIEF_INDEX_FILE}'.")
            print(f"Saved brief entities index to '{ENTITIES_BRIEF_INDEX_FILE}'.")
        except Exception as e:
            logging.error(f"Failed to save text-only entities index: {e}")
            print(f"Failed to save text-only entities index: {e}")
            sys.exit(1)
        
            # Save benchmarking data similarly to step 3
            try:
                with open(BENCHMARKING_FILE, 'w', encoding='utf-8') as f:
                    json.dump(benchmarking_data, f, indent=4)
                logging.info(f"Saved benchmarking data to '{BENCHMARKING_FILE}'.")
                print(f"Saved benchmarking data to '{BENCHMARKING_FILE}'.")
            except Exception as e:
                logging.error(f"Failed to save benchmarking data: {e}")
                print(f"Failed to save benchmarking data: {e}")
                sys.exit(1)
    else:
        logging.warning("No entities were extracted from any documents.")
        print("No entities were extracted from any documents.")

        # Prepare benchmarking data
        benchmarking_data = {
            "Total Inbound Tokens": total_inbound_tokens,
            "Total Outbound Tokens": total_outbound_tokens,
            "Chunks": per_chunk_metrics
        }

        # Log benchmarking totals
        logging.info(f"Total Inbound Tokens: {total_inbound_tokens}")
        logging.info(f"Total Outbound Tokens: {total_outbound_tokens}")

        # Log detailed benchmarking data
        for metric in per_chunk_metrics:
            logging.debug(f"Benchmarking Data - Document: {metric['Source Document']}, "
                          f"Chunk: {metric['Chunk Index']}, "
                          f"Inbound Tokens: {metric['Inbound Tokens']}, "
                          f"Outbound Tokens: {metric['Outbound Tokens']}, "
                          f"Processing Time (s): {metric['Processing Time (s)']}")

        # Save benchmarking data with _index_ modifier and timestamp
        benchmarking_index_filename = f"benchmarking_index_{timestamp}.json"
        BENCHMARKING_INDEX_FILE = os.path.join(os.path.dirname(BENCHMARKING_FILE), benchmarking_index_filename)

        try:
            with open(BENCHMARKING_INDEX_FILE, 'w', encoding='utf-8') as f:
                json.dump(benchmarking_data, f, indent=4)
            logging.info(f"Saved benchmarking data to '{BENCHMARKING_INDEX_FILE}'.")
            print(f"Saved benchmarking data to '{BENCHMARKING_INDEX_FILE}'.")
        except Exception as e:
            logging.error(f"Failed to save benchmarking data: {e}")
            print(f"Failed to save benchmarking data: {e}")

# =======================
# Main Execution
# =======================

def main():
    """
    Main function to execute the entity indexing process.
    """
    try:
        logging.info("Starting main function.")
        print("🚀 Starting main function.")  # Added print statement
        args = parse_arguments()
        logging.info(f"Parsed arguments: {args}")
        print(f"📝 Parsed arguments: {args}")  # Added print statement
        
        # Define the 'model' variable based on the '--model' argument
        if args.model == 'small':
            model = "llama3.2:1b"
        elif args.model == 'large':
            model = "llama3.2:latest"
        else:
            logging.error(f"Invalid model choice: {args.model}")
            print(f"❌ Invalid model choice: {args.model}")
            sys.exit(1)
        
        available_files = load_available_files(AVAILABLE_FILES_JSON)

        # Select files to process
        if args.number_of_files == 'all':
            files_to_process = available_files
        else:
            files_to_process = available_files[:args.number_of_files]

        if not files_to_process:
            logging.error("No valid files selected for processing. Exiting program.")
            print("No valid files selected for processing. Exiting program.")
            sys.exit(1)

        logging.info(f"Selected {len(files_to_process)} file(s) to process.")
        print(f"✅ Selected {len(files_to_process)} file(s) to process.")  # Added print statement
        
        # Extract and index entities
        logging.info("Beginning entity extraction.")
        print("🔍 Beginning entity extraction.")  # Added print statement
        extract_entities_index(files_to_process, model)
        logging.info("Completed entity extraction.")
        print("✅ Completed entity extraction.")  # Added print statement
    except Exception as e:
        logging.error(f"An error occurred in main: {e}")
        print(f"❌ An error occurred in main: {e}")  # Added print statement
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)
