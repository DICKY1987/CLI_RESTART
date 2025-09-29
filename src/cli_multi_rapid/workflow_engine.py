#!/usr/bin/env python3
"""
Workflow Engine (spec-driven)

Lightweight, deterministic engine that:
- Loads a pipeline implementation spec (JSON)
- Performs basic validation of required sections/fields
- Creates/updates local config scaffolding from the spec
- Persists a simple pipeline state file (per spec: .pipeline_state.json)

This module complements the existing WorkflowRunner by focusing on
spec ingestion and repository setup/validation, without changing
execution semantics elsewhere.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rich.console import Console

console = Console()


STATE_FILE = Path(".pipeline_state.json")


@dataclass
class SpecSummary:
    name: str
    version: str
    total_atoms: int
    total_phases: int
    roles: int


class PipelineSpecLoader:
    """Loads and normalizes the pipeline specification JSON."""

    def load(self, spec_path: Path) -> dict[str, Any]:
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec file not found: {spec_path}")
        with spec_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data or {}

    def summarize(self, spec: dict[str, Any]) -> SpecSummary:
        meta = spec.get("metadata") or {}
        return SpecSummary(
            name=str(meta.get("specification_name", "unknown")),
            version=str(meta.get("version", "0.0.0")),
            total_atoms=int(meta.get("total_atoms", 0)),
            total_phases=int(meta.get("total_phases", 0)),
            roles=int(meta.get("total_roles", 0)),
        )


class PipelineState:
    """Simple state persistence to a single JSON file, per spec."""

    def __init__(self, path: Path = STATE_FILE):
        self.path = path

    def read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            with self.path.open("r", encoding="utf-8") as f:
                return json.load(f) or {}
        except Exception:
            return {}

    def write(self, state: dict[str, Any]) -> None:
        try:
            with self.path.open("w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            console.print(f"[yellow]Failed to persist pipeline state: {e}[/yellow]")

    def update(self, **kwargs: Any) -> dict[str, Any]:
        cur = self.read()
        cur.update(kwargs)
        self.write(cur)
        return cur


class PipelineScaffolder:
    """Generates repo config files from the spec (idempotent)."""

    def __init__(self, repo_root: Path | None = None):
        self.root = repo_root or Path.cwd()
        self.config_dir = self.root / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def ensure_pipeline_yaml(self, spec: dict[str, Any]) -> Path:
        """Create a minimal pipeline.yaml if missing, based on spec outline."""
        path = self.config_dir / "pipeline.yaml"
        if path.exists():
            return path

        # Extract a minimal view of phases/roles
        phases = list((spec.get("phases") or {}).keys())
        roles = spec.get("phases", {}).get("phase_0", {}).get("sections", {})

        content = [
            "version: 1",
            "description: Minimal pipeline config derived from spec",
            "phases:",
        ]
        for p in phases:
            content.append(f"  - id: {p}")
        content.append("roles:")
        for r in (roles or {}).keys():
            content.append(f"  - id: {r}")

        path.write_text("\n".join(content) + "\n", encoding="utf-8")
        return path

    def ensure_quality_gates_yaml(self, spec: dict[str, Any]) -> Path:
        """Create quality_gates.yaml if missing using validation requirements."""
        path = self.config_dir / "quality_gates.yaml"
        if path.exists():
            return path

        vr = spec.get("validation_requirements") or {}
        unit = vr.get("unit_tests") or {}
        integ = vr.get("integration_tests") or {}
        perf = (vr.get("performance_tests") or {}).get("benchmarks") or {}

        # Defaults if spec is partial
        coverage = int(unit.get("coverage_requirement", 85))
        scenarios = integ.get("scenarios", [])

        lines = [
            "version: 1",
            "unit_tests:",
            f"  coverage_min: {coverage}",
            "integration_tests:",
            "  scenarios:",
        ]
        for s in scenarios:
            lines.append(f"    - {s}")
        lines.append("performance:")
        for k, v in perf.items():
            lines.append(f'  {k}: "{v}"')

        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    def ensure_tools_yaml_alignment(self) -> tuple[Path, bool]:
        """Ensure tools.yaml exists (do not overwrite). Return path and created?"""
        path = self.config_dir / "tools.yaml"
        created = False
        if not path.exists():
            # Provide a minimal default; repo may already include this file.
            minimal = (
                "version: 1\n"
                "tools:\n"
                "  - name: aider\n"
                '    capabilities: ["python", "refactor"]\n'
                '    version_cmd: ["aider", "--version"]\n'
                '    health_cmd: ["aider", "--help"]\n'
                "    cost_hint: 0.6\n"
            )
            path.write_text(minimal, encoding="utf-8")
            created = True
        return path, created


class PipelineValidator:
    """Validates presence of key spec sections and local setup completeness."""

    REQUIRED_TOP_LEVEL = [
        "metadata",
        "pipeline_overview",
        "phases",
        "implementation_roadmap",
        "validation_requirements",
        "deployment_specification",
    ]

    def validate_spec(self, spec: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        missing = [k for k in self.REQUIRED_TOP_LEVEL if k not in spec]
        ok = len(missing) == 0
        details: dict[str, Any] = {"missing_sections": missing}
        # Basic sanity checks
        meta = spec.get("metadata") or {}
        for field in ("specification_name", "version"):
            if field not in meta:
                details.setdefault("metadata_missing", []).append(field)
                ok = False
        return ok, details

    def validate_local_setup(self, repo_root: Path | None = None) -> dict[str, Any]:
        root = repo_root or Path.cwd()
        checks = {
            "python_version_req": "3.9+",  # informative only
            "src_exists": (root / "src").exists(),
            "tools_yaml": (root / "config" / "tools.yaml").exists(),
            "pipeline_yaml": (root / "config" / "pipeline.yaml").exists(),
            "quality_gates_yaml": (root / "config" / "quality_gates.yaml").exists(),
        }
        checks["ok"] = all(v for k, v in checks.items() if k != "python_version_req")
        return checks


def bootstrap_from_spec(spec_path: Path) -> dict[str, Any]:
    """Load, validate, scaffold configs, and persist state summary."""
    loader = PipelineSpecLoader()
    validator = PipelineValidator()
    state = PipelineState()
    scaffolder = PipelineScaffolder()

    spec = loader.load(spec_path)
    summary = loader.summarize(spec)
    ok, details = validator.validate_spec(spec)

    # Create config scaffolding if missing
    pipeline_yaml = scaffolder.ensure_pipeline_yaml(spec)
    quality_yaml = scaffolder.ensure_quality_gates_yaml(spec)
    tools_yaml, _ = scaffolder.ensure_tools_yaml_alignment()

    setup_checks = validator.validate_local_setup()

    # Persist state
    new_state = state.update(
        spec_summary={
            "name": summary.name,
            "version": summary.version,
            "total_atoms": summary.total_atoms,
            "total_phases": summary.total_phases,
            "roles": summary.roles,
        },
        spec_validation_ok=ok,
        spec_validation_details=details,
        setup_checks=setup_checks,
        artifacts={
            "config_files": [
                str(pipeline_yaml),
                str(quality_yaml),
                str(tools_yaml),
            ]
        },
    )

    return new_state
