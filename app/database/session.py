"""
DB session factory + FastAPI dependency.
"""
from sqlalchemy.orm import sessionmaker, Session

from app.database.database import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
