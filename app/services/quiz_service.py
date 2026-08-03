"""
Business logic for generating and grading quizzes. Delegates prompt
construction/AI calls to the QuizAgent and handles persistence + grading.
"""
import json

from sqlalchemy.orm import Session

from app.agents.quiz_agent import QuizAgent
from app.models.quiz import Quiz, QuizQuestion
from app.schemas.quiz import QuizGenerateRequest, QuizSubmitRequest


def generate_quiz(db: Session, user_id: int, req: QuizGenerateRequest) -> Quiz:
    agent = QuizAgent()
    questions = agent.generate_questions(
        subject=req.subject,
        topic=req.topic or "general",
        difficulty=req.difficulty,
        num_questions=req.num_questions,
    )

    quiz = Quiz(
        user_id=user_id,
        subject=req.subject,
        topic=req.topic,
        difficulty=req.difficulty,
        total_questions=len(questions),
    )
    db.add(quiz)
    db.flush()  # assigns quiz.id

    for q in questions:
        db.add(
            QuizQuestion(
                quiz_id=quiz.id,
                question_text=q["question"],
                options_json=json.dumps(q["options"]),
                correct_answer=q["correct_answer"],
                explanation=q.get("explanation"),
            )
        )

    db.commit()
    db.refresh(quiz)
    return quiz


def grade_quiz(db: Session, quiz: Quiz, submission: QuizSubmitRequest) -> dict:
    answer_map = {a.question_id: a.answer for a in submission.answers}
    correct_count = 0
    breakdown = []

    for question in quiz.questions:
        given = answer_map.get(question.id)
        is_correct = bool(given) and given.strip().lower() == question.correct_answer.strip().lower()
        question.user_answer = given
        question.is_correct = is_correct
        if is_correct:
            correct_count += 1

        breakdown.append(
            {
                "question_id": question.id,
                "question": question.question_text,
                "given_answer": given,
                "correct_answer": question.correct_answer,
                "is_correct": is_correct,
                "explanation": question.explanation,
            }
        )

    total = len(quiz.questions) or 1
    score = round((correct_count / total) * 100, 2)
    quiz.score = score

    import datetime as dt
    quiz.completed_at = dt.datetime.utcnow()

    db.commit()

    return {
        "quiz_id": quiz.id,
        "score": score,
        "total_questions": total,
        "correct_count": correct_count,
        "breakdown": breakdown,
    }
