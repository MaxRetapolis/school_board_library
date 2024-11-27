import os
import sys
import json
import subprocess
import argparse
import logging
from pathlib import Path
from datetime import datetime
import time
import re

# =======================
# Configuration Section
# =======================

AVAILABLE_FILES_JSON = r"C:\school_board_library\experiments\1_prelearning\data\2_available_converted_files.json"

RELATIONSHIPS_DIR = r"C:\school_board_library\experiments\1_prelearning\data\relationships"
os.makedirs(RELATIONSHIPS_DIR, exist_ok=True)

LOGS_DIR = r"C:\school_board_library\experiments\1_prelearning\data\logs"
os.makedirs(LOGS_DIR, exist_ok=True)

EXTRACTED_RELATIONSHIPS_FILE = os.path.join(RELATIONSHIPS_DIR, "extracted_relationships.json")

CHARS_PER_CHUNK = 1500
OVERLAP_CHARS = 300

# Generate a timestamp for the log filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = os.path.join(LOGS_DIR, f'relationship_extraction_{timestamp}.log')

# Configure logging to create a new log file each run with timestamp
logging.basicConfig(
    filename=log_filename,
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# =======================
# Prompt and Relationship Structure
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
        print(f"❌ Failed to load prompt template from '{prompt_file_path}': {e}")
        sys.exit(1)

# Set the path to 'prompt_relationships.txt'
PROMPT_TEMPLATE_FILE = r"C:\school_board_library\experiments\1_prelearning\data\prompts\prompt_relationships.txt"

# Load the prompt content
PROMPT_TEMPLATE = load_prompt_template(PROMPT_TEMPLATE_FILE)

# =======================
# Utility Functions
# =======================

def parse_arguments():
    """
    Parses command-line arguments.
    """
    def positive_int_or_all(value):
        if value.lower() == 'all':
            return 'all'
        try:
            ivalue = int(value)
            if ivalue < 1:
                raise argparse.ArgumentTypeError("Number must be a positive integer.")
            return ivalue
        except ValueError:
            raise argparse.ArgumentTypeError("Invalid number: must be a positive integer or 'all'.")

    parser = argparse.ArgumentParser(description="Extract relationships from school board meeting documents.")

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

def select_files_to_process(available_files, num_files):
    """
    Selects the files to process based on the provided parameters.
    """
    if num_files == 'all':
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
    chunks = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chars_per_chunk
            if end >= text_length:
                chunk = text[start:].strip()
                chunks.append((chunk, start, text_length))
                break
            else:
                # Avoid splitting words
                while end > start and text[end] not in (' ', '\n'):
                    end -= 1
                chunk = text[start:end].strip()
                chunks.append((chunk, start, end))
                start = end - overlap_chars
                if start < 0:
                    start = 0
        logging.info(f"Split '{file_path}' into {len(chunks)} chunk(s).")
        return chunks
    except Exception as e:
        logging.error(f"Error reading file '{file_path}': {e}")
        print(f"❌ Error reading file '{file_path}': {e}")
        return chunks  # Return whatever chunks were created before the error

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
            encoding='utf-8',
            errors='replace',
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
    """
    try:
        # Assuming the response is already in JSON
        data = json.loads(response)
        data['document_name'] = document_name
        data['chunk_number'] = chunk_number
        return data
    except json.JSONDecodeError:
        # Handle non-JSON responses
        logging.error("Model output is not valid JSON.")
        return {}
    except Exception as e:
        logging.error(f"Failed to process model output: {e}")
        return {}

def parse_ollama_response(response, source_file, chunk_number):
    """
    Parses the Ollama response and converts it into the defined JSON structure for relationships.
    """
    try:
        processed_data = process_model_output(response, source_file, chunk_number)
        relationships = processed_data.get("relationships", [])
        parsed_relationships = []
        for relationship in relationships:
            # Extract relationship attributes
            parsed_relationships.append({
                "relationship_type": relationship.get("relationship_type", "").strip(),
                "source_entity": relationship.get("source_entity", {}),
                "target_entity": relationship.get("target_entity", {}),
                "description": relationship.get("description", "").strip(),
                "context_or_evidence": relationship.get("context_or_evidence", "").strip(),
                "date_or_timeframe": relationship.get("date_or_timeframe", "").strip(),
                "document_name": source_file,
                "chunk_number": chunk_number,
                "start_character": relationship.get("start_character", 0),
                "end_character": relationship.get("end_character", 0),
                "chunk_file_name": relationship.get("chunk_file_name", "")
            })
        logging.info(f"Parsed Relationships for Source '{source_file}': {json.dumps(parsed_relationships)}")
        return {"source_file": source_file, "relationships": parsed_relationships}
    except Exception as e:
        logging.error(f"Error processing model output for '{source_file}': {e}")
        return {"source_file": source_file, "relationships": []}

def sanitize_filename(filename):
    """
    Sanitizes the filename to create a valid filename.
    """
    base_name = os.path.splitext(filename)[0]
    sanitized = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in base_name)
    return sanitized

def clean_text(text):
    """
    Cleans the input text by removing non-printable and non-ASCII characters.
    """
    # Remove non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    # Remove control characters
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    return text

def extract_relationships(selected_files):
    """
    Extracts relationships from the selected documents.
    """
    all_relationships = []
    total_chars_processed = 0
    per_chunk_timings = []

    for file_info in selected_files:
        processed_file = file_info.get("converted_file_path")

        if not processed_file or not os.path.isfile(processed_file):
            logging.warning(f"Processed file not found: {processed_file}. Skipping this file.")
            print(f"⚠️ Processed file not found: {processed_file}. Skipping this file.")
            continue

        original_file = file_info.get("original_file_name", os.path.basename(processed_file))
        logging.info(f"📄 Processing Document: {original_file}")
        print(f"📄 Processing Document: {original_file}")

        # Define unique relationships files
        sanitized_name = sanitize_filename(os.path.basename(processed_file))
        relationships_file = os.path.join(
            RELATIONSHIPS_DIR,
            f"relationships-{sanitized_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        relationships_text_file = os.path.join(
            RELATIONSHIPS_DIR,
            f"relationships_text_{sanitized_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        # Split the document into chunks
        chunks = split_text_into_chunks(processed_file, chars_per_chunk=CHARS_PER_CHUNK, overlap_chars=OVERLAP_CHARS)

        if not chunks:
            logging.warning(f"No chunks created for '{original_file}'. Skipping this file.")
            print(f"⚠️ No chunks created for '{original_file}'. Skipping this file.")
            continue

        logging.info(f"Split '{processed_file}' into {len(chunks)} chunk(s).")
        print(f"✅ Split '{processed_file}' into {len(chunks)} chunk(s).")

        document_relationships = []

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

            # Prepare the prompt with cleaned text
            prompt = (
                PROMPT_TEMPLATE +
                f"\n\n**Document Name:** {original_file}\n" +
                f"**Chunk Number:** {idx}\n" +
                f"**Start Character:** {start_char}\n" +
                f"**End Character:** {end_char}\n" +
                f"**Chunk File Name:** {chunk_filename}\n" +
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
                time_per_char_chunk = round(chunk_duration / chunk_size, 6) if chunk_size > 0 else 0
                per_chunk_timings.append({
                    "Chunk Number": idx,
                    "Chunk Size (chars)": chunk_size,
                    "Time Taken (seconds)": round(chunk_duration, 6),
                    "Time per Character (seconds)": time_per_char_chunk
                })

                # Log the full API response
                logging.info(f"Ollama API response for Chunk {idx}: {response}")

                # Write the exact model output to the relationships_text file
                try:
                    with open(relationships_text_file, 'a', encoding='utf-8') as text_file:
                        text_file.write(f"---- Chunk File Name: {chunk_filename} ----\n")
                        text_file.write(f"---- Chunk {idx} ----\n")
                        text_file.write(f"---- Start Char: {start_char} ||| End Char: {end_char} ----\n")
                        text_file.write(response + "\n\n")
                    logging.info(f"📄 Written model output for Chunk {idx} to '{relationships_text_file}'.")
                except Exception as e:
                    logging.error(f"❌ Failed to write model output to '{relationships_text_file}': {e}")
                    print(f"❌ Failed to write model output to '{relationships_text_file}': {e}")

                parsed_data = parse_ollama_response(response, os.path.basename(processed_file), idx)
                relationships = parsed_data.get("relationships", [])
                if relationships:
                    document_relationships.extend(relationships)
                    logging.info(f"✅ Extracted {len(relationships)} relationships from Chunk {idx}.")
                    print(f"✅ Extracted {len(relationships)} relationships from Chunk {idx}.")
                else:
                    logging.warning(f"No relationships found in response for Chunk {idx} of '{original_file}'.")
                    print(f"⚠️ No relationships found in response for Chunk {idx} of '{original_file}'.")
            else:
                logging.warning(f"No response received for chunk {idx} of '{original_file}'. Skipping.")
                print(f"⚠️ No response received for chunk {idx} of '{original_file}'. Skipping.")

        if not document_relationships:
            logging.warning(f"No relationships extracted from '{original_file}'.")
            print(f"⚠️ No relationships extracted from '{original_file}'.")
            continue

        # Save the extracted relationships for the document
        try:
            with open(relationships_file, 'w', encoding='utf-8') as rf:
                json.dump({"relationships": document_relationships}, rf, ensure_ascii=False, indent=4)
            logging.info(f"📄 Saved extracted relationships to '{relationships_file}'.")
            print(f"📄 Saved extracted relationships to '{relationships_file}'.")
            all_relationships.extend(document_relationships)
        except Exception as e:
            logging.error(f"Failed to save relationships for '{original_file}': {e}")
            print(f"❌ Failed to save relationships for '{original_file}': {e}")

    return all_relationships, total_chars_processed, per_chunk_timings

def test_api_connectivity():
    """
    Tests the Ollama API connectivity by asking a sample question and printing the first 100 characters of the response.
    """
    test_prompt = "Who is Jason Bourne? Reply in 30 words or less."
    print("🔍 Testing Ollama API connectivity...")
    try:
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
# Main Execution
# =======================

def main():
    """
    Main function to execute the relationship extraction process.
    """
    global OLLAMA_MODEL

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

    print(f"Using Ollama model: {OLLAMA_MODEL}")

    available_files = load_available_files(AVAILABLE_FILES_JSON)
    if not available_files:
        logging.error("No available files to process. Exiting program.")
        print("❌ No available files to process. Exiting program.")
        sys.exit(1)

    # Select files to process based on --number_of_files
    files_to_process = select_files_to_process(
        available_files,
        args.number_of_files
    )

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

    # Extract relationships from the selected files
    all_relationships, total_chars, per_chunk_timings = extract_relationships(files_to_process)

    # End benchmarking
    end_time = datetime.now()
    duration = end_time - start_time
    total_elapsed_time = duration.total_seconds()
    time_per_char = total_elapsed_time / total_chars if total_chars > 0 else 0

    # Create benchmark file
    benchmark_filename = os.path.join(
        LOGS_DIR,
        f"benchmark_{sanitize_filename(OLLAMA_MODEL)}_{end_time.strftime('%Y%m%d_%H%M%S')}.txt"
    )
    try:
        with open(benchmark_filename, 'w', encoding='utf-8') as bf:
            bf.write(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            bf.write(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            bf.write(f"Total Elapsed Time (seconds): {total_elapsed_time:.6f}\n")
            bf.write(f"Number of Characters Processed: {total_chars}\n")
            bf.write(f"Time per Character (seconds): {time_per_char:.6f}\n")
            bf.write(f"Model Used: {OLLAMA_MODEL}\n")
            bf.write("\nPer Chunk Timings:\n")
            bf.write("Chunk Number | Chunk Size (chars) | Time Taken (seconds) | Time per Character (seconds)\n")
            bf.write("-----------------------------------------------------------------------------\n")
            for timing in per_chunk_timings:
                bf.write(f"{timing['Chunk Number']} | {timing['Chunk Size (chars)']} | {timing['Time Taken (seconds)']} | {timing['Time per Character (seconds)']}\n")
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
