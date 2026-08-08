from urllib.parse import urlencode
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.config import settings
from app.core.security import create_access_token, decode_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import DevLoginRequest, TokenResponse, UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google")
async def google_login():
    """Redirect to Google consent screen."""
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    print(f"[OAUTH DEBUG] GOOGLE_REDIRECT_URI is: '{redirect_uri}'")
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
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


@router.post("/dev-login", response_model=TokenResponse)
async def dev_login(req: DevLoginRequest, db: Session = Depends(get_db)):
    """Development-only login endpoint (disabled when IS_PRODUCTION=True)."""
    if settings.IS_PRODUCTION:
        raise HTTPException(status_code=404, detail="Not available in production")

    auth_service = AuthService(db)
    user = auth_service.create_dev_user(
        email=req.email,
        name=req.name,
        role=req.role,
    )
    access_token, refresh_token = auth_service.create_tokens(str(user.id))

    response = JSONResponse(
        content={
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserRead.model_validate(user).model_dump(mode="json"),
        }
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.IS_PRODUCTION,
        samesite="lax",
        max_age=30 * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.IS_PRODUCTION,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
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

    user = (
        db.query(User)
        .filter(User.id == payload["sub"], User.deleted_at.is_(None))
        .first()
    )
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

