from __future__ import annotations

import json
from pathlib import Path

from ..models import GateResult


class TestsPassGate:
    def check(self, gate_config: dict, artifacts_dir: Path) -> GateResult:
        test_report_file = artifacts_dir / gate_config.get("test_report", "test_results.json")
        if not test_report_file.exists():
            return GateResult(gate_name="tests_pass", passed=False, message=f"Test report not found: {test_report_file}")
        try:
            with open(test_report_file, encoding="utf-8") as f:
                test_report = json.load(f)
            tests_passed = test_report.get("tests_passed", 0)
            tests_failed = test_report.get("tests_failed", 0)
            total_tests = tests_passed + tests_failed
            if tests_failed > 0:
                return GateResult(
                    gate_name="tests_pass",
                    passed=False,
                    message=f"{tests_failed} tests failed out of {total_tests}",
                    details={"tests_passed": tests_passed, "tests_failed": tests_failed, "total_tests": total_tests},
                )
            return GateResult(
                gate_name="tests_pass",
                passed=True,
                message=f"All {tests_passed} tests passed",
                details={"tests_passed": tests_passed, "total_tests": total_tests},
            )
        except Exception as e:
            return GateResult(gate_name="tests_pass", passed=False, message=f"Could not read test report: {e}")

