#!/usr/bin/env python3
"""
Tests for Unified Logging System

Verifies activity logging, conversation logging, PII redaction, and JSONL replay.
"""

import json
import tempfile
from pathlib import Path

import pytest

from cli_multi_rapid.logging.unified_logger import (
    PIIRedactor,
    UnifiedLogger,
    get_logger,
)


class TestPIIRedactor:
    """Test PII redaction functionality."""

    def test_email_redaction(self):
        """Test email address redaction."""
        text = "Contact me at user@example.com or admin@test.org"
        redacted = PIIRedactor.redact(text)

        assert "user@example.com" not in redacted
        assert "admin@test.org" not in redacted
        assert "[REDACTED-EMAIL]" in redacted

    def test_email_redaction_keep_domain(self):
        """Test email redaction with domain preservation."""
        text = "user@example.com"
        redacted = PIIRedactor.redact(text, keep_domain=True)

        assert "user" not in redacted
        assert "example.com" in redacted
        assert "[REDACTED-EMAIL]@example.com" == redacted

    def test_api_key_redaction(self):
        """Test API key redaction."""
        text = "My key is sk-1234567890abcdef1234567890abcdef12345678"
        redacted = PIIRedactor.redact(text)

        assert "sk-1234567890" not in redacted
        assert "[REDACTED-API_KEY]" in redacted

    def test_github_token_redaction(self):
        """Test GitHub token redaction."""
        text = "Token: ghp_1234567890abcdef1234567890abcdef1234"
        redacted = PIIRedactor.redact(text)

        assert "ghp_" not in redacted
        assert "[REDACTED-GITHUB_TOKEN]" in redacted

    def test_ssn_redaction(self):
        """Test SSN redaction."""
        text = "SSN: 123-45-6789"
        redacted = PIIRedactor.redact(text)

        assert "123-45-6789" not in redacted
        assert "[REDACTED-SSN]" in redacted

    def test_phone_redaction(self):
        """Test phone number redaction."""
        text = "Call 555-123-4567 or 555.987.6543"
        redacted = PIIRedactor.redact(text)

        assert "555-123-4567" not in redacted
        assert "555.987.6543" not in redacted
        assert "[REDACTED-PHONE]" in redacted

    def test_ip_address_redaction(self):
        """Test IP address redaction."""
        text = "Server at 192.168.1.1 or 10.0.0.5"
        redacted = PIIRedactor.redact(text)

        assert "192.168.1.1" not in redacted
        assert "10.0.0.5" not in redacted
        assert "[REDACTED-IP_ADDRESS]" in redacted

    def test_credit_card_redaction(self):
        """Test credit card redaction."""
        text = "Card: 1234-5678-9012-3456"
        redacted = PIIRedactor.redact(text)

        assert "1234-5678-9012-3456" not in redacted
        assert "[REDACTED-CREDIT_CARD]" in redacted

    def test_jwt_redaction(self):
        """Test JWT token redaction."""
        text = "JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc123"
        redacted = PIIRedactor.redact(text)

        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in redacted
        assert "[REDACTED-JWT]" in redacted

    def test_empty_string(self):
        """Test redaction of empty string."""
        assert PIIRedactor.redact("") == ""

    def test_no_pii(self):
        """Test text with no PII remains unchanged."""
        text = "This is a normal message with no sensitive data."
        redacted = PIIRedactor.redact(text)

        assert redacted == text


class TestUnifiedLogger:
    """Test suite for UnifiedLogger."""

    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def logger(self, temp_log_dir):
        """Create UnifiedLogger instance with proper cleanup."""
        logger = UnifiedLogger(
            log_dir=temp_log_dir, enable_pii_redaction=True, console_output=False
        )
        yield logger
        # Ensure cleanup
        logger.close()

    def test_logger_initialization(self, temp_log_dir):
        """Test logger initialization."""
        with UnifiedLogger(log_dir=temp_log_dir) as logger:
            assert logger.log_dir == temp_log_dir
            assert logger.enable_pii_redaction is True
            assert logger.activity_log_path.exists()

    def test_log_workflow_start(self, logger, temp_log_dir):
        """Test workflow start logging."""
        logger.log_workflow_start("test_workflow", "wf-001", {"key": "value"})

        # Verify log file contains entry
        with open(temp_log_dir / "activity.log", encoding="utf-8") as f:
            content = f.read()
            assert "WORKFLOW START" in content
            assert "test_workflow" in content
            assert "wf-001" in content

    def test_log_workflow_complete(self, logger, temp_log_dir):
        """Test workflow completion logging."""
        logger.log_workflow_complete("test_workflow", "wf-001", success=True, duration=5.5)

        with open(temp_log_dir / "activity.log", encoding="utf-8") as f:
            content = f.read()
            assert "WORKFLOW SUCCESS" in content
            assert "5.50s" in content

    def test_log_step_start(self, logger, temp_log_dir):
        """Test step start logging."""
        logger.log_step_start("1.001", "Test Step", "code_fixers", {"tool": "black"})

        with open(temp_log_dir / "activity.log", encoding="utf-8") as f:
            content = f.read()
            assert "STEP START" in content
            assert "1.001" in content
            assert "Test Step" in content
            assert "code_fixers" in content

    def test_log_step_complete(self, logger, temp_log_dir):
        """Test step completion logging."""
        logger.log_step_complete("1.001", "Test Step", success=True, duration=2.3, tokens_used=100)

        with open(temp_log_dir / "activity.log", encoding="utf-8") as f:
            content = f.read()
            assert "STEP SUCCESS" in content
            assert "2.30s" in content
            assert "Tokens: 100" in content

    def test_log_error(self, logger, temp_log_dir):
        """Test error logging."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            logger.log_error("Test context", e, {"detail": "test"})

        with open(temp_log_dir / "activity.log", encoding="utf-8") as f:
            content = f.read()
            assert "ERROR" in content
            assert "Test context" in content
            assert "ValueError" in content
            assert "Test error" in content

    def test_log_warning(self, logger, temp_log_dir):
        """Test warning logging."""
        logger.log_warning("Test warning", context="test_context")

        with open(temp_log_dir / "activity.log", encoding="utf-8") as f:
            content = f.read()
            assert "WARNING" in content
            assert "Test warning" in content

    def test_log_info(self, logger, temp_log_dir):
        """Test info logging."""
        logger.log_info("Test info", category="TEST")

        with open(temp_log_dir / "activity.log", encoding="utf-8") as f:
            content = f.read()
            assert "INFO" in content
            assert "Test info" in content

    def test_start_conversation(self, logger, temp_log_dir):
        """Test conversation start."""
        logger.start_conversation("conv-001", "ai_editor", "claude-3-5-sonnet", {"key": "value"})

        assert logger._current_conversation_id == "conv-001"

        # Verify JSONL log
        with open(temp_log_dir / "conversations.jsonl", encoding="utf-8") as f:
            entry = json.loads(f.readline())
            assert entry["type"] == "conversation_start"
            assert entry["conversation_id"] == "conv-001"
            assert entry["adapter"] == "ai_editor"
            assert entry["model"] == "claude-3-5-sonnet"

    def test_log_conversation_turn(self, logger, temp_log_dir):
        """Test logging conversation turns."""
        logger.start_conversation("conv-001", "ai_editor", "claude-3-5-sonnet")

        logger.log_conversation_turn("user", "Fix this bug", tokens=10)
        logger.log_conversation_turn("assistant", "Here's the fix", tokens=50)

        assert len(logger._conversation_turns) == 2

        # Verify JSONL log contains turns
        with open(temp_log_dir / "conversations.jsonl", encoding="utf-8") as f:
            lines = f.readlines()
            # First line is conversation_start, next two are turns
            turn1 = json.loads(lines[1])
            turn2 = json.loads(lines[2])

            assert turn1["type"] == "turn"
            assert turn1["role"] == "user"
            assert turn1["content"] == "Fix this bug"
            assert turn1["tokens"] == 10

            assert turn2["role"] == "assistant"
            assert turn2["content"] == "Here's the fix"
            assert turn2["tokens"] == 50

    def test_log_conversation_turn_with_pii(self, logger, temp_log_dir):
        """Test conversation turn with PII redaction."""
        logger.start_conversation("conv-001", "ai_editor", "claude-3-5-sonnet")

        logger.log_conversation_turn(
            "user",
            "Send results to user@example.com",
            tokens=10
        )

        # Verify PII is redacted in JSONL
        with open(temp_log_dir / "conversations.jsonl", encoding="utf-8") as f:
            lines = f.readlines()
            turn = json.loads(lines[1])

            assert "user@example.com" not in turn["content"]
            assert "[REDACTED-EMAIL]" in turn["content"]

    def test_end_conversation(self, logger, temp_log_dir):
        """Test ending conversation."""
        logger.start_conversation("conv-001", "ai_editor", "claude-3-5-sonnet")
        logger.log_conversation_turn("user", "Test prompt", tokens=10)
        logger.log_conversation_turn("assistant", "Test response", tokens=50)

        logger.end_conversation(success=True, total_tokens=60)

        assert logger._current_conversation_id is None
        assert len(logger._conversation_turns) == 0

        # Verify conversation_end in JSONL
        with open(temp_log_dir / "conversations.jsonl", encoding="utf-8") as f:
            lines = f.readlines()
            end_entry = json.loads(lines[-1])

            assert end_entry["type"] == "conversation_end"
            assert end_entry["success"] is True
            assert end_entry["total_tokens"] == 60
            assert end_entry["turn_count"] == 2

    def test_end_conversation_with_error(self, logger, temp_log_dir):
        """Test ending conversation with error."""
        logger.start_conversation("conv-001", "ai_editor", "claude-3-5-sonnet")

        logger.end_conversation(success=False, total_tokens=0, error="Test error")

        # Verify error in JSONL
        with open(temp_log_dir / "conversations.jsonl", encoding="utf-8") as f:
            lines = f.readlines()
            end_entry = json.loads(lines[-1])

            assert end_entry["success"] is False
            assert end_entry["error"] == "Test error"

    def test_get_conversation(self, logger):
        """Test retrieving a conversation by ID."""
        logger.start_conversation("conv-001", "ai_editor", "claude-3-5-sonnet")
        logger.log_conversation_turn("user", "Test", tokens=10)
        logger.end_conversation(success=True, total_tokens=10)

        conversation = logger.get_conversation("conv-001")

        assert len(conversation) == 3  # start + turn + end
        assert conversation[0]["type"] == "conversation_start"
        assert conversation[1]["type"] == "turn"
        assert conversation[2]["type"] == "conversation_end"

    def test_get_conversation_nonexistent(self, logger):
        """Test retrieving nonexistent conversation."""
        conversation = logger.get_conversation("nonexistent")

        assert len(conversation) == 0

    def test_export_conversation(self, logger, temp_log_dir):
        """Test exporting a conversation."""
        logger.start_conversation("conv-001", "ai_editor", "claude-3-5-sonnet")
        logger.log_conversation_turn("user", "Test", tokens=10)
        logger.end_conversation(success=True, total_tokens=10)

        output_path = temp_log_dir / "exported_conv.json"
        success = logger.export_conversation("conv-001", output_path)

        assert success
        assert output_path.exists()

        # Verify export content
        with open(output_path, encoding="utf-8") as f:
            exported = json.load(f)
            assert len(exported) == 3

    def test_export_conversation_nonexistent(self, logger, temp_log_dir):
        """Test exporting nonexistent conversation."""
        output_path = temp_log_dir / "exported_conv.json"
        success = logger.export_conversation("nonexistent", output_path)

        assert success is False
        assert not output_path.exists()

    def test_pii_redaction_disabled(self, temp_log_dir):
        """Test logger with PII redaction disabled."""
        with UnifiedLogger(
            log_dir=temp_log_dir, enable_pii_redaction=False, console_output=False
        ) as logger:
            logger.start_conversation("conv-001", "ai_editor", "claude-3-5-sonnet")
            logger.log_conversation_turn("user", "Email: user@example.com", tokens=10)

        # Verify email is NOT redacted
        with open(temp_log_dir / "conversations.jsonl", encoding="utf-8") as f:
            lines = f.readlines()
            turn = json.loads(lines[1])

            assert "user@example.com" in turn["content"]
            assert "[REDACTED-EMAIL]" not in turn["content"]


class TestGetLogger:
    """Test global logger singleton."""

    def test_get_logger_singleton(self):
        """Test get_logger returns singleton."""
        # Reset global logger
        import cli_multi_rapid.logging.unified_logger as ul
        if ul._global_logger:
            ul._global_logger.close()
        ul._global_logger = None

        logger1 = get_logger()
        logger2 = get_logger()

        assert logger1 is logger2

        # Cleanup
        logger1.close()

    def test_get_logger_with_custom_dir(self):
        """Test get_logger with custom directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Reset global logger
            import cli_multi_rapid.logging.unified_logger as ul
            if ul._global_logger:
                ul._global_logger.close()
            ul._global_logger = None

            logger = get_logger(log_dir=tmpdir)

            try:
                assert logger.log_dir == Path(tmpdir)
            finally:
                # Cleanup
                logger.close()
                ul._global_logger = None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
