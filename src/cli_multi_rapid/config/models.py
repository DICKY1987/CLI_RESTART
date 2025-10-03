from __future__ import annotations

"""Pydantic settings models for application configuration."""

from typing import Optional


from pydantic_settings import BaseSettings


class AppConfig(BaseModel):
    name: str = "cli-multi-rapid"
    log_level: str = Field("INFO", pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    debug: bool = False
    api_port: int = Field(8000, ge=1, le=65535)


class WorkflowConfig(BaseModel):
    enabled: bool = True
    max_concurrent: int = Field(5, ge=1)
    timeout_seconds: int = Field(3600, ge=1)


class CostConfig(BaseModel):
    daily_limit_usd: float = Field(10.0, ge=0)
    weekly_limit_usd: float = Field(50.0, ge=0)
    monthly_limit_usd: float = Field(200.0, ge=0)
    alerts_enabled: bool = True


class ObservabilityConfig(BaseModel):
    prometheus_enabled: bool = True
    prometheus_port: int = Field(9090, ge=1, le=65535)


class RedisSettings(BaseSettings):
    """Redis connection string. Secrets must be provided via env."""

    url: Optional[str] = Field(None, env=["REDIS_URL"])  # optional; if provided we may ping


class ApiKeys(BaseSettings):
    """External API keys (optional unless features used)."""

    openai_api_key: Optional[str] = Field(None, env=["OPENAI_API_KEY"])  # noqa: S105
    anthropic_api_key: Optional[str] = Field(None, env=["ANTHROPIC_API_KEY"])  # noqa: S105
    google_api_key: Optional[str] = Field(None, env=["GOOGLE_API_KEY", "GEMINI_API_KEY"])  # noqa: S105


class Settings(BaseSettings):
    """Top-level validated settings.

    Loads from dict (YAML merged result) plus environment variables for secrets.
    """

    app: AppConfig
    workflow: WorkflowConfig
    cost: CostConfig
    observability: ObservabilityConfig

    # External services / secrets via env
    redis: RedisSettings = RedisSettings()
    apikeys: ApiKeys = ApiKeys()

    class Config:
        # Prevent unexpected fields from passing silently
        extra = "forbid"

    @validator("app")
    def _normalize_log_level(cls, v: AppConfig) -> AppConfig:
        v.log_level = v.log_level.upper()
        return v


