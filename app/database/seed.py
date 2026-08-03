"""
Optional seed script: creates tables and a demo user.
Run with: python -m app.database.seed
"""
from app.database.database import Base, engine
from app.database.session import SessionLocal
from app.models import user as user_model  # noqa: F401  (register models)
from app.models import chat, study_plan, quiz, mocktest, progress, history  # noqa: F401
from app.auth.hashing import hash_password


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(user_model.User).filter_by(email="demo@studycoach.ai").first()
        if not existing:
            demo = user_model.User(
                name="Demo Student",
                email="demo@studycoach.ai",
                hashed_password=hash_password("Demo@1234"),
            )
            db.add(demo)
            db.commit()
            print("Seeded demo user: demo@studycoach.ai / Demo@1234")
        else:
            print("Demo user already exists.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
