from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import GateResult
from .gates.artifact_gate import ArtifactGate
from .gates.diff_gate import DiffLimitsGate
from .gates.schema_gate import SchemaGate, YamlSchemaGate
from .gates.test_gate import TestsPassGate


class GateValidator:
    """Orchestrates execution of verification gates."""

    def __init__(self) -> None:
        self._registry: dict[str, Any] = {
            "tests_pass": TestsPassGate(),
            "diff_limits": DiffLimitsGate(),
            "schema_valid": SchemaGate(),
            "yaml_schema_valid": YamlSchemaGate(),
            "artifact_gate": ArtifactGate(),
        }

    def check_gates(self, gates: list[dict[str, Any]], artifacts_dir: Path = Path("artifacts")) -> list[GateResult]:
        results: list[GateResult] = []
        artifacts_dir = Path(artifacts_dir)
        for gate_config in gates:
            gate_type = gate_config.get("type", "unknown")
            gate_name = gate_config.get("name", gate_type)
            gate = self._registry.get(gate_type)
            if not gate:
                results.append(GateResult(gate_name=gate_name, passed=False, message=f"Unknown gate type: {gate_type}"))
                continue
            try:
                result = gate.check(gate_config, artifacts_dir)
            except Exception as e:  # Defensive: isolate gate errors
                result = GateResult(gate_name=gate_name, passed=False, message=f"Gate check error: {e}")
            results.append(result)
        return results

