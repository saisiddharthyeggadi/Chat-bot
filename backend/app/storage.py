from typing import Dict, List, Any
import pydantic
from .schemas import ChatContent, ContentPart

#
"""
{user_id: 
    {
        session_id: List[ChatContent]
    }
}
"""

HISTORY_STORE: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

#are we declaring the HISTORY_STORE[user_id] correctly?
def get_history(user_id: str, session_id: str) -> List[Dict[str, Any]]:
    print("In get_history")
    
    if user_id not in HISTORY_STORE:
        HISTORY_STORE[user_id] = {}
    if session_id not in HISTORY_STORE[user_id]:
        HISTORY_STORE[user_id][session_id] = []
    return HISTORY_STORE[user_id][session_id]

def add_message(user_id: str, session_id: str, role: str, text: str):
    print("In add_message")
    
    history = get_history(user_id, session_id)
    history.append({
        "role": role,
        "parts": [{"text": text}]
    })
 