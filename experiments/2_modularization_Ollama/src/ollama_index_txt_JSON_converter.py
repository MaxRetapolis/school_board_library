import argparse
import os
import json
import logging
from datetime import datetime
import time
import re
import yaml  # Added import for YAML parsing

def initialize_logging(prompt_file):
    prompt_name = os.path.splitext(os.path.basename(prompt_file))[0]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    log_dir = r"C:\school_board_library\experiments\2_modularization_Ollama\data\logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"ollama_index_txt_JSON_{prompt_name}_{timestamp}.log")
    logging.basicConfig(
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Added handler for console output
        ],
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logging.info("Logging initialized.")

def parse_text_to_json(text):
    logging.info("Starting parse_text_to_json function.")
    try:
        logging.debug(f"Input text length: {len(text)} characters.")
        
        # Initialize the entities dictionary
        entities = {}

        # Split the text into lines for processing
        lines = text.splitlines()
        current_entity_type = None
        current_entity = {}
        
        for line in lines:
            logging.debug(f"Processing line: {line}")  # Log each line being processed
            line = line.strip()
            if line.startswith("- **Entity Type:**"):
                # Save the previous entity if exists
                if current_entity and current_entity_type:
                    entities[current_entity_type].append(current_entity)
                    logging.debug(f"Added entity to {current_entity_type}: {current_entity}")
                    current_entity = {}
                
                # Extract entity type
                try:
                    current_entity_type = line.split("**Entity Type:**")[1].strip()
                    if current_entity_type not in entities:
                        entities[current_entity_type] = []
                    logging.info(f"Detected entity type: {current_entity_type}")
                except IndexError:
                    logging.warning(f"Failed to extract entity type from line: {line}")
                    current_entity_type = None
            elif line.startswith("- **") and current_entity_type:
                # Extract key and value
                key, value = parse_key_value(line)
                if key and value:
                    current_entity[key] = value
                    logging.debug(f"Extracted {key}: {value}")
            elif line.startswith("-") and current_entity_type:
                # Handle nested attributes
                key, value = parse_key_value(line)
                if key and value:
                    current_entity[key] = value
                    logging.debug(f"Extracted {key}: {value}")
            else:
                logging.debug(f"Ignored line: {line}")  # Log ignored lines
            # ... Handle other possible patterns ...

        # Add the last entity if exists
        if current_entity and current_entity_type:
            entities[current_entity_type].append(current_entity)
            logging.debug(f"Added entity to {current_entity_type}: {current_entity}")
        
        logging.info(f"Final entities structure: {json.dumps(entities, indent=2)}")  # Log detailed entities
        return entities
    except Exception as e:
        logging.error(f"Error in parse_text_to_json: {e}", exc_info=True)  # Log exception with traceback
        return None

def parse_key_value(line):
    """
    Parses a line to extract key and value.
    Example: '- **Event Identifier:** Event_20230427_001' -> ('Event Identifier', 'Event_20230427_001')
    """
    try:
        # Use regex to extract text between '**' and '**' as key, and the rest as value
        match = re.match(r'- \*\*(.+?)\*\*:\s*(.+)', line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            return key, value
        else:
            logging.warning(f"Line format unrecognized: {line}")
            return None, None
    except Exception as e:
        logging.error(f"Error parsing line '{line}': {e}")
        return None, None

def run_converter(prompt_file, text_file):
    start_time = time.perf_counter()
    logging.info("Starting Ollama Index TXT to JSON Converter...")

    # Load prompt from file
    if not os.path.isfile(prompt_file):
        logging.error(f"Prompt file does not exist: {prompt_file}")
        return
    try:
        with open(prompt_file, 'r', encoding='utf-8') as file:
            prompt = file.read()
        logging.info("Prompt loaded successfully.")
    except Exception as e:
        logging.error(f"Failed to load prompt file: {e}")
        return

    # Load text file
    if not os.path.isfile(text_file):
        logging.error(f"Text file does not exist: {text_file}")
        return
    try:
        with open(text_file, 'r', encoding='utf-8') as file):
            text = file.read()
        logging.info("Text file loaded successfully.")
    except Exception as e:
        logging.error(f"Failed to load text file: {e}")
        return

    # Parse text to JSON
    json_output = parse_text_to_json(text)
    if json_output:
        logging.info("Text parsed to JSON successfully.")
    else:
        logging.error("Failed to parse text to JSON.")
        return

    # Ensure output directory exists
    output_dir = r"C:\school_board_library\experiments\2_modularization_Ollama\data\index_output"
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            logging.info(f"Output directory created: {output_dir}")
        except Exception as e:
            logging.error(f"Failed to create output directory: {e}")
            return
            
    # Write JSON output to file
    prompt_name = os.path.splitext(os.path.basename(prompt_file))[0]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = os.path.join(output_dir, f"ollama_index_txt_JSON_{prompt_name}_{timestamp}.json")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_output, f, indent=4)
        logging.info(f"JSON output saved to file: {output_file}")
    except Exception as e:
        logging.error(f"Failed to write JSON output to file: {e}")

    end_time = time.perf_counter()
    logging.info(f"Total execution time: {end_time - start_time:.4f} seconds.")

def main():
    parser = argparse.ArgumentParser(description="Ollama Index TXT to JSON Converter Script")
    parser.add_argument('--prompt_file', type=str, required=True, help='Path to the prompt file.')
    parser.add_argument('--text_file', type=str, required=True, help='Path to the text file to convert.')
    args = parser.parse_args()

    initialize_logging(args.prompt_file)  # Initialize logging early
    run_converter(args.prompt_file, args.text_file)

if __name__ == "__main__":
    main()
