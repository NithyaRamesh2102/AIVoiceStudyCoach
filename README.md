# AI Voice Study Coach — Backend

FastAPI backend for a multi-agent AI study coach: voice/text tutoring,
AI-generated study plans, quizzes, timed mock tests, and progress
analytics.

## Stack
- **FastAPI** + **SQLAlchemy** (SQLite by default, swap `DATABASE_URL` for Postgres)
- **JWT** auth (python-jose + passlib/bcrypt)
- **OpenAI** for chat completions, Whisper (speech-to-text), and TTS (text-to-speech)
- **reportlab** for PDF report generation

## Setup

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env    # then fill in OPENAI_API_KEY and SECRET_KEY
```

## Run

```bash
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

Optional: seed a demo user (demo@studycoach.ai / Demo@1234)
```bash
python -m app.database.seed
```

## Tests

```bash
pytest -v
```

## Architecture

```
app/
├── main.py           # FastAPI app, router registration, startup hook
├── config.py          # env-based settings
├── dependencies.py    # shared FastAPI Depends (db session, current user)
├── api/                # route handlers (thin — delegate to services/agents)
├── agents/            # one class per AI capability (tutor, planner, quiz, mocktest, progress)
│                       # + coordinator.py for lightweight intent routing
├── prompts/            # externalized prompt templates used by agents
├── services/            # business logic + external integrations
│                       # (openai_service, speech_to_text, text_to_speech, pdf_service, ...)
├── models/              # SQLAlchemy ORM models
├── schemas/              # Pydantic request/response models
├── auth/                # password hashing, JWT encode/decode
├── middleware/            # get_current_user dependency
└── database/              # engine, session, seed script
```

## Key endpoints

| Area | Endpoint |
|---|---|
| Auth | `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me` |
| Profile | `GET/PUT /api/profile` |
| Tutor | `POST /api/tutor/chat`, `GET /api/tutor/history/{session_id}` |
| Voice | `POST /api/voice/ask` (multipart audio upload → transcript → spoken reply) |
| Planner | `POST /api/planner/generate`, `GET /api/planner`, `PATCH /api/planner/tasks/{id}` |
| Quiz | `POST /api/quiz/generate`, `POST /api/quiz/{id}/submit` |
| Mock test | `POST /api/mocktest/generate`, `POST /api/mocktest/{id}/submit`, `GET /api/mocktest/history` |
| Progress | `POST /api/progress/log`, `GET /api/progress/summary`, `GET /api/progress/report.pdf` |

All routes except `/api/auth/register` and `/api/auth/login` require
`Authorization: Bearer <token>`.

## Notes
- If `OPENAI_API_KEY` is missing/invalid, the quiz/planner/mocktest
  agents fall back to deterministic placeholder content instead of
  crashing, so the rest of the stack stays testable offline.
- Generated TTS audio is written to `static/audio/` and served at
  `/static/audio/<file>.mp3`.
- Swap `DATABASE_URL` in `.env` to a Postgres URL for production; the
  SQLAlchemy models are dialect-agnostic.
