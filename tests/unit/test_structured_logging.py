import json
import logging
from io import StringIO

from src.observability.logging_json import configure_json_logging


def test_structlog_emits_json(tmp_path, capsys):
    configure_json_logging(logging.INFO)
    logging.getLogger("test").info("hello world")
    # Capture stdout via capsys
    out, _ = capsys.readouterr()
    # Ensure last non-empty line is valid JSON
    line = [line_str for line_str in out.splitlines() if l.strip()][-1]
    obj = json.loads(line_str)
    assert obj["level"] in ("info", "INFO")
    assert obj["event"] == "hello world"

