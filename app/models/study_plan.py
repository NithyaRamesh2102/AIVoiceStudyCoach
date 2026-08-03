"""
AI-generated study plan and its daily tasks.
"""
import datetime as dt

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.database.database import Base


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    exam_target = Column(String(120), nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    raw_plan_json = Column(Text, nullable=False)  # full structured plan from AI
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    user = relationship("User", back_populates="study_plans")
    tasks = relationship("StudyTask", back_populates="plan", cascade="all, delete-orphan")


class StudyTask(Base):
    __tablename__ = "study_tasks"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("study_plans.id"), nullable=False)
    day = Column(DateTime, nullable=False)
    subject = Column(String(120), nullable=False)
    topic = Column(String(255), nullable=False)
    duration_minutes = Column(Integer, default=30)
    is_completed = Column(Boolean, default=False)

    plan = relationship("StudyPlan", back_populates="tasks")
