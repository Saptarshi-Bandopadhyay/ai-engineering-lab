from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    project_name: str = "AI Workplace"
    environment: Literal["development", "testing", "production"] = "development"
    debug: bool = False

    version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    secret_key: str
    jwt_algorithm: str = "HS256"

    access_token_expire_minutes: int = 15

    default_llm_model: str = "gemini-flash-lite-latest"
    gemini_api_key: str
    default_embedding_model: str = "gemini-embedding-001"
    embedding_dimensions: int = 768

    # Database individual parameters
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    @property
    def database_url(self) -> URL:
        """
        Safely constructs the database URL.
        URL.create automatically URL-encodes special characters in the password.
        """
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        )

    # Automatically read from the .env file
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"), env_file_encoding="utf-8", extra="ignore"
    )


# Instantiate it once to be imported across the app
settings = Settings()
