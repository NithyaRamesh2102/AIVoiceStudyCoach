"""
Re-exports of commonly used FastAPI dependencies, so routers can do:
    from app.dependencies import get_db, get_current_user
"""
from app.database.session import get_db  # noqa: F401
from app.middleware.auth import get_current_user  # noqa: F401
