from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from .agent import get_chat_response_stream

app = FastAPI()

# root endpoint
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get('/chat-bot-response')
async def chat_reply():
    history = [
        {"role": "user", "parts": [{"text": "hello"}]}
    ]

    return StreamingResponse(
        get_chat_response_stream(history=history),
        media_type="text/plain"
    )

# health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}

