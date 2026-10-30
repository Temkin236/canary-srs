from fastapi import APIRouter

from app.api.v1.accuracy import router as accuracy_router
from app.api.v1.audits import router as audits_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.health import router as health_router
from app.api.v1.investigation import router as investigation_router
from app.api.v1.prepare import router as prepare_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(health_router, tags=["Health"])
api_v1_router.include_router(audits_router)
api_v1_router.include_router(prepare_router)
api_v1_router.include_router(accuracy_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(investigation_router)
