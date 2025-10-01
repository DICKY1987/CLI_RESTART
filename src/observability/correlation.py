import uuid
import structlog
from contextvars import ContextVar

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
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)


def get_correlation_id() -> str | None:
    """Get the current correlation ID if any."""
    return _correlation_id.get()