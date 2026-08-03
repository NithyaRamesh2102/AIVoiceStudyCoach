from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    name: str
    email: EmailStr
    target_exam: str | None = None
    daily_study_minutes: int = 60


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool
    created_at: datetime


class UserUpdate(BaseModel):
    name: str | None = None
    target_exam: str | None = None
    daily_study_minutes: int | None = None
