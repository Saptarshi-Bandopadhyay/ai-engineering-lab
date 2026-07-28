from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    project_name: str = "AI Workplace"
    environment: Literal["development", "testing", "production"] = "development"
    debug: bool = False

    version: str = "0.1.0"
    api_prefix: str = "/api/v1"

    # Automatically read from the .env file
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"), env_file_encoding="utf-8", extra="ignore"
    )


# Instantiate it once to be imported across the app
settings = Settings()
