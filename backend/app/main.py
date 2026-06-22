from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from .agent import get_chat_response_stream
from .schemas import ChatRequest
from .storage import get_history, add_message

app = FastAPI()

# root endpoint
@app.get("/")
def read_root():
    return {"Hello": "World"}

# test endpoint
@app.get('/chat-bot-response')
async def chat_reply():
    history = [
        {"role": "user", "parts": [{"text": "hello"}]}
    ]

    return StreamingResponse(
        get_chat_response_stream(history=history),
        media_type="text/plain"
    )

#where do we get user_id and session_id from?
# chat endpoint
@app.post("/chat")
async def chat_post(request: ChatRequest):
    print("In chat_post")

    user_id = request.user_id 
    session_id = request.session_id
    
    add_message(user_id, session_id, "user", request.message)
    
    history = get_history(user_id, session_id)

    async def response_wrapper():
        full_response = ""
        async for chunk in get_chat_response_stream(
            history=history,
            system_instruction=request.system_instruction
        ):
            full_response += chunk
            yield chunk
        
        if full_response:
            add_message(user_id, session_id, "model", full_response)

    return StreamingResponse(
        response_wrapper(),
        media_type="text/plain"
    )

# health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}

