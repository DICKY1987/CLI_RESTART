import uuid
from typing import Optional
from contextvars import ContextVar

try:
    import structlog  # type: ignore
    _STRUCTLOG_AVAILABLE = True
except Exception:
    structlog = None  # type: ignore
    _STRUCTLOG_AVAILABLE = False

# Context variable to hold correlation ID
_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def new_correlation_id() -> str:
    """Generate and bind a new correlation ID to the context."""
    cid = str(uuid.uuid4())
    bind_correlation_id(cid)
    return cid


def bind_correlation_id(correlation_id: str) -> None:
    """Bind an existing correlation ID to the context and structlog."""
    _correlation_id.set(correlation_id)
    if _STRUCTLOG_AVAILABLE:
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID if any."""
    return _correlation_id.get()
