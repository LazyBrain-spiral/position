"""Standard domain and DTO schemas for cross-service integrity."""

from datetime import UTC, datetime
from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class UserRole(str, Enum):
    """User authorization roles."""

    ADMIN = "admin"
    ENGINEER = "engineer"
    OPERATOR = "operator"
    VIEWER = "viewer"


class BaseDTO(BaseModel):
    """Base DTO enforcing strict validation and immutable JSON serialization."""

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )


class EntityMetadata(BaseDTO):
    """Metadata attached to persisted resources."""

    id: str = Field(..., description="Unique identifier (UUID or CUID)")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Creation timestamp UTC"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Last update timestamp UTC"
    )
    version: int = Field(default=1, description="Optimistic locking entity version")


class PaginationParams(BaseDTO):
    """Standardized pagination query parameters."""

    page: int = Field(default=1, ge=1, description="Page number starting at 1")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page (max 100)")


class PaginatedResponse(BaseDTO, Generic[T]):
    """Standard paginated envelope returned by list endpoints."""

    items: list[T]
    total: int = Field(..., ge=0, description="Total matching items count")
    page: int = Field(..., ge=1, description="Current page")
    page_size: int = Field(..., ge=1, description="Page size")
    total_pages: int = Field(..., ge=0, description="Total pages calculated")


class StandardResponse(BaseDTO, Generic[T]):
    """Unified API response wrapper ensuring consistent client contract."""

    success: bool = True
    data: T | None = None
    message: str | None = None
    correlation_id: str | None = None


class HealthStatus(BaseDTO):
    """Service health state schema for probes and load balancers."""

    status: str = "healthy"
    version: str
    environment: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    uptime_seconds: float
