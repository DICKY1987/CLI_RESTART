import logging
import sys
from typing import Optional

import structlog


def configure_json_logging(level: int = logging.INFO) -> None:
    """Configure structlog for JSON Lines output and bridge stdlib logging.

    - Emits JSON objects per line to stdout
    - Includes timestamp, level, logger name, and event message
    - Merges contextvars (e.g., correlation_id) into each event
    - Bridges logging.getLogger(...) calls through structlog for consistency
    """

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


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """Get a structlog logger with optional name bound."""
    logger = structlog.get_logger()
    return logger.bind(logger=name) if name else logger