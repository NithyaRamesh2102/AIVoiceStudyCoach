"""
Aggregates progress entries and quiz history into summary statistics
for the dashboard/progress pages.
"""
import datetime as dt

from sqlalchemy.orm import Session

from app.models.progress import ProgressEntry
from app.models.quiz import Quiz


def get_progress_summary(db: Session, user_id: int) -> dict:
    entries = (
        db.query(ProgressEntry)
        .filter(ProgressEntry.user_id == user_id)
        .order_by(ProgressEntry.date.desc())
        .all()
    )

    total_minutes = sum(e.minutes_studied for e in entries)

    quizzes = (
        db.query(Quiz)
        .filter(Quiz.user_id == user_id, Quiz.score.isnot(None))
        .all()
    )
    avg_accuracy = (
        round(sum(q.score for q in quizzes) / len(quizzes), 2) if quizzes else None
    )

    subjects: dict[str, dict] = {}
    for e in entries:
        bucket = subjects.setdefault(e.subject, {"subject": e.subject, "minutes": 0, "topics": 0})
        bucket["minutes"] += e.minutes_studied
        bucket["topics"] += e.topics_covered

    streak = _compute_streak([e.date for e in entries])

    return {
        "total_minutes_studied": total_minutes,
        "average_quiz_accuracy": avg_accuracy,
        "subjects_breakdown": list(subjects.values()),
        "streak_days": streak,
    }


def _compute_streak(dates: list[dt.datetime]) -> int:
    if not dates:
        return 0
    day_set = {d.date() for d in dates}
    streak = 0
    cursor = dt.date.today()
    while cursor in day_set:
        streak += 1
        cursor -= dt.timedelta(days=1)
    return streak
