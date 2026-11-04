"""Application configuration and environment settings."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
_CANONICAL_DB_PATH = (_BACKEND_DIR / "swms_dev.db").as_posix()


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables or .env."""

    PROJECT_NAME: str = "Smart Waste Management System API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/swms_db"
    SQLITE_FALLBACK_URL: str = f"sqlite:///{_CANONICAL_DB_PATH}"
    JWT_SECRET: str = "bilcode-swms-super-secret-jwt-key-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1440 minutes / 24 hours
    UPLOAD_DIR: str = str(_BACKEND_DIR / "uploads" / "reports")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


settings = Settings()
