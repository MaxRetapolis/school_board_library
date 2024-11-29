import argparse
import subprocess
import os
from datetime import datetime
import logging
import time
import uuid

# Initialize logging
def initialize_logging(prompt_file):
    prompt_name = os.path.splitext(os.path.basename(prompt_file))[0]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    log_dir = r"C:\school_board_library\experiments\2_modularization_Ollama\data\logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"ollama_call_2nd_pass_{prompt_name}_{timestamp}.log")
    logging.basicConfig(
        filename=log_file,
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logging.info("Logging initialized.")

def list_available_models():
    try:
        result = subprocess.run(['ollama', 'list'],
                                text=True,
                                capture_output=True,
                                encoding='utf-8',
                                errors='replace',
                                check=True)
        models = result.stdout.strip().split('\n')
        logging.info(f"Available models: {models}")
        return models
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to list models: {e.stderr}")
        return []
    except Exception as e:
        logging.error(f"Unexpected error while listing models: {e}")
        return []

def call_ollama(prompt, model):
    """
    Sends the prompt to Ollama and returns the response.
    """
    print("Step: Initiating Ollama subprocess...")
    try:
        result = subprocess.run(
            ['ollama', 'run', model],
            input=prompt,
            text=True,
            capture_output=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        print("Step: Ollama subprocess completed.")
        if result.stdout:
            print("Step: Received output from Ollama.")
            return result.stdout.strip()
        else:
            print("Step: Ollama returned no output.")
            return ""
    except subprocess.CalledProcessError as e:
        print(f"Step: Ollama command failed with error: {e.stderr}")
        return None
    except Exception as e:
        print(f"Step: Unexpected error during Ollama command: {e}")
        return None

def analyze_entities(text):
    """
    Analyzes the text to identify entities and generate unique IDs.
    """
    entities = {}  # Dictionary to store entities and their unique IDs
    # Placeholder logic for entity extraction
    for word in text.split():
        if word not in entities:
            entities[word] = str(uuid.uuid4())
    return entities

def run_second_pass(prompt_file, context_file, model, first_pass_output_file):
    initialize_logging(prompt_file)
    start_second_pass = time.perf_counter()
    logging.info("Step: Starting Ollama Second Pass...")

    # Map 'small' and 'large' to specific model names
    if model.lower() == 'small':
        selected_model = "llama3.2:1b"
    elif model.lower() == 'large':
        selected_model = "llama3.2:latest"
    else:
        logging.error(f"Invalid model selection: {model}")
        print(f"Invalid model selection: {model}")
        return

    # Load prompt, pre-analyzed entities, and text to analyze
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt = f.read()
        with open(first_pass_output_file, 'r', encoding='utf-8') as f:
            pre_analyzed_entities = f.read()
        with open(context_file, 'r', encoding='utf-8') as f:
            text_to_analyze = f.read()
        logging.info("Step: Loaded prompt, pre-analyzed entities, and text to analyze.")
    except Exception as e:
        logging.error(f"Step: Failed to load files: {e}")
        return

    # Combine prompt, pre-analyzed entities, and text to analyze
    combined_text = prompt + "\n\nPre-Analyzed Entities:\n" + pre_analyzed_entities + "\n\nText to Analyze:\n" + text_to_analyze
    logging.info("Step: Combined prompt, pre-analyzed entities, and text to analyze.")

    # Call Ollama API for second pass analysis
    response = call_ollama(combined_text, selected_model)
    if response:
        logging.info("Step: Received response from Ollama.")
        entities = analyze_entities(response)
        logging.info(f"Step: Identified entities: {entities}")

        # Write second pass output to file
        prompt_name = os.path.splitext(os.path.basename(prompt_file))[0]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_dir = r"C:\school_board_library\experiments\2_modularization_Ollama\data\model_output"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"ollama_call_2nd_pass_{prompt_name}_{timestamp}.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response)
            f.write("\n\nEntities:\n")
            for entity, entity_id in entities.items():
                f.write(f"{entity}: {entity_id}\n")
        logging.info(f"Step: Second pass output written to file: {output_file}")
    else:
        logging.warning("Step: No response received from Ollama.")

    end_second_pass = time.perf_counter()
    logging.info(f"Total execution time: {end_second_pass - start_second_pass:.4f} seconds.")

def main():
    parser = argparse.ArgumentParser(description="Ollama Second Pass Script")
    parser.add_argument('--prompt_file', type=str, required=True, help='Path to the second pass prompt file.')
    parser.add_argument('--context_file', type=str, required=True, help='Path to the text file to analyze.')
    # Replace dynamic model choices with fixed 'small' and 'large'
    parser.add_argument('--model', type=str, choices=['small', 'large'], required=True, help='Model size: small or large.')
    parser.add_argument('--first_pass_output_file', type=str, required=True, help='Path to the prompt entities file.')
    args = parser.parse_args()

    run_second_pass(args.prompt_file, args.context_file, args.model, args.first_pass_output_file)

if __name__ == "__main__":
    main()
