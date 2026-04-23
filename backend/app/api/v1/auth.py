from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.config import settings
from app.core.security import create_access_token, decode_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google")
async def google_login():
    """Redirect to Google consent screen."""
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        "response_type=code&"
        "scope=openid email profile&"
        "access_type=offline&"
        "prompt=consent"
    )
    return RedirectResponse(url=google_auth_url)


@router.get("/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """Handle Google OAuth callback — exchange code, upsert user, set cookies."""
    auth_service = AuthService(db)

    google_tokens = await auth_service.exchange_code(code)
    google_user = await auth_service.get_google_user_info(
        google_tokens["access_token"]
    )
    user = auth_service.find_or_create_user(google_user)

    access_token, refresh_token = auth_service.create_tokens(str(user.id))

    response = RedirectResponse(url=f"{settings.FRONTEND_URL}/auth/callback")
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.IS_PRODUCTION,
        samesite="lax",
        max_age=30 * 60,  # 30 minutes
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.IS_PRODUCTION,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,  # 7 days
        path="/api/v1/auth/refresh",
    )
    return response


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user — full DB query."""
    return current_user


@router.post("/refresh")
async def refresh_token(request: Request, db: Session = Depends(get_db)):
    """Refresh access token using refresh token cookie."""
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")

    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    new_access_token = create_access_token(str(user.id))
    response = JSONResponse({"message": "Token refreshed"})
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=settings.IS_PRODUCTION,
        samesite="lax",
        max_age=30 * 60,
        path="/",
    )
    return response


@router.post("/logout")
async def logout():
    """Clear auth cookies."""
    response = JSONResponse({"message": "Logged out"})
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/api/v1/auth/refresh")
    return response
