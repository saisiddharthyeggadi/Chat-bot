import os 
from dotenv import load_dotenv
from google import genai
from typing import AsyncGenerator, List, Dict, Any

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

client = genai.Client(api_key=api_key)

#low latency and cost efficient model gemini 2.5 flash
model = client.models.get(model="models/gemini-2.5-flash")

async def get_chat_response_stream(
    history: List[Dict[str, Any]],
    system_instruction: str = None,
) -> AsyncGenerator[str, None]:
    try:
        # print("config not done")
        config = genai.types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
        )
        # print("config done")
        
        response_stream = await client.aio.models.generate_content_stream(
            model=model.name,
            contents=history,
            config=config
        )

        async for chunk in response_stream:
            # print("almost done")
            if chunk.text:
                yield chunk.text
    
    except Exception as e:
        yield f"[BACKEND ERROR] : failed to generate stream, {str(e)} and {history}"

    
    