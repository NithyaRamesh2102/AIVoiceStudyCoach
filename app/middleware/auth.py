"""
Request-scoped auth dependency: resolves the current user from the
Bearer token, or raises 401.
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.jwt_handler import decode_access_token
from app.auth.oauth import oauth2_scheme
from app.database.session import get_db
from app.models.user import User

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise CREDENTIALS_EXCEPTION

    user = db.query(User).filter(User.email == payload["sub"]).first()
    if user is None or not user.is_active:
        raise CREDENTIALS_EXCEPTION
    return user
