import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    print("Error: GEMINI_API_KEY not found in .env file.")
else:
    try:
        genai.configure(api_key=gemini_api_key)
        print("Attempting to list models...")
        for model in genai.list_models():
            print(model.name)
        print("Gemini API key is working and models are listed successfully!")
    except Exception as e:
        print(f"Error connecting to Gemini API: {e}")
        print("Please check your GEMINI_API_KEY in the .env file.")
