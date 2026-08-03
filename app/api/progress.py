"""
Progress dashboard: summary stats, logging study minutes, PDF export,
and an AI-generated natural language coaching summary.
"""
import datetime as dt

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents.progress_agent import ProgressAgent
from app.dependencies import get_db, get_current_user
from app.models.progress import ProgressEntry
from app.models.user import User
from app.schemas.progress import ProgressSummary
from app.services.analytics_service import get_progress_summary
from app.services.pdf_service import build_progress_report_pdf

router = APIRouter(prefix="/api/progress", tags=["progress"])
progress_agent = ProgressAgent()


class LogStudyRequest(BaseModel):
    subject: str
    minutes_studied: int
    quiz_accuracy: float | None = None
    topics_covered: int = 0


@router.post("/log")
def log_study(
    payload: LogStudyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = ProgressEntry(
        user_id=current_user.id,
        subject=payload.subject,
        date=dt.datetime.utcnow(),
        minutes_studied=payload.minutes_studied,
        quiz_accuracy=payload.quiz_accuracy,
        topics_covered=payload.topics_covered,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {"id": entry.id}


@router.get("/summary", response_model=ProgressSummary)
def summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_progress_summary(db, current_user.id)


@router.get("/summary/voice")
def summary_voice(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = get_progress_summary(db, current_user.id)
    narrative = progress_agent.summarize(data)
    return {"summary": narrative, "data": data}


@router.get("/report.pdf")
def report_pdf(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = get_progress_summary(db, current_user.id)
    pdf_bytes = build_progress_report_pdf(data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=progress_report.pdf"},
    )
