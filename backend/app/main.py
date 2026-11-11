import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import app.models.audit  # noqa: F401
from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.db.session import Base, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("canary")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema for local development
    Base.metadata.create_all(bind=engine)
    logger.info("Canary SRS backend initialized with database tables.")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Contamination Audit for Human-Written Datasets",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."},
    )


# Mount API routers
app.include_router(api_v1_router)


@app.get("/health/live")
def liveness():
    """Liveness probe: verifies process is responding."""
    return {"status": "alive"}


@app.get("/health/ready")
def readiness():
    """Readiness probe: verifies DB and Redis dependencies are operational."""
    from sqlalchemy import text

    db_healthy = True
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.warning(f"Readiness DB check failed: {e}")
        db_healthy = False

    queue_healthy = True
    if not settings.USE_IN_MEMORY_QUEUE or settings.ENVIRONMENT == "production":
        try:
            import redis

            r = redis.from_url(settings.REDIS_URL, socket_timeout=2)
            r.ping()
        except Exception as e:
            logger.warning(f"Readiness Redis check failed: {e}")
            queue_healthy = False

    if not (db_healthy and queue_healthy):
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "database": "healthy" if db_healthy else "unhealthy",
                "queue": "healthy" if queue_healthy else "unhealthy",
            },
        )

    return {
        "status": "ready",
        "database": "healthy",
        "queue": "healthy",
        "version": settings.APP_VERSION,
    }


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "health_url": "/api/v1/health",
        "readiness_url": "/health/ready",
        "liveness_url": "/health/live",
    }
