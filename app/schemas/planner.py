from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PlanGenerateRequest(BaseModel):
    exam_target: str
    subjects: list[str]
    days: int = 30
    daily_minutes: int = 60
    weak_areas: list[str] | None = None


class StudyTaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    day: datetime
    subject: str
    topic: str
    duration_minutes: int
    is_completed: bool


class StudyPlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    exam_target: str | None
    start_date: datetime
    end_date: datetime
    tasks: list[StudyTaskOut] = []


class TaskUpdateRequest(BaseModel):
    is_completed: bool
