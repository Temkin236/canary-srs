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


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "health_url": "/api/v1/health",
    }
