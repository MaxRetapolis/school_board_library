import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in environment variables!")
    print("Please check your .env file contains: GOOGLE_API_KEY=your_key_here")
    exit(1)

try:
    # Configure the library with your API key
    genai.configure(api_key=api_key)
    
    # Test the API by listing models
    print("Testing connection to Google API...")
    models = genai.list_models()
    print("✓ Connection successful!")
    print("\nAvailable models:")
    for model in models:
        if "generateContent" in model.supported_generation_methods:
            print(f"- {model.name}")
    
    # Try a simple completion to verify full functionality
    print("\nTesting a simple completion...")
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say hello in 5 words or less")
    print(f"Response: {response.text}")
    print("\n✓ API key is working correctly!")

except Exception as e:
    print(f"ERROR: Failed to connect to Google API: {e}")
    print("Please check your API key and internet connection.")
