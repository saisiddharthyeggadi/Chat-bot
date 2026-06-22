from pydantic import BaseModel
from typing import List, Optional

class ContentPart(BaseModel):
    text: str

class ChatContent(BaseModel):
    role: str # 'user' or 'model'
    parts: List[ContentPart]

class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str
    system_instruction: Optional[str] = None