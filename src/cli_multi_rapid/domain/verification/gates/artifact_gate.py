from __future__ import annotations

from pathlib import Path

from ..models import GateResult
from .schema_gate import verify_artifact


class ArtifactGate:
    """Generic artifact presence/validity checks (extensible)."""

    def check(self, gate_config: dict, artifacts_dir: Path) -> GateResult:
        try:
            path = gate_config.get("path")
            if not path:
                return GateResult(gate_name="artifact_gate", passed=True, message="No artifact specified")
            art_path = artifacts_dir / path if not str(path).startswith("/") else Path(path)
            if not art_path.exists():
                return GateResult(gate_name="artifact_gate", passed=False, message=f"Artifact not found: {art_path}")
            # Optional schema validation mapping
            schema = gate_config.get("schema")
            passed = True
            if schema:
                passed = verify_artifact(art_path, Path(schema))
            return GateResult(
                gate_name="artifact_gate",
                passed=bool(passed),
                message=("Artifact valid" if passed else "Artifact invalid"),
                details={"path": str(art_path)},
            )
        except Exception as e:
            return GateResult(gate_name="artifact_gate", passed=False, message=f"Artifact gate error: {e}")

