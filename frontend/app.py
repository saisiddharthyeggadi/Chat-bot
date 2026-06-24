import streamlit as st
import uuid
from api_client import chat_stream, get_history

st.set_page_config(page_title="Gemini AI Chatbot", page_icon="🤖", layout="wide")

# Custom CSS for premium look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    .stTextInput > div > div > input {
        background-color: #262730;
        color: #e0e0e0;
        border-radius: 10px;
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .user-message {
        background-color: #1e3a8a;
    }
    .assistant-message {
        background-color: #1f2937;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Gemini AI Chatbot")
st.markdown("---")

#Initializing Session State 
if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{uuid.uuid4().hex[:8]}"
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{uuid.uuid4().hex[:8]}"
if "messages" not in st.session_state:
    st.session_state.messages = []

#Sidebar
with st.sidebar:
    st.header("Settings")
    system_instruction = st.text_area(
        "System Instruction",
        placeholder="e.g. You are a helpful AI assistant.",
        value="You are a helpful and concise AI assistant."
    )
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.session_state.session_id = f"session_{uuid.uuid4().hex[:8]}"
        st.rerun()

#Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("What's on your mind?"):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response with streaming
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Start streaming
        stream = chat_stream(
            message=prompt,
            user_id=st.session_state.user_id,
            session_id=st.session_state.session_id,
            system_instruction=system_instruction
        )
        
        first_chunk = True
        for data in stream:
            if "error" in data:
                st.error(data["error"])
                break
            
            if "user_id" in data:
                st.session_state.user_id = data["user_id"]
                st.session_state.session_id = data["session_id"]
                continue
                
            if "chunk" in data:
                full_response += data["chunk"]
                response_placeholder.markdown(full_response + "▌")
        
        response_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
