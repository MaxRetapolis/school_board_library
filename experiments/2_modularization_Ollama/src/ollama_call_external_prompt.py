import argparse
import subprocess
import os
from datetime import datetime
import logging
import time

# Initialize logging
def initialize_logging(prompt_file):
    prompt_name = os.path.splitext(os.path.basename(prompt_file))[0]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    log_dir = r"C:\school_board_library\experiments\2_modularization_Ollama\data\logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"ollama_call_{prompt_name}_{timestamp}.log")
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

def run_canary(prompt_file, context_file, model):
    initialize_logging(prompt_file)
    start_canary = time.perf_counter()
    print("Step: Starting Ollama Canary...")
    logging.info("Step: Starting Ollama Canary...")
    
    # Step 1: Load prompt from file
    step1_start = time.perf_counter()
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
    step1_end = time.perf_counter()
    logging.info(f"Step 1 completed in {step1_end - step1_start:.4f} seconds.")
    
    # Step 2: Load context from file
    step2_start = time.perf_counter()
    print(f"Step: Loading context file: {context_file}")
    logging.info(f"Step: Loading context file: {context_file}")
    try:
        with open(context_file, 'r', encoding='utf-8') as file:
            context = file.read()
        print("Step: Context loaded successfully.")
        logging.info("Step: Context loaded successfully.")
    except Exception as e:
        print(f"Step: Failed to load context file: {e}")
        logging.error(f"Step: Failed to load context file: {e}")
        return
    step2_end = time.perf_counter()
    logging.info(f"Step 2 completed in {step2_end - step2_start:.4f} seconds.")
    
    # Step 3: Select model
    step3_start = time.perf_counter()
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
    step3_end = time.perf_counter()
    logging.info(f"Step 3 completed in {step3_end - step3_start:.4f} seconds.")
    
    # Step 4: Combine prompt and context
    step4_start = time.perf_counter()
    combined_text = prompt + "\n" + context
    print("Step: Combined prompt and context.")
    logging.info("Step: Combined prompt and context.")
    step4_end = time.perf_counter()
    logging.info(f"Step 4 completed in {step4_end - step4_start:.4f} seconds.")
    
    # Step 5: Call Ollama API
    step5_start = time.perf_counter()
    print("Step: Calling Ollama API with combined text...")
    logging.info("Step: Calling Ollama API with combined text...")
    response = call_ollama(combined_text, selected_model)
    if response:
        print("Step: Received response from Ollama:")
        print(response)
        logging.info("Step: Received response from Ollama:")
        logging.info(response)
        step5_end = time.perf_counter()
        logging.info(f"Step 5 completed in {step5_end - step5_start:.4f} seconds.")
        
        # Write response to file
        step6_start = time.perf_counter()
        prompt_name = os.path.splitext(os.path.basename(prompt_file))[0]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_dir = r"C:\school_board_library\experiments\2_modularization_Ollama\data\model_output"
        os.makedirs(output_dir, exist_ok=True)
        print(f"Step: Ensured output directory exists: {output_dir}")
        logging.info(f"Step: Ensured output directory exists: {output_dir}")
        output_file = os.path.join(output_dir, f"ollama_call_{prompt_name}_{timestamp}.txt")
        print(f"Step: Output file path: {output_file}")
        logging.info(f"Step: Output file path: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response)
        print(f"Step: Model output written to file: {output_file}")
        logging.info(f"Step: Model output written to file: {output_file}")
        step6_end = time.perf_counter()
        logging.info(f"Step 6 completed in {step6_end - step6_start:.4f} seconds.")
    else:
        step5_end = time.perf_counter()
        logging.info(f"Step 5 completed in {step5_end - step5_start:.4f} seconds.")
        print("Step: No response received from Ollama.")
        logging.warning("Step: No response received from Ollama.")
    
    end_canary = time.perf_counter()
    logging.info(f"Total execution time: {end_canary - start_canary:.4f} seconds.")
    
    return response

def main():
    parser = argparse.ArgumentParser(description="Ollama Canary Script")
    parser.add_argument('--prompt_file', type=str, required=True, help='Path to the prompt file.')
    parser.add_argument('--context_file', type=str, required=True, help='Path to the context file.')
    parser.add_argument('--model', type=str, choices=['small', 'large'], default='small', help='Model size: small or large.')
    args = parser.parse_args()
    
    run_canary(args.prompt_file, args.context_file, args.model)

if __name__ == "__main__":
    main()

# Note: When running the script, ensure to wrap the file paths in quotes if they contain spaces.
# Example:
# python c:/school_board_library/experiments/2_modularization_Ollama/src/ollama_call_external_prompt.py --prompt_file "c:/school_board_library/experiments/2_modularization_Ollama/prompts/prompt_entities_index.txt" --context_file "c:/school_board_library/experiments/2_modularization_Ollama/inbound_documents/081324 BOARD BUZZ_converted.txt" --model small
