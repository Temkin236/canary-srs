from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(default="ok")
    version: str = Field(default="0.1.0")
    database: str = Field(default="healthy")
    queue: str = Field(default="healthy")
    environment: str = Field(default="development")
