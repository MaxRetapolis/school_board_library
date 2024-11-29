import tiktoken
import os
import logging
from datetime import datetime
import time
import argparse

def initialize_logging():
    log_dir = r"C:\school_board_library\experiments\2_modularization_Ollama\data\logs"
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    log_file = os.path.join(log_dir, f"tokenizer_{timestamp}.log")
    logging.basicConfig(
        filename=log_file,
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logging.info("Logging initialized.")

def read_file(file_path):
    print(f"Step: Reading file: {file_path}")
    logging.info(f"Step: Reading file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        print("Step: File read successfully.")
        logging.info("Step: File read successfully.")
        return content
    except Exception as e:
        print(f"Step: Failed to read file: {e}")
        logging.error(f"Step: Failed to read file: {e}")
        return None

def tokenize(content):
    print("Step: Tokenizing content...")
    logging.info("Step: Tokenizing content...")
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(content)
    print("Step: Tokenization completed.")
    logging.info("Step: Tokenization completed.")
    return tokens

def save_tokens(tokens, output_file, input_file):
    print(f"Step: Saving token summary to file: {output_file}")
    logging.info(f"Step: Saving token summary to file: {output_file}")
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        # Write the processed filename and total number of tokens
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(f"Processed File: {input_file}\n")
            file.write(f"Total Number of Tokens: {len(tokens)}\n")
        print("Step: Token summary saved successfully.")
        logging.info("Step: Token summary saved successfully.")
    except Exception as e:
        print(f"Step: Failed to save token summary: {e}")
        logging.error(f"Step: Failed to save token summary: {e}")

def main(input_file):
    initialize_logging()
    start_time = time.perf_counter()
    logging.info("Step: Starting tokenization process")
    
    # Generate output file path in data/model_output
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "model_output")
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = os.path.join(output_dir, f"token_summary_{timestamp}.txt")
    
    content = read_file(input_file)
    if content:
        tokens = tokenize(content)
        save_tokens(tokens, output_file, input_file)
    
    end_time = time.perf_counter()
    processing_time = end_time - start_time
    logging.info(f"Step: Tokenization process completed in {processing_time:.4f} seconds")
    print(f"Number of tokens: {len(tokens)}")
    print(f"Output saved to: {output_file}")
    logging.info(f"Number of tokens: {len(tokens)}")
    logging.info(f"Output saved to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tokenizer Script")
    parser.add_argument('input_file', type=str, help='Path to the input file.')
    args = parser.parse_args()
    
    main(args.input_file)
