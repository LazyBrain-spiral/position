"""API service settings."""

from common.config import BaseAppSettings
from pydantic import Field


class ApiSettings(BaseAppSettings):
    """Configuration specific to API backend service."""

    api_host: str = Field(default="0.0.0.0", description="Bind host")
    api_port: int = Field(default=8000, description="Bind port")
    api_prefix: str = Field(default="/api/v1", description="Global route prefix")
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origin domains",
    )


settings = ApiSettings()
