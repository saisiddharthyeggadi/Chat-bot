from typing import Dict, List, Any
from datetime import datetime
import uuid
import pydantic
import sqlite3
import os
from .schemas import ChatContent, ContentPart

# get_history
# add_message

# Store structure (kept for backward compatibility and testing):
# {
#     user_id: {
#         session_id: {
#             "created_at": str (ISO format),
#             "messages": List[Dict[str, Any]]
#         }
#     }
# }
HISTORY_STORE: Dict[str, Dict[str, Dict[str, Any]]] = {}

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chat_history.db")

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        print(f"SQLite database initialized at: {DB_PATH}")
    except Exception as e:
        print(f"Failed to initialize SQLite database: {e}")

# Initialize the SQLite db
init_db()

def load_messages_from_db(user_id: str, session_id: str) -> List[Dict[str, Any]]:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM messages WHERE user_id = ? AND session_id = ? ORDER BY id ASC",
            (user_id, session_id)
        )
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for role, content in rows:
            messages.append({"role": role, "parts": [{"text": content}]})
        return messages
    except Exception as e:
        print(f"Error loading messages from SQLite: {e}")
        return []

def add_message_to_db(user_id: str, session_id: str, role: str, content: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (user_id, session_id, role, content) VALUES (?, ?, ?, ?)",
            (user_id, session_id, role, content)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error adding message to SQLite: {e}")

def get_history(user_id: str, session_id: str) -> List[Dict[str, Any]]:
    print(f"In get_history for user: {user_id}, session: {session_id}")

    if user_id not in HISTORY_STORE:
        HISTORY_STORE[user_id] = {}

    if session_id not in HISTORY_STORE[user_id]:
        HISTORY_STORE[user_id][session_id] = {
            "created_at": datetime.now().isoformat(),
            "messages": [],
        }
        # Populate history cache from SQLite
        db_messages = load_messages_from_db(user_id, session_id)
        if db_messages:
            HISTORY_STORE[user_id][session_id]["messages"] = db_messages

    return HISTORY_STORE[user_id][session_id]["messages"]


def add_message(user_id: str, session_id: str, role: str, text: str):
    print(f"In add_message for role: {role}")

    # Prepend timestamp to text as requested
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = f"[{timestamp}] {text}"

    # Write to SQLite
    add_message_to_db(user_id, session_id, role, formatted_text)

    # Sync back to memory HISTORY_STORE
    history = get_history(user_id, session_id)
    history.append({"role": role, "parts": [{"text": formatted_text}]})

