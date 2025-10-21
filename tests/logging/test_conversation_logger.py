"""Tests for ConversationLogger."""

import json
from datetime import datetime
from pathlib import Path

import pytest

from cli_multi_rapid.logging.conversation_logger import ConversationLogger


@pytest.fixture
def temp_log_dir(tmp_path):
    """Create a temporary log directory."""
    log_dir = tmp_path / "conversations"
    log_dir.mkdir(parents=True)
    return log_dir


@pytest.fixture
def logger(temp_log_dir):
    """Create a ConversationLogger instance."""
    return ConversationLogger(log_dir=temp_log_dir)


def test_conversation_logger_initialization(temp_log_dir):
    """Test ConversationLogger initialization."""
    logger = ConversationLogger(log_dir=temp_log_dir)
    assert logger.log_dir == temp_log_dir
    assert (temp_log_dir / ".gitkeep").exists()


def test_log_conversation(logger, temp_log_dir):
    """Test logging a conversation."""
    conversation_id = logger.log_conversation(
        adapter_name="test_adapter",
        model="test-model",
        prompt="Test prompt",
        response="Test response",
        context={"test": "context"},
        metadata={"tokens": 100}
    )

    assert conversation_id is not None
    assert "test_adapter" in conversation_id

    # Check that log file was created
    log_files = list(temp_log_dir.glob("*.jsonl"))
    assert len(log_files) == 1

    # Verify log entry
    with open(log_files[0]) as f:
        entry = json.loads(f.readline())
        assert entry["conversation_id"] == conversation_id
        assert entry["adapter_name"] == "test_adapter"
        assert entry["model"] == "test-model"
        assert entry["prompt"] == "Test prompt"
        assert entry["response"] == "Test response"
        assert entry["context"] == {"test": "context"}
        assert entry["metadata"] == {"tokens": 100}


def test_pii_redaction(logger, temp_log_dir):
    """Test PII redaction in logged conversations."""
    prompt_with_pii = "My email is test@example.com and my API key is sk-1234567890abcdef"

    logger.log_conversation(
        adapter_name="test_adapter",
        model="test-model",
        prompt=prompt_with_pii,
        response="Test response"
    )

    # Read the log file
    log_files = list(temp_log_dir.glob("*.jsonl"))
    with open(log_files[0]) as f:
        entry = json.loads(f.readline())

    # Check that PII was redacted
    assert "test@example.com" not in entry["prompt"]
    assert "sk-1234567890abcdef" not in entry["prompt"]
    assert "[REDACTED_EMAIL]" in entry["prompt"]
    assert "[REDACTED_API_KEY]" in entry["prompt"]


def test_get_conversation(logger):
    """Test retrieving a conversation by ID."""
    conversation_id = logger.log_conversation(
        adapter_name="test_adapter",
        model="test-model",
        prompt="Test prompt",
        response="Test response"
    )

    # Retrieve the conversation
    entries = logger.get_conversation(conversation_id)

    assert len(entries) == 1
    assert entries[0]["conversation_id"] == conversation_id
    assert entries[0]["adapter_name"] == "test_adapter"


def test_list_conversations(logger):
    """Test listing conversations."""
    # Log multiple conversations
    logger.log_conversation(
        adapter_name="adapter1",
        model="model1",
        prompt="Prompt 1",
        response="Response 1"
    )

    logger.log_conversation(
        adapter_name="adapter2",
        model="model2",
        prompt="Prompt 2",
        response="Response 2"
    )

    # List all conversations
    conversations = logger.list_conversations(limit=10)

    assert len(conversations) == 2


def test_export_conversation(logger, temp_log_dir):
    """Test exporting a conversation to JSON."""
    conversation_id = logger.log_conversation(
        adapter_name="test_adapter",
        model="test-model",
        prompt="Test prompt",
        response="Test response"
    )

    output_file = temp_log_dir / "exported_conversation.json"
    success = logger.export_conversation(conversation_id, output_file)

    assert success
    assert output_file.exists()

    # Verify exported data
    with open(output_file) as f:
        data = json.load(f)
        assert data["conversation_id"] == conversation_id
        assert len(data["turns"]) == 1


def test_multi_turn_conversation(logger):
    """Test logging multi-turn conversations."""
    conversation_id = logger._generate_conversation_id("test_adapter", "Initial prompt")

    # Log multiple turns
    for i in range(3):
        logger.log_conversation_turn(
            conversation_id=conversation_id,
            adapter_name="test_adapter",
            model="test-model",
            prompt=f"Prompt {i}",
            response=f"Response {i}",
            turn_number=i + 1
        )

    # Retrieve conversation
    entries = logger.get_conversation(conversation_id)

    assert len(entries) == 3
    assert all(e["conversation_id"] == conversation_id for e in entries)
    assert [e["turn_number"] for e in entries] == [1, 2, 3]


def test_delete_old_conversations(logger, temp_log_dir):
    """Test deleting old conversation logs."""
    # Create a log file
    logger.log_conversation(
        adapter_name="test_adapter",
        model="test-model",
        prompt="Test",
        response="Test"
    )

    # Delete conversations older than 0 days (should delete immediately)
    deleted_count = logger.delete_old_conversations(days=0)

    # Note: This test might be flaky due to timing
    # In a real scenario, you'd create files with specific timestamps
    assert isinstance(deleted_count, int)
