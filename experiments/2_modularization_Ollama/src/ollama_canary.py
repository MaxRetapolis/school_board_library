import argparse
import subprocess

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

def run_canary(prompt_file, model):
    print("Step: Starting Ollama Canary...")
    
    # Step 1: Load prompt from file
    print(f"Step: Loading prompt file: {prompt_file}")
    try:
        with open(prompt_file, 'r', encoding='utf-8') as file:
            prompt = file.read()
        print("Step: Prompt loaded successfully.")
    except Exception as e:
        print(f"Step: Failed to load prompt file: {e}")
        return
    
    # Step 2: Select model
    print(f"Step: Selecting model: {model}")
    if model.lower() == 'small':
        selected_model = "llama3.2:1b"
    elif model.lower() == 'large':
        selected_model = "llama3.2:latest"
    else:
        print("Step: Invalid model selection. Choose 'small' or 'large'.")
        return
    print(f"Step: Model selected: {selected_model}")
    
    # Step 3: Call Ollama API
    print("Step: Calling Ollama API...")
    response = call_ollama(prompt, selected_model)
    if response:
        print("Step: Received response from Ollama:")
        print(response)
    else:
        print("Step: No response received from Ollama.")
    
    return response

def main():
    parser = argparse.ArgumentParser(description="Ollama Canary Script")
    parser.add_argument('--prompt_file', type=str, required=True, help='Path to the prompt file.')
    parser.add_argument('--model', type=str, choices=['small', 'large'], default='small', help='Model size: small or large.')
    args = parser.parse_args()
    
    run_canary(args.prompt_file, args.model)

if __name__ == "__main__":
    main()
