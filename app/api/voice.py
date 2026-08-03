"""
Voice upload endpoint: accepts an audio file, transcribes it, and
optionally feeds the transcript straight into the tutor for a spoken
reply (audio in, audio/text out).
"""
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.agents.tutor_agent import TutorAgent
from app.config import settings
from app.dependencies import get_db, get_current_user
from app.models.chat import ChatMessage
from app.models.user import User
from app.schemas.chat import ChatResponse
from app.services.speech_to_text import transcribe_audio
from app.services.text_to_speech import synthesize_speech
from app.utils.constants import ALLOWED_AUDIO_TYPES
from app.utils.helper import new_session_id

router = APIRouter(prefix="/api/voice", tags=["voice"])
tutor_agent = TutorAgent()

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/ask", response_model=ChatResponse)
def voice_ask(
    audio: UploadFile = File(...),
    session_id: str | None = None,
    subject: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if audio.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported audio type: {audio.content_type}")

    session_id = session_id or new_session_id()
    dest_path = UPLOAD_DIR / f"{uuid.uuid4().hex}_{audio.filename}"
    with open(dest_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    transcript = transcribe_audio(dest_path)

    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == current_user.id, ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    history_payload = [{"role": h.role, "content": h.content} for h in history]

    reply_text = tutor_agent.respond(message=transcript, subject=subject, history=history_payload)
    audio_url = synthesize_speech(reply_text)

    db.add(
        ChatMessage(
            user_id=current_user.id,
            session_id=session_id,
            role="user",
            content=transcript,
            subject=subject,
        )
    )
    db.add(
        ChatMessage(
            user_id=current_user.id,
            session_id=session_id,
            role="assistant",
            content=reply_text,
            subject=subject,
            audio_url=audio_url,
        )
    )
    db.commit()

    return ChatResponse(reply=reply_text, audio_url=audio_url, session_id=session_id)
