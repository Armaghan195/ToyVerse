from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    session_id: str = Field(..., description="Chat session ID")

class ChatMessageResponse(BaseModel):
    id: Optional[int] = None
    message: str
    response: str
    session_id: str
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: list[ChatMessageResponse]
    total_messages: int
