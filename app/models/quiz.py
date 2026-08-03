"""
Quiz session + individual questions/answers.
"""
import datetime as dt

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship

from app.database.database import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String(120), nullable=False)
    topic = Column(String(255), nullable=True)
    difficulty = Column(String(20), default="medium")
    score = Column(Float, nullable=True)
    total_questions = Column(Integer, default=0)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    options_json = Column(Text, nullable=False)  # JSON-encoded list of options
    correct_answer = Column(String(255), nullable=False)
    user_answer = Column(String(255), nullable=True)
    is_correct = Column(Boolean, nullable=True)
    explanation = Column(Text, nullable=True)

    quiz = relationship("Quiz", back_populates="questions")
