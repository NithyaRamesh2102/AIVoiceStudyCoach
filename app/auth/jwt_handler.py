"""
JWT creation and decoding.
"""
import datetime as dt

from jose import jwt, JWTError

from app.config import settings


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    expire = dt.datetime.utcnow() + dt.timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
