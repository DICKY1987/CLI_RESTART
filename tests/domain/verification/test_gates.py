import json
from pathlib import Path

from src.cli_multi_rapid.domain.verification.gates.diff_gate import DiffLimitsGate
from src.cli_multi_rapid.domain.verification.gates.test_gate import TestsPassGate
from src.cli_multi_rapid.domain.verification.gates.schema_gate import SchemaGate


def test_diff_limits_gate_pass(temp_dir):
    art = temp_dir / "artifacts"
    art.mkdir(parents=True, exist_ok=True)
    (art / "changes.diff").write_text("line1\nline2\n", encoding="utf-8")

    gate = DiffLimitsGate()
    res = gate.check({"type": "diff_limits", "max_lines": 5, "diff_file": "changes.diff"}, art)
    assert res.passed is True


def test_tests_pass_gate_fail_when_report_missing(temp_dir):
    art = temp_dir / "artifacts"
    art.mkdir(parents=True, exist_ok=True)
    gate = TestsPassGate()
    res = gate.check({"type": "tests_pass", "test_report": "nope.json"}, art)
    assert res.passed is False


def test_schema_gate_basic_validation(temp_dir):
    art = temp_dir / "artifacts"
    art.mkdir(parents=True, exist_ok=True)
    # Create a simple artifact that should pass basic validation
    payload = {"timestamp": "2025-10-24T01:02:03", "type": "demo"}
    (art / "demo-artifact.json").write_text(json.dumps(payload), encoding="utf-8")

    gate = SchemaGate()
    res = gate.check({"type": "schema_valid", "artifacts": ["demo-artifact.json"]}, art)
    assert res.passed is True

