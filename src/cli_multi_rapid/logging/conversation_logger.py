"""
Conversation Logger - AI conversation capture with replay capability.

DEPRECATED: This module is deprecated and will be removed in a future version.
Use unified_logger.UnifiedLogger instead for all logging needs.

Captures all AI interactions including prompts, responses, context, and metadata
for debugging, compliance, and auditing purposes.
"""

import hashlib
import json
import logging
import re
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

# Emit deprecation warning on import
warnings.warn(
    "ConversationLogger is deprecated. Use unified_logger.UnifiedLogger or "
    "unified_logger.get_logger() instead.",
    DeprecationWarning,
    stacklevel=2,
)


class ConversationLogger:
    """Capture and store AI conversations in JSONL format with PII redaction."""

    # PII patterns to redact
    PII_PATTERNS = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "api_key": r"(sk-[a-zA-Z0-9]{48}|[a-zA-Z0-9]{32,})",
        "ip_address": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
    }

    def __init__(self, log_dir: Path = Path("logs/conversations")):
        """Initialize conversation logger.

        Args:
            log_dir: Directory to store conversation logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create .gitkeep to ensure directory is tracked
        gitkeep = self.log_dir / ".gitkeep"
        gitkeep.touch(exist_ok=True)

    def log_conversation(
        self,
        adapter_name: str,
        model: str,
        prompt: str,
        response: str,
        context: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
        conversation_id: Optional[str] = None,
    ) -> str:
        """Log a complete AI conversation.

        Args:
            adapter_name: Name of the adapter executing the conversation
            model: AI model used (e.g., "claude-3-5-sonnet-20241022")
            prompt: The prompt sent to the AI
            response: The AI's response
            context: Additional context (files, workflow info, etc.)
            metadata: Additional metadata (tokens, cost, duration, etc.)
            conversation_id: Optional conversation ID (generated if not provided)

        Returns:
            conversation_id: Unique identifier for this conversation
        """
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = self._generate_conversation_id(adapter_name, prompt)

        # Redact PII from prompt and response
        prompt_redacted = self._redact_pii(prompt)
        response_redacted = self._redact_pii(response)

        # Build conversation entry
        entry = {
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "adapter_name": adapter_name,
            "model": model,
            "prompt": prompt_redacted,
            "response": response_redacted,
            "prompt_length": len(prompt),
            "response_length": len(response),
            "context": context or {},
            "metadata": metadata or {},
        }

        # Write to JSONL file
        log_file = self.log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")

            logger.info(
                f"Logged conversation {conversation_id} to {log_file}",
                extra={
                    "conversation_id": conversation_id,
                    "adapter": adapter_name,
                    "model": model,
                },
            )

        except Exception as e:
            logger.error(f"Failed to write conversation log: {e}")

        return conversation_id

    def log_conversation_turn(
        self,
        conversation_id: str,
        adapter_name: str,
        model: str,
        prompt: str,
        response: str,
        turn_number: int,
        context: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log a single turn in a multi-turn conversation.

        Args:
            conversation_id: ID of the ongoing conversation
            adapter_name: Name of the adapter
            model: AI model used
            prompt: The prompt for this turn
            response: The AI's response for this turn
            turn_number: Turn number in the conversation
            context: Additional context
            metadata: Additional metadata
        """
        # Redact PII
        prompt_redacted = self._redact_pii(prompt)
        response_redacted = self._redact_pii(response)

        # Build turn entry
        entry = {
            "conversation_id": conversation_id,
            "turn_number": turn_number,
            "timestamp": datetime.now().isoformat(),
            "adapter_name": adapter_name,
            "model": model,
            "prompt": prompt_redacted,
            "response": response_redacted,
            "prompt_length": len(prompt),
            "response_length": len(response),
            "context": context or {},
            "metadata": metadata or {},
        }

        # Write to JSONL file
        log_file = self.log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")

            logger.debug(
                f"Logged turn {turn_number} for conversation {conversation_id}",
                extra={"conversation_id": conversation_id, "turn": turn_number},
            )

        except Exception as e:
            logger.error(f"Failed to write conversation turn log: {e}")

    def get_conversation(self, conversation_id: str) -> list[dict[str, Any]]:
        """Retrieve all turns of a conversation by ID.

        Args:
            conversation_id: The conversation ID to retrieve

        Returns:
            List of conversation entries in chronological order
        """
        entries = []

        # Search through all log files
        for log_file in sorted(self.log_dir.glob("*.jsonl")):
            try:
                with open(log_file, encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue

                        entry = json.loads(line)
                        if entry.get("conversation_id") == conversation_id:
                            entries.append(entry)

            except Exception as e:
                logger.warning(f"Error reading log file {log_file}: {e}")

        # Sort by timestamp and turn number if available
        entries.sort(
            key=lambda x: (x.get("timestamp", ""), x.get("turn_number", 0))
        )

        return entries

    def list_conversations(
        self,
        date: Optional[str] = None,
        adapter_name: Optional[str] = None,
        model: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """List conversations with optional filtering.

        Args:
            date: Filter by date (YYYY-MM-DD format)
            adapter_name: Filter by adapter name
            model: Filter by AI model
            limit: Maximum number of conversations to return

        Returns:
            List of conversation summaries
        """
        conversations = {}

        # Determine which log files to search
        if date:
            log_files = [self.log_dir / f"{date}.jsonl"]
        else:
            log_files = sorted(self.log_dir.glob("*.jsonl"), reverse=True)

        # Read and filter conversations
        for log_file in log_files:
            if not log_file.exists():
                continue

            try:
                with open(log_file, encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue

                        entry = json.loads(line)
                        conv_id = entry.get("conversation_id")

                        # Apply filters
                        if adapter_name and entry.get("adapter_name") != adapter_name:
                            continue
                        if model and entry.get("model") != model:
                            continue

                        # Track unique conversations
                        if conv_id not in conversations:
                            conversations[conv_id] = {
                                "conversation_id": conv_id,
                                "adapter_name": entry.get("adapter_name"),
                                "model": entry.get("model"),
                                "timestamp": entry.get("timestamp"),
                                "turns": 1,
                            }
                        else:
                            conversations[conv_id]["turns"] += 1

                        if len(conversations) >= limit:
                            break

            except Exception as e:
                logger.warning(f"Error reading log file {log_file}: {e}")

            if len(conversations) >= limit:
                break

        # Return as sorted list
        return sorted(
            conversations.values(),
            key=lambda x: x.get("timestamp", ""),
            reverse=True,
        )[:limit]

    def _generate_conversation_id(self, adapter_name: str, prompt: str) -> str:
        """Generate a unique conversation ID.

        Args:
            adapter_name: Name of the adapter
            prompt: The conversation prompt

        Returns:
            Unique conversation ID
        """
        # Use timestamp + hash of prompt for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:8]
        unique_id = str(uuid4())[:8]

        return f"{adapter_name}_{timestamp}_{prompt_hash}_{unique_id}"

    def _redact_pii(self, text: str) -> str:
        """Redact PII from text using regex patterns.

        Args:
            text: Text to redact

        Returns:
            Text with PII redacted
        """
        redacted = text

        for pii_type, pattern in self.PII_PATTERNS.items():
            redacted = re.sub(
                pattern,
                f"[REDACTED_{pii_type.upper()}]",
                redacted,
                flags=re.IGNORECASE,
            )

        return redacted

    def export_conversation(
        self, conversation_id: str, output_file: Path
    ) -> bool:
        """Export a conversation to a JSON file.

        Args:
            conversation_id: The conversation ID to export
            output_file: Path to the output file

        Returns:
            True if export succeeded, False otherwise
        """
        entries = self.get_conversation(conversation_id)

        if not entries:
            logger.warning(f"No conversation found with ID: {conversation_id}")
            return False

        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "conversation_id": conversation_id,
                        "turns": entries,
                        "exported_at": datetime.now().isoformat(),
                    },
                    f,
                    indent=2,
                )

            logger.info(f"Exported conversation {conversation_id} to {output_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to export conversation: {e}")
            return False

    def delete_old_conversations(self, days: int = 30) -> int:
        """Delete conversation logs older than specified days.

        Args:
            days: Number of days to retain

        Returns:
            Number of files deleted
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0

        for log_file in self.log_dir.glob("*.jsonl"):
            # Skip .gitkeep
            if log_file.name == ".gitkeep":
                continue

            try:
                # Parse date from filename (YYYY-MM-DD.jsonl)
                file_date_str = log_file.stem
                file_date = datetime.strptime(file_date_str, "%Y-%m-%d")

                if file_date < cutoff_date:
                    log_file.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted old conversation log: {log_file}")

            except Exception as e:
                logger.warning(f"Error processing log file {log_file}: {e}")

        logger.info(f"Deleted {deleted_count} old conversation logs")
        return deleted_count
