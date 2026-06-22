from pydantic import BaseModel
from typing import List, Optional

class ContentPart(BaseModel):
    text: str

class ChatContent(BaseModel):
    role: str # 'user' or 'model'
    parts: List[ContentPart]

class ChatRequest(BaseModel):
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    message: str
    system_instruction: Optional[str] = None