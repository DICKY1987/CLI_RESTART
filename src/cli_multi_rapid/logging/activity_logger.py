"""Activity Logger - Real-time workflow execution logging with structured output."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ActivityLogger:
    """Write structured activity logs for real-time monitoring of workflow execution."""

    def __init__(self, log_path: Path):
        """Initialize activity logger.

        Args:
            log_path: Path to the activity log file
        """
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, level: str, message: str, **kwargs: Any) -> None:
        """Write log entry with timestamp and level.

        Args:
            level: Log level (INFO, WARNING, ERROR, DEBUG)
            message: Log message
            **kwargs: Additional structured data to include in log
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [{level}] {message}"

        # Add structured data if provided
        if kwargs:
            entry += f" {json.dumps(kwargs)}"

        # Write to file
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(entry + "\n")
        except Exception as e:
            logger.warning(f"Failed to write to activity log: {e}")

        # Also log to console for INFO level
        if level == "INFO":
            logger.info(message)
        elif level == "WARNING":
            logger.warning(message)
        elif level == "ERROR":
            logger.error(message)
        elif level == "DEBUG":
            logger.debug(message)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log INFO level message."""
        self.log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log WARNING level message."""
        self.log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log ERROR level message."""
        self.log("ERROR", message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log DEBUG level message."""
        self.log("DEBUG", message, **kwargs)

    def workflow_started(self, workflow_name: str, run_id: str, **kwargs: Any) -> None:
        """Log workflow start event."""
        self.info(
            f"Workflow started: {workflow_name}",
            run_id=run_id,
            workflow_name=workflow_name,
            **kwargs
        )

    def workflow_completed(self, workflow_name: str, run_id: str, success: bool, **kwargs: Any) -> None:
        """Log workflow completion event."""
        status = "completed successfully" if success else "failed"
        level = "INFO" if success else "ERROR"
        self.log(
            level,
            f"Workflow {status}: {workflow_name}",
            run_id=run_id,
            workflow_name=workflow_name,
            success=success,
            **kwargs
        )

    def step_started(self, step_id: str, step_name: str, actor: str, **kwargs: Any) -> None:
        """Log step start event."""
        self.info(
            f"Step started: {step_id} - {step_name}",
            step_id=step_id,
            step_name=step_name,
            actor=actor,
            **kwargs
        )

    def step_completed(self, step_id: str, step_name: str, success: bool, **kwargs: Any) -> None:
        """Log step completion event."""
        status = "completed" if success else "failed"
        level = "INFO" if success else "ERROR"
        self.log(
            level,
            f"Step {status}: {step_id} - {step_name}",
            step_id=step_id,
            step_name=step_name,
            success=success,
            **kwargs
        )

    def git_snapshot(self, snapshot: Dict[str, Any], event_type: str = "snapshot") -> None:
        """Log Git snapshot event."""
        self.info(
            f"Git {event_type}: {snapshot.get('branch', 'unknown')} @ {snapshot.get('commit_hash', 'unknown')}",
            event_type=event_type,
            **snapshot
        )
