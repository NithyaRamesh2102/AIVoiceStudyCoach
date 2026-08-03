"""
Tutor chat history (text or transcribed voice turns).
"""
import datetime as dt

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(64), index=True, nullable=False)
    role = Column(String(20), nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    subject = Column(String(120), nullable=True)
    audio_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    user = relationship("User", back_populates="chats")
