import os
import sys

try:
    import google.generativeai as genai
except ImportError:
    print("Installing required packages...")
    os.system(f"{sys.executable} -m pip install google-generativeai")
    import google.generativeai as genai

# Get API key from environment variable or .env file
api_key = os.getenv("GOOGLE_API_KEY")

# If not in environment variables, try to read from .env file
if not api_key:
    try:
        with open("aider/.env", "r") as f:
            for line in f:
                if line.startswith("GOOGLE_API_KEY="):
                    api_key = line.strip().split("=", 1)[1].strip()
                    # Remove quotes if present
                    if api_key.startswith('"') and api_key.endswith('"'):
                        api_key = api_key[1:-1]
                    break
    except:
        pass

if not api_key:
    print("ERROR: Google API key not found!")
    print("Please set GOOGLE_API_KEY in your environment or aider/.env file")
    sys.exit(1)

print(f"Testing Google API with key: {api_key[:5]}...{api_key[-3:]}")

try:
    # Configure the library
    genai.configure(api_key=api_key)
    
    # List available models
    models = genai.list_models()
    print("\n✅ Successfully connected to Google API!")
    
    print("\nAvailable models:")
    for model in models:
        if "generateContent" in model.supported_generation_methods:
            print(f"  - {model.name}")
    
    # Test with a simple prompt
    print("\nTesting with a simple prompt...")
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say hello world")
    print(f"\nResponse: {response.text}")
    
    print("\n✅ API key is working correctly!")
    print("\nTo run Aider, use the run_aider.bat script or adjust your config files as shown.")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nPlease check your API key and internet connection.")
