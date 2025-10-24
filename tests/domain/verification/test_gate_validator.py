from pathlib import Path

from src.cli_multi_rapid.domain.verification.gate_validator import GateValidator


def test_gate_validator_runs_known_and_unknown_gates(temp_dir):
    art = temp_dir / "artifacts"
    art.mkdir(parents=True, exist_ok=True)
    (art / "changes.diff").write_text("line1\n", encoding="utf-8")

    gv = GateValidator()
    gates = [
        {"type": "diff_limits", "name": "Diff", "max_lines": 10, "diff_file": "changes.diff"},
        {"type": "nonexistent_gate", "name": "Nope"},
    ]
    results = gv.check_gates(gates, art)
    assert len(results) == 2
    assert results[0].passed is True
    assert results[1].passed is False

