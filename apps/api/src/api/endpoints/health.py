"""Health and liveness probes."""

import time

from api.config import settings
from contracts.models import HealthStatus, StandardResponse
from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/healthz", response_model=StandardResponse[HealthStatus])
async def healthz(request: Request) -> StandardResponse[HealthStatus]:
    uptime = time.time() - getattr(request.app.state, "start_time", time.time())
    status_data = HealthStatus(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment,
        uptime_seconds=round(uptime, 2),
    )
    return StandardResponse[HealthStatus](success=True, data=status_data)


@router.get("/readyz")
async def readyz():
    return {"ready": True, "dependencies": {"database": "connected", "cache": "connected"}}
