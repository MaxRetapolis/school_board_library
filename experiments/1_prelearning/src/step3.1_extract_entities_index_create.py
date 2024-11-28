import os
from pathlib import Path
import tiktoken  # Ensure this library is installed: pip install tiktoken
import argparse
import logging
import sys
import json
from datetime import datetime  # Added import for timestamp

# Directory paths
DOCUMENTS_DIR = r"C:\school_board_library\experiments\1_prelearning\data\documents"
PROMPTS_DIR = r"C:\school_board_library\experiments\1_prelearning\data\prompts"
LOGS_DIR = r"C:\school_board_library\experiments\1_prelearning\data\logs"
os.makedirs(LOGS_DIR, exist_ok=True)

# =======================
# Configuration Section
# =======================

MAX_TOKENS = 128000
OUTPUT_TOKEN_BUFFER = 20000  # Default buffer

# Additional Configuration Variables
OLLAMA_MODEL = "llama3.2:1b"

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

# Directory to save the extracted entities
ENTITIES_DIR = r"C:\school_board_library\experiments\1_prelearning\data\entities"
os.makedirs(ENTITIES_DIR, exist_ok=True)

# Path to save the extracted entities
EXTRACTED_ENTITIES_FILE = os.path.join(ENTITIES_DIR, "extracted_entities.json")

# =======================
# Argument Parsing
# =======================

def parse_arguments():
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

    parser = argparse.ArgumentParser(description="Process documents for token counting.")
    parser.add_argument(
        '--number_of_files',
        type=positive_int_or_all,
        default='all',
        help="Number of files to process: specify a positive integer or 'all'."
    )
    parser.add_argument(
        '--model',
        choices=['small', 'large'],
        default='small',
        help="Model size to use for tokenization."
    )
    print("✅ Parsed command-line arguments.")
    return parser.parse_args()

# =======================
# Logging Configuration
# =======================

# Generate timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Configure logging with the new log filename
logging.basicConfig(
    filename=os.path.join(LOGS_DIR, f'step3.1_entities_extraction_index_{timestamp}.log'),
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Function to discover documents
def discover_documents(directory):
    supported_extensions = ['.pdf', '.docx', '.txt']
    documents = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if Path(file).suffix.lower() in supported_extensions:
                documents.append(os.path.join(root, file))
    return documents

# Function to load prompts
def load_prompts(directory):
    prompt_file = os.path.join(directory, 'prompt_entities_index.txt')
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return [f.read()]
    except Exception as e:
        logging.error(f"Failed to load prompt from '{prompt_file}': {e}")
        print(f"❌ Failed to load prompt from '{prompt_file}': {e}")
        sys.exit(1)

# Initialize tokenizer
tokenizer = tiktoken.get_encoding("cl100k_base")  # Adjust based on the model used

# Function to extract text from documents (implement as needed)
def extract_text(file_path):
    # TODO: Implement text extraction based on file type
    # Example for text files:
    if file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    # Add extraction for .pdf, .docx as required
    return ""

# =======================
# Load Available Files
# =======================

def load_available_files(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            available_files = json.load(f)
        logging.info(f"Loaded {len(available_files)} available file(s) from '{json_path}'.")
        print(f"✅ Loaded {len(available_files)} available file(s) from '{json_path}'.")
        return available_files
    except Exception as e:
        logging.error(f"Failed to load available files from '{json_path}': {e}")
        print(f"❌ Failed to load available files from '{json_path}': {e}")
        sys.exit(1)

# =======================
# Select Files to Process
# =======================

def select_files(available_files, number_of_files):
    if number_of_files == 'all':
        selected_files = available_files
        logging.info("Selected to process all available files.")
        print("✅ Selected to process all available files.")
    else:
        selected_files = available_files[:number_of_files]
        logging.info(f"Selected the first {number_of_files} file(s) to process.")
        print(f"✅ Selected the first {number_of_files} file(s) to process.")
    return selected_files

# =======================
# Modify Main Execution
# =======================

# Define the 'extract_entities' function and necessary helper functions

def call_ollama(prompt):
    # Function to call Ollama API
    import requests
    try:
        response = requests.post(
            'http://localhost:11434/generate',
            json={'model': OLLAMA_MODEL, 'prompt': prompt}
        )
        if response.status_code == 200:
            return response.json().get('response', '')
        else:
            logging.error(f"Ollama API error: {response.status_code} - {response.text}")
            return ''
    except Exception as e:
        logging.error(f"Exception occurred while calling Ollama API: {e}")
        return ''

def process_model_output(response, document_name):
    # Function to process the model output
    # Save the output to entities index file and log
    if response:
        # Save to entities index file
        entities_filename = f"entities_extraction_index_{timestamp}.txt"
        entities_filepath = os.path.join(ENTITIES_DIR, entities_filename)
        with open(entities_filepath, 'a', encoding='utf-8') as ef:
            ef.write(f"Document: {document_name}\n")
            ef.write(f"{response}\n\n")
        logging.info(f"Entities extracted for '{document_name}' saved to '{entities_filepath}'.")
        print(f"✅ Entities extracted for '{document_name}' saved to '{entities_filepath}'.")
    else:
        logging.warning(f"No entities extracted for '{document_name}'.")
        print(f"⚠️ No entities extracted for '{document_name}'.")

def main():
    args = parse_arguments()
    logging.info(f"Number of files to process: {args.number_of_files}")
    logging.info(f"Model selected: {args.model}")
    
    available_files = load_available_files(r"C:\school_board_library\experiments\1_prelearning\data\2_available_converted_files.json")
    selected_files = select_files(available_files, args.number_of_files)
    
    documents = [file['converted_file_path'] for file in selected_files]
    
    # Load the prompt content using PROMPTS_DIR
    prompt_content = load_prompts(PROMPTS_DIR)
    PROMPT_TEMPLATE = prompt_content[0] if prompt_content else ""
    
    # Initialize tokenizer based on selected model
    if args.model == 'small':
        tokenizer = tiktoken.get_encoding("cl100k_base")  # Use valid encoding
    else:
        tokenizer = tiktoken.get_encoding("cl100k_base")  # Use the same encoding or another valid one
    
    for doc in documents:
        # Start processing a new file
        print(f"🚀 Starting processing for file: {doc}")
        logging.info(f"🚀 Starting processing for file: {doc}")
        
        total_file_tokens = 0  # Initialize token count for the file
        file_start_time = datetime.now()  # Start timing for the file
        
        # Extract text from the document
        doc_text = extract_text(doc)
        if not doc_text:
            logging.warning(f"No text extracted from '{doc}'. Skipping.")
            print(f"⚠️ No text extracted from '{doc}'. Skipping.")
            continue
        
        # Start of token calculation for prompt
        print("🔍 Starting token calculation for prompt.")
        logging.info("🔍 Starting token calculation for prompt.")
        
        prompt_tokens = len(tokenizer.encode(PROMPT_TEMPLATE))
        
        # Log and display prompt token count
        print(f"💡 Prompt tokens: {prompt_tokens}")
        logging.info(f"💡 Prompt tokens: {prompt_tokens}")
        
        doc_tokens = len(tokenizer.encode(doc_text))
        total_tokens = prompt_tokens + doc_tokens
        total_file_tokens += total_tokens  # Accumulate tokens for the file

        # Evaluate total tokens against maximum
        if total_tokens < MAX_TOKENS:
            print(f"✅ Total tokens ({total_tokens}) within limit. Sending to Ollama...")
            logging.info(f"✅ Total tokens ({total_tokens}) within limit. Sending to Ollama...")
            # Prepare the full prompt
            full_prompt = f"{PROMPT_TEMPLATE}\n\nText to analyze:\n\n{doc_text}"
            # Call Ollama API
            response = call_ollama(full_prompt)
            # Process the response
            process_model_output(response, doc)
        else:
            print(f"⚠️ Total tokens ({total_tokens}) exceed the maximum limit ({MAX_TOKENS}). Skipping.")
            logging.warning(f"Total tokens ({total_tokens}) exceed the maximum limit ({MAX_TOKENS}). Skipping.")
            continue

        # End processing for the current prompt
        print(f"✅ Finished processing prompt for file: {doc}")
        logging.info(f"✅ Finished processing prompt for file: {doc}")
    
    # Remove the code that tries to write 'all_entities' which is undefined
    # ...existing code...
    # with open(EXTRACTED_ENTITIES_FILE.replace('.json', '.txt'), 'w', encoding='utf-8') as ef:
    #     for entity in all_entities:
    #         ef.write(f"{entity}\n")
    # logging.info(f"Extracted entities saved to '{EXTRACTED_ENTITIES_FILE.replace('.json', '.txt')}'.")
    # print(f"✅ Extracted entities saved to '{EXTRACTED_ENTITIES_FILE.replace('.json', '.txt')}'.")
    
    # Remove redundant PROMPT_TEMPLATE assignment at the end of main()
    # ...existing code...

if __name__ == "__main__":
    main()
