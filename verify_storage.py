from backend.app.storage import add_message, get_history, HISTORY_STORE
from datetime import datetime

def verify_storage():
    user_id = "guest_1234"
    session_id = "session_test"
    
    print(f"--- Initializing Session for {user_id} ---")
    add_message(user_id, session_id, "user", "Hello bot")
    
    history = get_history(user_id, session_id)
    print(f"History after user message: {history}")
    
    add_message(user_id, session_id, "model", "Hello guest")
    
    print("\n--- Verifying HISTORY_STORE Structure ---")
    session_data = HISTORY_STORE[user_id][session_id]
    print(f"Created at: {session_data['created_at']}")
    print(f"Messages count: {len(session_data['messages'])}")
    
    for i, msg in enumerate(session_data['messages']):
        print(f"Message {i+1} ({msg['role']}): {msg['parts'][0]['text']}")
        if "[" not in msg['parts'][0]['text'] or "]" not in msg['parts'][0]['text']:
            print("FAILED: Timestamp missing in message text")
        else:
            print("PASSED: Timestamp present")

if __name__ == "__main__":
    verify_storage()
