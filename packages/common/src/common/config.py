"""Strongly typed application configuration using Pydantic Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseAppSettings(BaseSettings):
    """Base application settings with environment variable auto-binding."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = Field(default="development", description="Runtime environment")
    log_level: str = Field(default="INFO", description="Log verbosity level")
    app_name: str = Field(default="EnterpriseApp", description="Application identifier")
    app_version: str = Field(default="1.0.0", description="Semver release")
    debug: bool = Field(default=False, description="Debug flag")
