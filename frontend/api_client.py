import requests
import json
from typing import Generator, List, Dict, Any

BACKEND_URL = "http://localhost:8000"

def get_history(user_id: str, session_id: str) -> Dict[str, Any]:
    response = requests.get(
        f"{BACKEND_URL}/get-chat",
        params={"user_id": user_id, "session_id": session_id}
    )
    if response.status_code == 200:
        return response.json()["history"]
    return []

def chat_stream(
    message: str,
    user_id: str = None,
    session_id: str = None,
    system_instruction: str = None
) -> Generator[Dict[str, Any], None, None]:
    payload = {
        "message": message,
        "user_id": user_id,
        "session_id": session_id,
        "system_instruction": system_instruction
    }
    
    response = requests.post(
        f"{BACKEND_URL}/chat",
        json=payload,
        stream=True
    )
    
    if response.status_code != 200:
        yield {"error": f"Error: {response.status_code} - {response.text}"}
        return

    # Get generated IDs from headers
    new_user_id = response.headers.get("X-User-Id")
    new_session_id = response.headers.get("X-Session-Id")
    
    yield {"user_id": new_user_id, "session_id": new_session_id}
    
    for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
        if chunk:
            yield {"chunk": chunk}
