"""
Aggregated progress / analytics snapshots per user.
"""
import datetime as dt

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.database.database import Base


class ProgressEntry(Base):
    __tablename__ = "progress_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String(120), nullable=False)
    date = Column(DateTime, default=dt.datetime.utcnow)
    minutes_studied = Column(Integer, default=0)
    quiz_accuracy = Column(Float, nullable=True)
    topics_covered = Column(Integer, default=0)

    user = relationship("User", back_populates="progress_entries")
