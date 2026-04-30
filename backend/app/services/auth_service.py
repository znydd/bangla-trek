import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.models.user import User


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    async def exchange_code(self, code: str) -> dict:
        """Exchange the Google auth code for tokens."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
            )
            response.raise_for_status()
            return response.json()

    async def get_google_user_info(self, access_token: str) -> dict:
        """Fetch user profile from Google using the access token."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.json()

    def find_or_create_user(self, google_user: dict) -> User:
        """Upsert user from Google profile data."""
        user = (
            self.db.query(User)
            .filter(User.google_id == google_user["sub"])
            .first()
        )

        if user:
            # Update profile on each login (name/picture might change)
            user.name = google_user["name"]
            user.picture_url = google_user.get("picture")
            user.email = google_user["email"]
        else:
            user = User(
                google_id=google_user["sub"],
                email=google_user["email"],
                name=google_user["name"],
                picture_url=google_user.get("picture"),
            )
            self.db.add(user)

        self.db.commit()
        self.db.refresh(user)
        return user

    @staticmethod
    def create_tokens(user_id: str) -> tuple[str, str]:
        """Generate access and refresh JWT tokens."""
        return create_access_token(user_id), create_refresh_token(user_id)
