"""FastAPI application entrypoint with production middleware and lifecycle hooks."""

import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from common.exceptions import AppException
from common.logging import get_logger, setup_logging
from common.middleware import CorrelationIdMiddleware
from contracts.models import StandardResponse
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.config import settings
from api.endpoints.router import api_v1_router

start_time = time.time()
logger = get_logger("api.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context for startup and graceful shutdown."""
    setup_logging(log_level=settings.log_level, json_format=not settings.debug)
    logger.info("service_starting", app=settings.app_name, version=settings.app_version)
    app.state.start_time = start_time
    yield
    logger.info("service_shutdown", app=settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(CorrelationIdMiddleware)


@app.exception_handler(AppException)
async def handle_app_exception(_: Request, exc: AppException) -> JSONResponse:
    logger.warning("domain_exception", code=exc.code, message=exc.message)
    resp = StandardResponse[None](success=False, message=exc.message)
    return JSONResponse(status_code=exc.status_code, content=resp.model_dump())


@app.exception_handler(RequestValidationError)
async def handle_validation_exception(_: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning("validation_error", errors=exc.errors())
    resp = StandardResponse[list[dict]](
        success=False,
        message="Request validation failed",
        data=[{"loc": err["loc"], "msg": err["msg"], "type": err["type"]} for err in exc.errors()],
    )
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=resp.model_dump())


app.include_router(api_v1_router, prefix=settings.api_prefix)


@app.get("/", tags=["Root"])
async def root():
    return {"name": settings.app_name, "version": settings.app_version, "status": "running"}
