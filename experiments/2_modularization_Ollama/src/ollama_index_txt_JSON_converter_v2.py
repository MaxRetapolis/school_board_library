import argparse
import os
import json
import logging
from datetime import datetime
import time
import re
import yaml  # Ensure pyyaml is installed

from pyparsing import Word, alphas, alphanums, Suppress, Group, OneOrMore, Optional, restOfLine

def initialize_logging():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    log_dir = r"C:\school_board_library\experiments\2_modularization_Ollama\data\logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"ollama_index_txt_JSON_{timestamp}.log")
    logging.basicConfig(
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ],
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.DEBUG  # Set to DEBUG for detailed logs
    )
    logging.info("Logging initialized.")

def parse_text_to_json(text):
    logging.info("Starting parse_text_to_json function.")
    try:
        # Log the entire text being processed
        logging.debug(f"Full text to be parsed:\n{text}")

        # Skip introductory text using a regular expression
        match = re.search(r"\*\*Entity Type:\*\*", text)
        if not match:
            logging.error("No entity type found in the text.")
            raise ValueError("No entity type found in the text.")
        text = text[match.start():]

        # Define grammar
        entity_type = Suppress("- **Entity Type:**") + Word(alphanums + " ")
        key = Suppress("- **") + Word(alphanums + " " + "/") + Suppress("**:")
        value = restOfLine

        attribute = Group(key + value)
        entity = Group(entity_type("type") + OneOrMore(attribute))
        grammar = OneOrMore(entity)

        parsed = grammar.parseString(text)

        entities = {}
        for ent in parsed:
            ent_type = ent.type.strip()
            if ent_type not in entities:
                entities[ent_type] = []
            attr = {k.strip(): v.strip() for k, v in ent[1:]}
            entities[ent_type].append(attr)
            logging.debug(f"Parsed entity under '{ent_type}': {attr}")

        logging.info(f"Final entities structure: {json.dumps(entities, indent=2)}")
        return entities
    except Exception as e:
        logging.error(f"Error in parse_text_to_json: {e}", exc_info=True)
        return None

def run_converter(text_file):
    start_time = time.perf_counter()
    logging.info("Starting Ollama Index TXT to JSON Converter V2...")

    # Load text file
    if not os.path.isfile(text_file):
        logging.error(f"Text file does not exist: {text_file}")
        return
    try:
        with open(text_file, 'r', encoding='utf-8') as file:
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
    output_dir = os.path.dirname(text_file)
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            logging.info(f"Output directory created: {output_dir}")
        except Exception as e:
            logging.error(f"Failed to create output directory: {e}")
            return

    # Write JSON output to file
    base_name = os.path.splitext(os.path.basename(text_file))[0]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = os.path.join(output_dir, f"{base_name}_{timestamp}.json")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_output, f, indent=4)
        logging.info(f"JSON output saved to file: {output_file}")
    except Exception as e:
        logging.error(f"Failed to write JSON output to file: {e}")

    end_time = time.perf_counter()
    logging.info(f"Total execution time: {end_time - start_time:.4f} seconds.")

def main():
    parser = argparse.ArgumentParser(description="Ollama Index TXT to JSON Converter Script V2")
    parser.add_argument('--text_file', type=str, required=True, help='Path to the text file to convert.')
    args = parser.parse_args()

    initialize_logging()  # Initialize logging early
    run_converter(args.text_file)

if __name__ == "__main__":
    main()