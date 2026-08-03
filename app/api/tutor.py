"""
Voice/text tutor chat endpoint.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents.tutor_agent import TutorAgent
from app.dependencies import get_db, get_current_user
from app.models.chat import ChatMessage
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessageOut
from app.services.text_to_speech import synthesize_speech

router = APIRouter(prefix="/api/tutor", tags=["tutor"])
tutor_agent = TutorAgent()


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    with_audio: bool = False,
):
    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == current_user.id, ChatMessage.session_id == payload.session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    history_payload = [{"role": h.role, "content": h.content} for h in history]

    reply_text = tutor_agent.respond(
        message=payload.message, subject=payload.subject, history=history_payload
    )

    audio_url = None
    if with_audio:
        audio_url = synthesize_speech(reply_text)

    db.add(
        ChatMessage(
            user_id=current_user.id,
            session_id=payload.session_id,
            role="user",
            content=payload.message,
            subject=payload.subject,
        )
    )
    db.add(
        ChatMessage(
            user_id=current_user.id,
            session_id=payload.session_id,
            role="assistant",
            content=reply_text,
            subject=payload.subject,
            audio_url=audio_url,
        )
    )
    db.commit()

    return ChatResponse(reply=reply_text, audio_url=audio_url, session_id=payload.session_id)


@router.get("/history/{session_id}", response_model=list[ChatMessageOut])
def get_history(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == current_user.id, ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
