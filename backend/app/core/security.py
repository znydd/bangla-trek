from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings


def create_token(user_id: str, expires_delta: timedelta, token_type: str) -> str:
    payload = {
        "sub": str(user_id),
        "type": token_type,
        "exp": datetime.now(timezone.utc) + expires_delta,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: str) -> str:
    return create_token(user_id, timedelta(minutes=30), "access")


def create_refresh_token(user_id: str) -> str:
    return create_token(user_id, timedelta(days=7), "refresh")


def decode_token(token: str) -> dict:
    return jwt.decode(
        token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
    )
