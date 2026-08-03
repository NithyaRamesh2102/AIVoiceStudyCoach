"""
Full-length timed mock test: generate, submit answers, and evaluate.
"""
import datetime as dt
import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents.mocktest_agent import MockTestAgent
from app.dependencies import get_db, get_current_user
from app.models.mocktest import MockTest
from app.models.user import User

router = APIRouter(prefix="/api/mocktest", tags=["mocktest"])
mocktest_agent = MockTestAgent()


class MockTestGenerateRequest(BaseModel):
    exam_name: str
    subjects: list[str]
    duration_minutes: int = 60
    total_questions: int = 20


class MockTestSubmitRequest(BaseModel):
    answers: dict[str, str]  # "{section_idx}:{question_idx}" -> answer


@router.post("/generate")
def generate(
    payload: MockTestGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    paper = mocktest_agent.generate_paper(
        exam_name=payload.exam_name,
        duration_minutes=payload.duration_minutes,
        subjects=payload.subjects,
        total_questions=payload.total_questions,
    )

    total_marks = sum(
        q.get("marks", 1) for section in paper.get("sections", []) for q in section.get("questions", [])
    )

    mocktest = MockTest(
        user_id=current_user.id,
        exam_name=payload.exam_name,
        duration_minutes=payload.duration_minutes,
        total_marks=total_marks,
        questions_json=json.dumps(paper),
        status="in_progress",
    )
    db.add(mocktest)
    db.commit()
    db.refresh(mocktest)

    # Strip correct answers before sending to client
    client_paper = json.loads(json.dumps(paper))
    for section in client_paper.get("sections", []):
        for q in section.get("questions", []):
            q.pop("correct_answer", None)

    return {
        "id": mocktest.id,
        "exam_name": mocktest.exam_name,
        "duration_minutes": mocktest.duration_minutes,
        "total_marks": mocktest.total_marks,
        "paper": client_paper,
    }


@router.post("/{mocktest_id}/submit")
def submit(
    mocktest_id: int,
    payload: MockTestSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mocktest = (
        db.query(MockTest)
        .filter(MockTest.id == mocktest_id, MockTest.user_id == current_user.id)
        .first()
    )
    if not mocktest:
        raise HTTPException(status_code=404, detail="Mock test not found")

    paper = json.loads(mocktest.questions_json)
    scored = 0.0
    breakdown = []

    for s_idx, section in enumerate(paper.get("sections", [])):
        for q_idx, q in enumerate(section.get("questions", [])):
            key = f"{s_idx}:{q_idx}"
            given = payload.answers.get(key)
            correct = str(q.get("correct_answer", "")).strip().lower()
            is_correct = bool(given) and given.strip().lower() == correct
            marks = q.get("marks", 1)
            if is_correct:
                scored += marks
            breakdown.append(
                {
                    "key": key,
                    "subject": section.get("subject"),
                    "given_answer": given,
                    "correct_answer": q.get("correct_answer"),
                    "is_correct": is_correct,
                    "marks": marks,
                }
            )

    mocktest.scored_marks = scored
    mocktest.answers_json = json.dumps(payload.answers)
    mocktest.status = "evaluated"
    mocktest.submitted_at = dt.datetime.utcnow()
    db.commit()

    return {
        "id": mocktest.id,
        "scored_marks": scored,
        "total_marks": mocktest.total_marks,
        "breakdown": breakdown,
    }


@router.get("/history")
def history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tests = (
        db.query(MockTest)
        .filter(MockTest.user_id == current_user.id)
        .order_by(MockTest.started_at.desc())
        .all()
    )
    return [
        {
            "id": t.id,
            "exam_name": t.exam_name,
            "status": t.status,
            "scored_marks": t.scored_marks,
            "total_marks": t.total_marks,
            "started_at": t.started_at,
            "submitted_at": t.submitted_at,
        }
        for t in tests
    ]
