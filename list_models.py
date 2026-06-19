import os
from dotenv import load_dotenv
from google import genai

load_dotenv(dotenv_path='backend/.env')
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("GEMINI_API_KEY not found")
else:
    client = genai.Client(api_key=api_key)
    print("Listing models...")
    try:
        for model in client.models.list():
            print(f"Model: {model.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
