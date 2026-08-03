import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure app package is importable and uses an isolated test DB
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["OPENAI_API_KEY"] = "test-key"

from app.main import app  # noqa: E402
from app.database.database import Base, engine  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    db_file = Path("test.db")
    if db_file.exists():
        db_file.unlink()


@pytest.fixture
def client():
    return TestClient(app)
