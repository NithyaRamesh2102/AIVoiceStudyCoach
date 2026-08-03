from datetime import datetime
from pydantic import BaseModel


class ProgressSummary(BaseModel):
    total_minutes_studied: int
    average_quiz_accuracy: float | None
    subjects_breakdown: list[dict]
    streak_days: int


class ProgressEntryOut(BaseModel):
    id: int
    subject: str
    date: datetime
    minutes_studied: int
    quiz_accuracy: float | None
    topics_covered: int
