"""
Centralised settings loaded from environment variables / .env file.
We use pydantic-settings so the settings object is type-checked.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    app_name: str = "AI Interview Prep API"
    debug: bool = True

    # --- Database ---
    database_url: str = "sqlite:///./interview_prep.db"

    # --- Auth ---
    jwt_secret: str = "CHANGE_ME_IN_PRODUCTION_USE_A_LONG_RANDOM_STRING"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # --- CORS ---
    cors_origins: str = "http://localhost:3000"

    # --- AI ---
    groq_api_key: str | None = None
    openai_api_key: str | None = None
    huggingface_token: str | None = None
    whisper_model: str = "tiny.en"  # tiny.en | base.en | small.en | medium.en

    # --- Admin ---
    # Comma-separated list of emails that are automatically granted admin role
    # on signup. Useful for one-click demo / first-user setup.
    admin_emails: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def admin_emails_list(self) -> List[str]:
        return [e.strip().lower() for e in self.admin_emails.split(",") if e.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
