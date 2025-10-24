import json
import tempfile
from pathlib import Path

from src.observability.conversation_logger import log_interaction
from src.observability.correlation import bind_correlation_id


def test_conversation_logging_to_jsonl(tmp_path):
    bind_correlation_id("cid-test")
    base_dir = tmp_path / "logs"
    p = log_interaction(
        actor="ai_editor",
        prompt="What is 2+2?",
        response="4",
        model="test-model",
        tokens_used=7,
        metadata={"foo": "bar"},
        base_dir=base_dir,
    )
    assert p.exists()
    data = [json.loads(line_str) for line_str in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert data[-1]["correlation_id"] == "cid-test"
    assert data[-1]["actor"] == "ai_editor"
    assert data[-1]["tokens_used"] == 7

