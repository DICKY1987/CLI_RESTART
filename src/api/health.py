from __future__ import annotations

from datetime import timedelta
import os
import time
from typing import Any, Dict

from fastapi import APIRouter

from cli_multi_rapid.enterprise.health_checks import (
    HealthCheck,
    HealthCheckManager,
    HealthStatus,
)

router = APIRouter()


start_time = time.time()


def _with_optional_dependencies(manager: HealthCheckManager) -> None:
    # Redis readiness if configured
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        def _ping_redis() -> bool:
            try:
                import redis  # type: ignore

                client = redis.from_url(redis_url, socket_connect_timeout=1, socket_timeout=1)
                client.ping()
                return True
            except Exception:
                return False

        manager.add_check(HealthCheck("redis", _ping_redis, "Ping Redis"))


@router.get("/health")
async def health() -> Dict[str, Any]:
    manager = HealthCheckManager("cli-orchestrator")
    manager.add_default_checks()
    _with_optional_dependencies(manager)
    overall = await manager.get_overall_health()
    return {
        "status": overall.status.value,
        "message": overall.message,
        "uptime_seconds": int(time.time() - start_time),
        "version": os.getenv("FRAMEWORK_VERSION", "simplified-25ops"),
    }


@router.get("/ready")
async def ready() -> Dict[str, Any]:
    manager = HealthCheckManager("cli-orchestrator")
    manager.add_default_checks()
    _with_optional_dependencies(manager)
    results = await manager.run_all_checks()

    unhealthy = [r for r in results.values() if r.status == HealthStatus.UNHEALTHY]
    degraded = [r for r in results.values() if r.status == HealthStatus.DEGRADED]

    status = "healthy"
    if unhealthy:
        status = "unhealthy"
    elif degraded:
        status = "degraded"

    return {
        "status": status,
        "checks": {k: v.status.value for k, v in results.items()},
        "uptime_seconds": int(time.time() - start_time),
        "version": os.getenv("FRAMEWORK_VERSION", "simplified-25ops"),
    }

