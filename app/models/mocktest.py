"""
Timed full-length mock test attempts.
"""
import datetime as dt

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.database.database import Base


class MockTest(Base):
    __tablename__ = "mocktests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exam_name = Column(String(150), nullable=False)
    duration_minutes = Column(Integer, default=60)
    total_marks = Column(Float, default=0)
    scored_marks = Column(Float, nullable=True)
    questions_json = Column(Text, nullable=False)  # full generated paper
    answers_json = Column(Text, nullable=True)     # submitted answers
    status = Column(String(20), default="in_progress")  # in_progress | submitted | evaluated
    started_at = Column(DateTime, default=dt.datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="mocktests")
