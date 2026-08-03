from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ChatRequest(BaseModel):
    session_id: str
    message: str
    subject: str | None = None


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role: str
    content: str
    subject: str | None = None
    audio_url: str | None = None
    created_at: datetime


class ChatResponse(BaseModel):
    reply: str
    audio_url: str | None = None
    session_id: str
