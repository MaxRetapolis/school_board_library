import argparse
import subprocess
import os
from datetime import datetime
import logging
import time
import re  # Added import

def initialize_logging(prompt_file):
    prompt_name = os.path.splitext(os.path.basename(prompt_file))[0]
    prompt_name = os.path.splitext(os.path.basename(prompt_file))[0]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # Added timestamp definition
    log_dir = r"C:\school_board_library\experiments\2_modularization_Ollama\data\logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"ollama_event_index_{prompt_name}_{timestamp}.log")
    logging.basicConfig(
        filename=log_file,
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logging.info("Logging initialized.")

def call_ollama(prompt, model):
    """
    Sends the prompt to Ollama and returns the response.
    """
    print("Step: Initiating Ollama subprocess...")
    try:
        result = subprocess.run(
            ['ollama', 'run', model],  # Removed '--no-spinner'
            input=prompt,
            text=True,
            stdout=subprocess.PIPE,        # Capture stdout
            stderr=subprocess.STDOUT,      # Redirect stderr to stdout
            encoding='utf-8',
            errors='replace'
        )
        print("Step: Ollama subprocess completed.")
        output = result.stdout or ''  # Capture all output from stdout
        print(f"Response from Ollama before post-processing (first 100 chars): {output[:100]}")
        logging.info(f"Response from Ollama before parsing (first 100 chars): {output[:100]}")
        logging.debug(f"Complete response from Ollama:\n{output}")  # Added complete output logging
        if output.strip():
            # Remove ANSI escape sequences and non-printable characters from the output
            ansi_escape = re.compile(r'''
                \x1B  # ESC
                (?:   # 7-bit C1 Fe Escape sequences
                    [@-Z\\-_]  # ESC [@ - _]
                |     # or [ for CSI sequences
                    \[
                    [0-?]*  # Parameter bytes
                    [ -/]*  # Intermediate bytes
                    [@-~]   # Final byte
                )
            ''', re.VERBOSE)
            # Remove ANSI escape sequences
            clean_output = ansi_escape.sub('', output)
            # Remove spinner characters (Unicode Braille Patterns)
            spinner_pattern = re.compile(r'[\u2800-\u28FF]')
            clean_output = spinner_pattern.sub('', clean_output)
            # Remove non-Unicode characters from the start and end
            clean_output = clean_output.strip().encode('utf-8', 'ignore').decode('utf-8')
            
            print("Step: Received clean output from Ollama.")
            logging.info(f"Clean output from Ollama (first 100 chars): {clean_output[:100]}")
            logging.debug(f"Complete clean output from Ollama:\n{clean_output}")  # Updated logging
            return clean_output
        else:
            print("Step: Ollama returned no output.")
            return ""
    except subprocess.CalledProcessError as e:
        print(f"Step: Ollama command failed with error: {e.stderr}")
        return None
    except Exception as e:
        print(f"Step: Unexpected error during Ollama command: {e}")
        return None

def clean_and_format_output(raw_output):
    """
    Cleans the raw model output by removing non-Unicode characters.
    Preserves formatting of the surrounding text.
    """
    # Remove non-Unicode characters from the start and end
    structured_output = raw_output.strip().encode('utf-8', 'ignore').decode('utf-8')
    
    logging.info(f"Cleaned output:\n{structured_output}")
    return structured_output

def run_indexer(prompt_file, previous_output_file, model):
    initialize_logging(prompt_file)
    start_time = time.perf_counter()
    print("Step: Starting Ollama Event Indexer...")
    logging.info("Step: Starting Ollama Event Indexer...")

    # Step 1: Load prompt from file
    print(f"Step: Loading prompt file: {prompt_file}")
    logging.info(f"Step: Loading prompt file: {prompt_file}")
    try:
        with open(prompt_file, 'r', encoding='utf-8') as file:
            prompt = file.read()
        print("Step: Prompt loaded successfully.")
        logging.info("Step: Prompt loaded successfully.")
    except Exception as e:
        print(f"Step: Failed to load prompt file: {e}")
        logging.error(f"Step: Failed to load prompt file: {e}")
        return

    # Step 2: Load previous model output from file
    print(f"Step: Loading previous model output file: {previous_output_file}")
    logging.info(f"Step: Loading previous model output file: {previous_output_file}")
    try:
        with open(previous_output_file, 'r', encoding='utf-8') as file:
            previous_output = file.read()
        print("Step: Previous model output loaded successfully.")
        logging.info("Step: Previous model output loaded successfully.")
    except Exception as e:
        print(f"Step: Failed to load previous model output file: {e}")
        logging.error(f"Step: Failed to load previous model output file: {e}")
        return

    # Step 3: Combine prompt and previous model output
    combined_text = prompt + "\n\n" + previous_output
    print(f"Prompt sent to Ollama (first 100 chars): {combined_text[:100]}")
    logging.info("Step: Combined prompt and previous model output.")

    # Step 4: Select model
    print(f"Step: Selecting model: {model}")
    logging.info(f"Step: Selecting model: {model}")
    if model.lower() == 'small':
        selected_model = "llama3.2:1b"
    elif model.lower() == 'large':
        selected_model = "llama3.2:latest"
    else:
        print("Step: Invalid model selection. Choose 'small' or 'large'.")
        logging.warning("Step: Invalid model selection. Choose 'small' or 'large'.")
        return
    print(f"Step: Model selected: {selected_model}")
    logging.info(f"Step: Model selected: {selected_model}")

    # Step 5: Call Ollama API
    print("Step: Calling Ollama API with combined text...")
    logging.info("Step: Calling Ollama API with combined text...")
    response = call_ollama(combined_text, selected_model)
    if response:
        print(f"Response from Ollama before post-processing (first 100 chars): {response[:100]}")
        logging.info(f"Response from Ollama before parsing (first 100 chars): {response[:100]}")

        # Write response to file
        prompt_name = os.path.splitext(os.path.basename(prompt_file))[0]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_dir = r"C:\school_board_library\experiments\2_modularization_Ollama\data\index_output"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"ollama_event_index_{prompt_name}_{timestamp}.txt")
        print(f"Step: Writing index output to file: {output_file}")
        logging.info(f"Step: Writing index output to file: {output_file}")
        
        # Clean and format the response before writing
        formatted_response = clean_and_format_output(response)
        if formatted_response:
            print(f"Formatted response after post-processing (first 100 chars): {formatted_response[:100]}")
            logging.info(f"Formatted response after post-processing (first 100 chars): {formatted_response[:100]}")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(formatted_response)
            logging.info(f"Cleaned output saved to file: {output_file}")  # Added confirmation of file saving
            print("Step: Index output written successfully.")
            logging.info("Step: Index output written successfully.")
        else:
            print("Step: Failed to format the model output.")
            logging.error("Step: Failed to format the model output.")
            logging.debug(f"Formatted response is None. Raw response:\n{response}")  # Added debug log for raw response
    else:
        print("Step: No response received from Ollama.")
        logging.warning("Step: No response received from Ollama.")

    end_time = time.perf_counter()
    logging.info(f"Total execution time: {end_time - start_time:.4f} seconds.")

def main():
    parser = argparse.ArgumentParser(description="Ollama Event Indexer Script")
    parser.add_argument('--prompt_file', type=str, required=True, help='Path to the prompt file.')
    parser.add_argument('--previous_output_file', type=str, required=True, help='Path to the previous model output file.')
    parser.add_argument('--model', type=str, choices=['small', 'large'], default='small', help='Model size: small or large.')
    args = parser.parse_args()

    run_indexer(args.prompt_file, args.previous_output_file, args.model)
if __name__ == "__main__":    main()