from __future__ import annotations

from pathlib import Path

from ..models import GateResult


class DiffLimitsGate:
    def check(self, gate_config: dict, artifacts_dir: Path) -> GateResult:
        max_lines = gate_config.get("max_lines", 1000)
        diff_file = artifacts_dir / gate_config.get("diff_file", "changes.diff")
        if not diff_file.exists():
            return GateResult(gate_name="diff_limits", passed=True, message="No diff file found - assuming no changes")
        try:
            with open(diff_file, encoding="utf-8") as f:
                lines = f.readlines()
            line_count = len(lines)
            if line_count > max_lines:
                return GateResult(
                    gate_name="diff_limits",
                    passed=False,
                    message=f"Diff too large: {line_count} lines (max: {max_lines})",
                    details={"line_count": line_count, "max_lines": max_lines},
                )
            return GateResult(
                gate_name="diff_limits",
                passed=True,
                message=f"Diff size acceptable: {line_count} lines",
                details={"line_count": line_count, "max_lines": max_lines},
            )
        except Exception as e:
            return GateResult(gate_name="diff_limits", passed=False, message=f"Could not read diff file: {e}")

