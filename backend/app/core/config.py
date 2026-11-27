import os
from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_NAME: str = "Canary SRS"
    APP_VERSION: str = "0.1.0"

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"
    ALLOWED_ORIGINS: Union[List[str], str] = ["http://localhost:5173", "http://localhost:3000"]

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

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: object) -> object:
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                try:
                    import json

                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

# Ensure storage path exists
os.makedirs(settings.STORAGE_PATH, exist_ok=True)
