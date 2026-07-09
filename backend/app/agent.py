import os
import asyncio
from dotenv import load_dotenv
from google import genai
from typing import AsyncGenerator, List, Dict, Any

# get_chat_response_stream
#


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

client = genai.Client(api_key=api_key)

# low latency and cost efficient model gemini 2.5 flash
# model = client.models.get(model="models/gemini-2.5-flash")


async def get_chat_response_stream(
    history: List[Dict[str, Any]],
    system_instruction: str = None,
    provider: str = None,
    model_name: str = None,
) -> AsyncGenerator[str, None]:
    max_retries = 3
    base_delay = 1  # seconds

    for attempt in range(max_retries):
        try:
            print(f"In get_chat_response_stream (attempt {attempt + 1})")

            if provider == "lm-studio":
                model = httpx.AsyncClient(
                    base_url="http://localhost:1234/v1",
                    timeout=30,
                )
            elif provider == "ollama":
                model = httpx.AsyncClient(
                    base_url="http://localhost:11434/v1",
                    timeout=30,
                )
            else:
                model = client.models.get(model="models/gemini-2.5-flash")
                config = genai.types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                )

            response_stream = await client.aio.models.generate_content_stream(
                model=model.name, contents=history, config=config
            )

            async for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
            return  # Success

        except Exception as e:
            error_str = str(e)
            if "503" in error_str or "UNAVAILABLE" in error_str:
                if attempt < max_retries - 1:
                    delay = base_delay * (2**attempt)
                    print(f"503 error, retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    continue

            yield f"[BACKEND ERROR] : failed to generate stream after {attempt + 1} attempts. Error: {error_str}"
            break
