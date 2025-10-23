"""Minimal FastAPI application exposing health and readiness endpoints.

The original project packaged a more feature rich server module, but it was
removed during repository housekeeping which caused the integration tests to
fail during import.  This lightweight reimplementation wires the existing
``src.api.health`` router into a FastAPI application so the test suite can
exercise the health probes without needing the entire production stack.
"""

from __future__ import annotations

from fastapi import FastAPI

from src.api.health import router as health_router

app = FastAPI(title="CLI Multi-Rapid Health API", version="1.0.0")
app.include_router(health_router)


__all__ = ["app"]
