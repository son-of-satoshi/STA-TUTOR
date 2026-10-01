import os
import pathlib
from google import genai
from dotenv import load_dotenv

#Load the .env file from the main folder
env_path = pathlib.Path(__file__ ).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

api_key = os.getenv( "GEMINI_API_KEY")
print(f"-> Loaded Key Prefix: {api_key[:10] if api_key else 'None'}... (Total Length: {len(api_key) if api_key else 0})")

try:
    # Initialize the Gemini client
    client = genai.Client(api_key=api_key)
    
    # Test a simple generation
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents="Say hello!"
    )
    print("\nSUCCESS! Gemini replied:")
    print(response.text)
    
except Exception as e:
    print(f"\nFAILED with error:\n{e}")