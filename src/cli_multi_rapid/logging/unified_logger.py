#!/usr/bin/env python3
"""
Unified Logging System

Consolidates activity logging (workflow execution) and conversation logging (AI interactions)
into a single, flexible logging system with structured output, PII redaction, and replay capabilities.

This replaces the separate activity_logger.py and conversation_logger.py modules.
"""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class PIIRedactor:
    """Handles PII (Personally Identifiable Information) redaction from logs."""

    # Regex patterns for common PII
    PATTERNS = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "api_key": r"\b(?:sk-|pk-|API[_-]?KEY[_-]?)[A-Za-z0-9_-]{20,}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        "github_token": r"\bgh[pousr]_[A-Za-z0-9_]{36,}\b",
        "jwt": r"\beyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\b",
    }

    @classmethod
    def redact(cls, text: str, keep_domain: bool = False) -> str:
        """
        Redact PII from text.

        Args:
            text: Text to redact
            keep_domain: If True, keep email domains for debugging

        Returns:
            Redacted text
        """
        if not text:
            return text

        # Email redaction (special handling for domain preservation)
        if keep_domain:
            text = re.sub(
                cls.PATTERNS["email"],
                lambda m: f"[REDACTED-EMAIL]@{m.group(0).split('@')[1]}",
                text,
            )
        else:
            text = re.sub(cls.PATTERNS["email"], "[REDACTED-EMAIL]", text)

        # Redact other patterns
        for pii_type, pattern in cls.PATTERNS.items():
            if pii_type != "email":  # Already handled
                text = re.sub(pattern, f"[REDACTED-{pii_type.upper()}]", text)

        return text


class UnifiedLogger:
    """
    Unified logging system for workflow execution and AI conversations.

    Features:
    - Structured logging with timestamps
    - Workflow and step lifecycle events
    - AI conversation capture with multi-turn support
    - PII redaction
    - JSONL format for conversation replay
    - File and console output
    """

    def __init__(
        self,
        log_dir: Union[str, Path] = "logs",
        enable_pii_redaction: bool = True,
        console_output: bool = True,
        log_level: str = "INFO",
    ):
        """
        Initialize unified logger.

        Args:
            log_dir: Directory for log files
            enable_pii_redaction: Enable PII redaction
            console_output: Enable console output
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.enable_pii_redaction = enable_pii_redaction
        self.console_output = console_output

        # Configure Python logging
        self.logger = logging.getLogger("cli_orchestrator")
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # File handlers
        self.activity_log_path = self.log_dir / "activity.log"
        self.conversation_log_path = self.log_dir / "conversations.jsonl"

        # Setup handlers
        self._setup_handlers()

        # Conversation state
        self._current_conversation_id: Optional[str] = None
        self._conversation_turns: List[Dict[str, Any]] = []

    def _setup_handlers(self) -> None:
        """Setup file and console handlers."""
        # Activity log handler (structured text)
        self.activity_handler = logging.FileHandler(self.activity_log_path, encoding="utf-8")
        self.activity_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        self.logger.addHandler(self.activity_handler)

        # Console handler (if enabled)
        if self.console_output:
            self.console_handler = logging.StreamHandler()
            self.console_handler.setFormatter(
                logging.Formatter("%(levelname)s: %(message)s")
            )
            self.logger.addHandler(self.console_handler)
        else:
            self.console_handler = None

    def _redact_if_enabled(self, text: str) -> str:
        """Apply PII redaction if enabled."""
        if self.enable_pii_redaction:
            return PIIRedactor.redact(text)
        return text

    # ========== Activity Logging Methods ==========

    def log_workflow_start(
        self, workflow_name: str, workflow_id: str, metadata: Optional[Dict] = None
    ) -> None:
        """Log workflow execution start."""
        meta_str = f" | Metadata: {metadata}" if metadata else ""
        self.logger.info(
            f"[WORKFLOW START] {workflow_name} (ID: {workflow_id}){meta_str}"
        )

    def log_workflow_complete(
        self, workflow_name: str, workflow_id: str, success: bool, duration: float
    ) -> None:
        """Log workflow execution completion."""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(
            f"[WORKFLOW {status}] {workflow_name} (ID: {workflow_id}) | Duration: {duration:.2f}s"
        )

    def log_step_start(
        self, step_id: str, step_name: str, actor: str, metadata: Optional[Dict] = None
    ) -> None:
        """Log workflow step start."""
        meta_str = f" | Metadata: {metadata}" if metadata else ""
        self.logger.info(
            f"[STEP START] {step_id}: {step_name} (Actor: {actor}){meta_str}"
        )

    def log_step_complete(
        self,
        step_id: str,
        step_name: str,
        success: bool,
        duration: float,
        tokens_used: int = 0,
    ) -> None:
        """Log workflow step completion."""
        status = "SUCCESS" if success else "FAILED"
        token_str = f" | Tokens: {tokens_used}" if tokens_used > 0 else ""
        self.logger.info(
            f"[STEP {status}] {step_id}: {step_name} | Duration: {duration:.2f}s{token_str}"
        )

    def log_adapter_execution(
        self, adapter_name: str, operation: str, result: Any
    ) -> None:
        """Log adapter execution."""
        result_summary = str(result)[:100]  # Truncate long results
        self.logger.debug(
            f"[ADAPTER] {adapter_name}.{operation} | Result: {result_summary}"
        )

    def log_error(
        self, context: str, error: Exception, additional_info: Optional[Dict] = None
    ) -> None:
        """Log error with context."""
        info_str = f" | Info: {additional_info}" if additional_info else ""
        self.logger.error(
            f"[ERROR] {context} | {type(error).__name__}: {str(error)}{info_str}"
        )

    def log_warning(self, message: str, context: Optional[str] = None) -> None:
        """Log warning."""
        context_str = f" | Context: {context}" if context else ""
        self.logger.warning(f"[WARNING] {message}{context_str}")

    def log_info(self, message: str, category: Optional[str] = None) -> None:
        """Log informational message."""
        category_str = f"[{category}] " if category else ""
        self.logger.info(f"{category_str}{message}")

    def log_debug(self, message: str, context: Optional[Dict] = None) -> None:
        """Log debug message."""
        context_str = f" | Context: {context}" if context else ""
        self.logger.debug(f"[DEBUG] {message}{context_str}")

    # ========== Conversation Logging Methods ==========

    def start_conversation(
        self,
        conversation_id: str,
        adapter: str,
        model: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        Start a new AI conversation session.

        Args:
            conversation_id: Unique conversation identifier
            adapter: Adapter name (e.g., "ai_editor", "deepseek")
            model: Model name (e.g., "claude-3-5-sonnet-20241022")
            metadata: Additional metadata
        """
        self._current_conversation_id = conversation_id
        self._conversation_turns = []

        self.logger.info(
            f"[CONVERSATION START] ID: {conversation_id} | Adapter: {adapter} | Model: {model}"
        )

        # Log conversation header to JSONL
        self._write_conversation_log(
            {
                "type": "conversation_start",
                "conversation_id": conversation_id,
                "adapter": adapter,
                "model": model,
                "metadata": metadata or {},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def log_conversation_turn(
        self,
        role: str,
        content: str,
        tokens: Optional[int] = None,
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        Log a single conversation turn (user or assistant message).

        Args:
            role: "user" or "assistant"
            content: Message content
            tokens: Token count for this turn
            metadata: Additional metadata (e.g., tool calls, function results)
        """
        if not self._current_conversation_id:
            self.logger.warning("No active conversation - call start_conversation() first")
            return

        # Redact PII from content
        redacted_content = self._redact_if_enabled(content)

        turn = {
            "type": "turn",
            "conversation_id": self._current_conversation_id,
            "role": role,
            "content": redacted_content,
            "tokens": tokens,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self._conversation_turns.append(turn)
        self._write_conversation_log(turn)

        # Log to activity log as well
        token_str = f" ({tokens} tokens)" if tokens else ""
        self.logger.debug(
            f"[CONVERSATION] {role.upper()}: {redacted_content[:100]}...{token_str}"
        )

    def end_conversation(
        self, success: bool, total_tokens: int = 0, error: Optional[str] = None
    ) -> None:
        """
        End the current conversation session.

        Args:
            success: Whether conversation completed successfully
            total_tokens: Total tokens used
            error: Error message if failed
        """
        if not self._current_conversation_id:
            self.logger.warning("No active conversation to end")
            return

        status = "SUCCESS" if success else "FAILED"
        error_str = f" | Error: {error}" if error else ""

        self.logger.info(
            f"[CONVERSATION {status}] ID: {self._current_conversation_id} | "
            f"Turns: {len(self._conversation_turns)} | "
            f"Total Tokens: {total_tokens}{error_str}"
        )

        # Log conversation end to JSONL
        self._write_conversation_log(
            {
                "type": "conversation_end",
                "conversation_id": self._current_conversation_id,
                "success": success,
                "total_tokens": total_tokens,
                "turn_count": len(self._conversation_turns),
                "error": error,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        # Reset state
        self._current_conversation_id = None
        self._conversation_turns = []

    def _write_conversation_log(self, entry: Dict[str, Any]) -> None:
        """Write conversation entry to JSONL log."""
        try:
            with open(self.conversation_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            self.logger.error(f"Failed to write conversation log: {e}")

    # ========== Replay and Retrieval Methods ==========

    def get_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve a conversation by ID.

        Args:
            conversation_id: Conversation identifier

        Returns:
            List of conversation entries (turns)
        """
        conversation = []

        if not self.conversation_log_path.exists():
            return conversation

        try:
            with open(self.conversation_log_path, encoding="utf-8") as f:
                for line in f:
                    entry = json.loads(line)
                    if entry.get("conversation_id") == conversation_id:
                        conversation.append(entry)
        except Exception as e:
            self.logger.error(f"Failed to read conversation log: {e}")

        return conversation

    def export_conversation(
        self, conversation_id: str, output_path: Union[str, Path]
    ) -> bool:
        """
        Export a conversation to a separate file.

        Args:
            conversation_id: Conversation identifier
            output_path: Output file path

        Returns:
            True if successful
        """
        conversation = self.get_conversation(conversation_id)

        if not conversation:
            self.logger.warning(f"No conversation found with ID: {conversation_id}")
            return False

        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(conversation, f, indent=2)

            self.logger.info(
                f"Exported conversation {conversation_id} to {output_path}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to export conversation: {e}")
            return False

    def close(self) -> None:
        """Close all file handlers to release file locks."""
        # Remove and close activity handler
        if hasattr(self, 'activity_handler'):
            self.logger.removeHandler(self.activity_handler)
            self.activity_handler.close()

        # Remove console handler if exists
        if hasattr(self, 'console_handler') and self.console_handler:
            self.logger.removeHandler(self.console_handler)
            self.console_handler.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup."""
        self.close()
        return False


# Global logger instance (singleton pattern)
_global_logger: Optional[UnifiedLogger] = None


def get_logger(
    log_dir: Union[str, Path] = "logs",
    enable_pii_redaction: bool = True,
    console_output: bool = True,
    log_level: str = "INFO",
) -> UnifiedLogger:
    """
    Get or create the global unified logger instance.

    Args:
        log_dir: Directory for log files
        enable_pii_redaction: Enable PII redaction
        console_output: Enable console output
        log_level: Logging level

    Returns:
        UnifiedLogger instance
    """
    global _global_logger

    if _global_logger is None:
        _global_logger = UnifiedLogger(
            log_dir=log_dir,
            enable_pii_redaction=enable_pii_redaction,
            console_output=console_output,
            log_level=log_level,
        )

    return _global_logger
