"""
FastAPI application entrypoint.
Run with: uvicorn app.main:app --reload
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database.database import Base, engine
from app.utils.logger import logger

# Register all models on Base before create_all
from app.models import user, chat, study_plan, quiz, mocktest, progress, history  # noqa: F401

from app.api import auth, profile, tutor, voice, planner, quiz as quiz_router, mocktest as mocktest_router, progress as progress_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend for the AI Voice Study Coach — a multi-agent tutoring, "
    "planning, quiz, and mock-test platform with voice I/O.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path("static").mkdir(exist_ok=True)
Path("static/audio").mkdir(parents=True, exist_ok=True)
Path(settings.UPLOAD_DIR).mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(tutor.router)
app.include_router(voice.router)
app.include_router(planner.router)
app.include_router(quiz_router.router)
app.include_router(mocktest_router.router)
app.include_router(progress_router.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    logger.info("%s started — tables ensured, ready to serve.", settings.APP_NAME)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "service": settings.APP_NAME}


@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}
