"""
Generic activity/audit log (voice sessions, logins, plan regenerations, etc.)
"""
import datetime as dt

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey

from app.database.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
