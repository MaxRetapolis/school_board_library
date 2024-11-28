import os
from pathlib import Path
import tiktoken  # Ensure this library is installed: pip install tiktoken
import argparse
import logging
import sys
import json

# Directory paths
DOCUMENTS_DIR = r"C:\school_board_library\experiments\1_prelearning\data\documents"
PROMPTS_DIR = r"C:\school_board_library\experiments\1_prelearning\data\prompts"

MAX_TOKENS = 128000

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

logging.basicConfig(
    filename='step3.1_log.log',
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

def main():
    args = parse_arguments()
    logging.info(f"Number of files to process: {args.number_of_files}")
    logging.info(f"Model selected: {args.model}")
    
    available_files = load_available_files(r"C:\school_board_library\experiments\1_prelearning\data\2_available_converted_files.json")
    selected_files = select_files(available_files, args.number_of_files)
    
    # ...existing code for processing selected_files...
    documents = [file['converted_file_path'] for file in selected_files]
    prompts = load_prompts(PROMPTS_DIR)
    
    # Initialize tokenizer based on selected model
    if args.model == 'small':
        tokenizer = tiktoken.get_encoding("cl100k_base")  # Use valid encoding
    else:
        tokenizer = tiktoken.get_encoding("cl100k_base")  # Use the same encoding or another valid one
    
    for doc in documents:
        for prompt in prompts:
            doc_text = extract_text(doc)
            
            prompt_tokens = len(tokenizer.encode(prompt))
            doc_tokens = len(tokenizer.encode(doc_text))
            total_tokens = prompt_tokens + doc_tokens
            
            print(f"📄 Processing Document: {doc}")
            
            if total_tokens > MAX_TOKENS:
                print(f"❌ Document '{doc}' with prompt exceeds {MAX_TOKENS} tokens. Needs chunking.")
                logging.info(f"Document '{doc}' with prompt exceeds {MAX_TOKENS} tokens. Needs chunking.")
                # TODO: Implement chunking logic here
            else:
                print(f"✅ Document '{doc}' with prompt fits within {MAX_TOKENS} tokens.")
                logging.info(f"Document '{doc}' with prompt fits within {MAX_TOKENS} tokens.")
                # TODO: Proceed with processing

if __name__ == "__main__":
    main()
