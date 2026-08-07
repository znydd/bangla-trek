from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User


async def extract_token_from_request(request: Request) -> str | None:
    """Extract token from Authorization header or access_token cookie."""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1]
    return request.cookies.get("access_token")



async def get_current_user_id(request: Request) -> str:
    """Lightweight auth — JWT-only, no DB query.

    Supports cookie 'access_token' and 'Authorization: Bearer <token>' header.
    """
    token = await extract_token_from_request(request)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        return payload["sub"]
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> User:
    """Full auth — JWT + DB query.

    Checks user exists, is_active=True, and deleted_at is None.
    """
    user = (
        db.query(User)
        .filter(User.id == user_id, User.deleted_at.is_(None))
        .first()
    )
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


async def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User | None:
    """Optional auth for public endpoints that may customize output for logged-in users."""
    token = await extract_token_from_request(request)
    if not token:
        return None
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        user = (
            db.query(User)
            .filter(User.id == user_id, User.deleted_at.is_(None))
            .first()
        )
        if user and user.is_active:
            return user
    except Exception:
        return None
    return None


def require_roles(*allowed_roles: str):
    """Dependency factory for role-based access control."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied. Required role: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker


async def get_current_admin_user(
    user: User = Depends(require_roles("admin")),
) -> User:
    return user


async def get_current_moderator_or_admin(
    user: User = Depends(require_roles("moderator", "admin")),
) -> User:
    return user

