#!/usr/bin/env python3
"""
CLI Orchestrator Verifier (Backward-Compatible Wrapper)

Delegates verification to domain layer `domain.verification` components
while preserving the previous Verifier API and GateResult import path.
"""

from pathlib import Path
from typing import Any, Optional

from rich.console import Console

from .domain.verification.gate_validator import GateValidator
from .domain.verification.gates.schema_gate import verify_artifact as _verify_artifact
from .domain.verification.models import GateResult as _DomainGateResult

# Re-export GateResult to keep existing import paths working
GateResult = _DomainGateResult

console = Console()


class Verifier:
    """Validates artifacts and enforces quality gates (facade)."""

    def __init__(self):
        self.console = Console()
        self._validator = GateValidator()

    def verify_artifact(self, artifact_file: Path, schema_file: Optional[Path] = None) -> bool:
        return _verify_artifact(artifact_file, schema_file)

    def check_gates(self, gates: list[dict[str, Any]], artifacts_dir: Path = Path("artifacts")) -> list[GateResult]:
        # Provide similar logging as before
        for gate in gates:
            gate_name = gate.get("name", gate.get("type", "unknown"))
            console.print(f"[cyan]Checking gate: {gate_name}[/cyan]")
        results = self._validator.check_gates(gates, artifacts_dir)
        for result in results:
            if result.passed:
                console.print(f"[green][OK] {result.gate_name}: {result.message}[/green]")
            else:
                console.print(f"[red][FAIL] {result.gate_name}: {result.message}[/red]")
        return results
