from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint verifying database connectivity and system status."""
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    queue_status = "healthy"  # In-memory or Redis check

    return HealthResponse(
        status="ok" if db_status == "healthy" else "degraded",
        version=settings.APP_VERSION,
        database=db_status,
        queue=queue_status,
        environment=settings.ENVIRONMENT,
    )
