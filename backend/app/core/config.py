import os
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_NAME: str = "Canary SRS"
    APP_VERSION: str = "0.1.0"

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    DATABASE_URL: str = "sqlite:///./canary.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_IN_MEMORY_QUEUE: bool = True

    STORAGE_PATH: str = "./data/storage"
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    MAX_RECORDS_COUNT: int = 10_000

    DEFAULT_RETENTION_DAYS: int = 7
    SECRET_KEY: str = "canary-development-secret-key-32-bytes-minimum"
    AI_SPENDING_CAP_PER_AUDIT_USD: float = 5.00

    GEMINI_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

# Ensure storage path exists
os.makedirs(settings.STORAGE_PATH, exist_ok=True)
