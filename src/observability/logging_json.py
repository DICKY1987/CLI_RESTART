import logging
import sys
from typing import Optional

try:
    import structlog  # type: ignore
    _STRUCTLOG_AVAILABLE = True
except Exception:
    structlog = None  # type: ignore
    _STRUCTLOG_AVAILABLE = False


def configure_json_logging(level: int = logging.INFO) -> None:
    """Configure structlog for JSON Lines output and bridge stdlib logging.

    - Emits JSON objects per line to stdout
    - Includes timestamp, level, logger name, and event message
    - Merges contextvars (e.g., correlation_id) into each event
    - Bridges logging.getLogger(...) calls through structlog for consistency
    """

    if _STRUCTLOG_AVAILABLE:
        timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)

        # Configure standard logging to go through structlog ProcessorFormatter
        shared_processors = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            timestamper,
        ]

        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
            foreign_pre_chain=shared_processors,
        )

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)

        root = logging.getLogger()
        root.handlers[:] = [handler]
        root.setLevel(level)

        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.stdlib.add_log_level,
                timestamper,
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        return

    # Fallback: stdlib logger with JSON formatting
    class _JsonFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:  # noqa: D401
            import json
            from datetime import datetime, timezone

            payload = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname.lower(),
                "logger": record.name,
                "event": record.getMessage(),
            }
            return json.dumps(payload)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_JsonFormatter())
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level)


def get_logger(name: Optional[str] = None):
    """Get a logger; uses structlog if available, else stdlib logging."""
    if _STRUCTLOG_AVAILABLE:
        logger = structlog.get_logger()
        return logger.bind(logger=name) if name else logger
    return logging.getLogger(name or "app")
