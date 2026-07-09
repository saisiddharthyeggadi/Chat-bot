from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from .agent import get_chat_response_stream
from .schemas import ChatRequest
from .storage import get_history, add_message
import uuid
import random
import time


app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # For testing, allow all origins. In production, specify the frontend URL.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-User-Id", "X-Session-Id"],  # Expose custom headers
)


# @app.get("/")
# @app.get("/get-chat")
#   get_response
# @app.post("/chat")
#   chat_post
# @app.get("/health")


# root endpoint
@app.get("/")
def read_root():
    return {"Hello": "World"}


# Method to get chat history
@app.get("/get-chat")
def get_response(user_id: str, session_id: str):
    history = get_history(user_id, session_id)
    return {"user_id": user_id, "session_id": session_id, "history": history}


# chat endpoint
@app.post("/chat")
async def chat_post(request: ChatRequest):
    print("In chat_post")

    if not request.user_id:
        user_id = f"guest_{random.randint(1000, 9999)}"
    else:
        user_id = request.user_id

    if not request.session_id:
        session_id = f"session_{uuid.uuid4()}"
    else:
        session_id = request.session_id

    # to /backend/app/storage.py
    add_message(user_id, session_id, "user", request.message)

    history = get_history(user_id, session_id)

    async def response_wrapper():
        full_response = ""
        first_chunk = True
        # to /backend/app/agent.py
        async for chunk in get_chat_response_stream(
            history=history, 
            system_instruction=request.system_instruction,
            provider=request.provider,
            model_name=request.model_name
        ):
            full_response += chunk
            yield chunk

        if full_response:
            add_message(user_id, session_id, "model", full_response)

    response = StreamingResponse(response_wrapper(), media_type="text/plain")
    response.headers["X-User-Id"] = user_id
    response.headers["X-Session-Id"] = session_id
    return response


# health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}
