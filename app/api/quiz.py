"""
Quiz generation, retrieval, and submission/grading.
"""
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.quiz import Quiz
from app.models.user import User
from app.schemas.quiz import (
    QuizGenerateRequest,
    QuizOut,
    QuizQuestionOut,
    QuizSubmitRequest,
    QuizResultOut,
)
from app.services.quiz_service import generate_quiz, grade_quiz

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


def _to_quiz_out(quiz: Quiz) -> QuizOut:
    return QuizOut(
        id=quiz.id,
        subject=quiz.subject,
        topic=quiz.topic,
        difficulty=quiz.difficulty,
        questions=[
            QuizQuestionOut(
                id=q.id,
                question_text=q.question_text,
                options=json.loads(q.options_json),
            )
            for q in quiz.questions
        ],
    )


@router.post("/generate", response_model=QuizOut)
def generate(
    payload: QuizGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quiz = generate_quiz(db, current_user.id, payload)
    return _to_quiz_out(quiz)


@router.get("/{quiz_id}", response_model=QuizOut)
def get_quiz(quiz_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return _to_quiz_out(quiz)


@router.post("/{quiz_id}/submit", response_model=QuizResultOut)
def submit(
    quiz_id: int,
    payload: QuizSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    result = grade_quiz(db, quiz, payload)
    return QuizResultOut(**result)
