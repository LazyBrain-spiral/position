"""API v1 master router."""

from fastapi import APIRouter

from .health import router as health_router
from .resources import router as resources_router

api_v1_router = APIRouter()
api_v1_router.include_router(health_router, prefix="/health", tags=["Health & Readiness"])
api_v1_router.include_router(resources_router, prefix="/resources", tags=["Domain Resources"])
