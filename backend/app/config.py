from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    DATABASE_URL: str

    # Server
    UVICORN_PORT: int = 1100

    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str = "http://localhost:1100/api/v1/auth/callback"

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    # Frontend
    FRONTEND_URL: str = "http://localhost:5173"

    # Environment
    IS_PRODUCTION: bool = False


settings = Settings()
