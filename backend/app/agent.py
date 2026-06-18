import os 
from dotenv import load_dotenv
from google import genai
from typing import AsyncGenerator, List, Dict

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

client = genai.Client(api_key=api_key)

#low latency and cost efficient model gemini 2.5 flash
model = client.models.get("gemini-2.5-flash")

async def get_chat_response_stream(
    history: List[Dict[str, str]],
    system_instruction: str = None,
) -> AsyncGenerator[str, None]:
    try:
        
    except:

    
    