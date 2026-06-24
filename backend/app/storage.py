from typing import Dict, List, Any
from datetime import datetime
import uuid
import pydantic
from .schemas import ChatContent, ContentPart

# get_history
# add_message

# Store structure:
# {
#     user_id: {
#         session_id: {
#             "created_at": str (ISO format),
#             "messages": List[Dict[str, Any]]
#         }
#     }
# }
HISTORY_STORE: Dict[str, Dict[str, Dict[str, Any]]] = {}


def get_history(user_id: str, session_id: str) -> List[Dict[str, Any]]:
    print(f"In get_history for user: {user_id}, session: {session_id}")

    if user_id not in HISTORY_STORE:
        HISTORY_STORE[user_id] = {}

    if session_id not in HISTORY_STORE[user_id]:
        HISTORY_STORE[user_id][session_id] = {
            "created_at": datetime.now().isoformat(),
            "messages": [],
        }

    return HISTORY_STORE[user_id][session_id]["messages"]


def add_message(user_id: str, session_id: str, role: str, text: str):
    print(f"In add_message for role: {role}")

    history = get_history(user_id, session_id)

    # Prepend timestamp to text as requested
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = f"[{timestamp}] {text}"

    history.append({"role": role, "parts": [{"text": formatted_text}]})
