#!/usr/bin/env python3
"""
Deterministic Engine for 400-Atom Pipeline

Scaffolding to classify atoms and orchestrate phase execution leveraging
existing coordinator constructs. Keeps behavior deterministic and side-effect free.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from rich.console import Console

from .workflow_runner import CoordinatedWorkflowResult, WorkflowResult


@dataclass
class DeterminismAnalysis:
    deterministic: bool
    issues: list[str]


class DeterministicEngine:
    """Lightweight deterministic analyzer used by tests.

    Mode 'strict' applies conservative checks for non-determinism.
    """

    def __init__(self, mode: str = "strict") -> None:
        self.mode = mode

    def analyze_step(self, step: dict, context: dict | None = None) -> DeterminismAnalysis:
        issues: list[str] = []
        actor = (step.get("actor") or "").lower()
        params = step.get("with") or {}

        # Flag explicitly non-deterministic parameters
        for k in ("random", "seed", "time", "timestamp"):
            if params.get(k) is True:
                issues.append(f"param:{k}")

        # Inspect shell commands for time/entropy sources
        cmd = params.get("cmd") or params.get("command") or ""
        cmd_l = str(cmd).lower()
        if any(tok in cmd_l for tok in ["date", "openssl rand", "uuidgen", "$random"]):
            issues.append("command:time_entropy")

        deterministic = True
        if self.mode == "strict":
            # Non-deterministic if shell-like actor with risky params
            if actor in {"shell", "bash", "sh", "powershell"} and issues:
                deterministic = False
            # Deterministic for known deterministic actors
            elif actor in {"code_fixers", "pytest_runner", "vscode_diagnostics"}:
                deterministic = len(issues) == 0
            else:
                # Default: deterministic unless checks failed
                deterministic = len(issues) == 0

        return DeterminismAnalysis(deterministic=deterministic, issues=issues)

console = Console()


@dataclass
class AtomClassification:
    deterministic: list[dict[str, Any]]
    ai_required: list[dict[str, Any]]
    uncertain: list[dict[str, Any]]
    total_atoms: int
    deterministic_percentage: float


class AtomClassifier:
    """Simple rules-based classifier (placeholder) for atoms.

    Heuristics:
    - atom.get('deterministic') == True => deterministic
    - elif atom.get('type') in {'lint','format','parse','rename'} => deterministic
    - elif atom.get('type') in {'design','rewrite','synthesis'} => ai_required
    - else => uncertain
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    def classify_atoms(self, atoms: list[dict[str, Any]]) -> dict[str, Any]:
        det: list[dict[str, Any]] = []
        ai: list[dict[str, Any]] = []
        unc: list[dict[str, Any]] = []
        for a in atoms:
            if a.get("deterministic") is True:
                det.append(a)
            elif (a.get("type") or "").lower() in {"lint", "format", "parse", "rename", "schema"}:
                det.append(a)
            elif (a.get("type") or "").lower() in {"design", "rewrite", "synthesis", "analysis"}:
                ai.append(a)
            else:
                unc.append(a)

        total = len(atoms)
        pct = (len(det) / total * 100.0) if total else 0.0

        # Split into 6 coarse phases for orchestration
        phases: list[dict[str, Any]] = []
        buckets = [det, ai, unc]
        phase_names = ["deterministic-core", "ai-support", "uncertain-queue"]
        for i, bucket in enumerate(buckets):
            # chunk into two sub-phases each to reach 6 total
            mid = len(bucket) // 2
            first, second = bucket[:mid], bucket[mid:]
            phases.append({"id": f"p{i*2+1}-{phase_names[i]}-a", "atoms": first})
            phases.append({"id": f"p{i*2+2}-{phase_names[i]}-b", "atoms": second})

        return {
            "summary": AtomClassification(
                deterministic=det,
                ai_required=ai,
                uncertain=unc,
                total_atoms=total,
                deterministic_percentage=pct,
            ),
            "phases": phases,
        }


class PipelineOrchestrator:
    """Maps classified atoms to phase results using Router for costs."""

    def __init__(self, coordinator: Any, scope_manager: Any):
        self.coordinator = coordinator
        self.scope_manager = scope_manager

    def execute_phases(
        self,
        classification: dict[str, Any],
        coordination_id: str | None = None,
        execution_mode: str = "production",
    ) -> CoordinatedWorkflowResult:
        phases = classification.get("phases") or []
        start = time.time()
        workflow_results: dict[str, WorkflowResult] = {}

        for phase in phases:
            atoms: list[dict[str, Any]] = phase.get("atoms") or []
            steps = []
            # Convert atoms to pseudo-steps for routing + cost estimation
            for a in atoms:
                actor = "code_fixers" if a in classification.get("summary").deterministic else "ai_editor"
                steps.append({"id": a.get("id", "atom"), "actor": actor, "files": a.get("files")})

            # Estimate cost deterministically without external adapters
            # Simple model: deterministic=10, ai=100, uncertain=20 tokens per atom
            det_set = {id(a) for a in classification.get("summary").deterministic}
            ai_set = {id(a) for a in classification.get("summary").ai_required}
            est_tokens = 0
            for a in atoms:
                key = id(a)
                if key in det_set:
                    est_tokens += 10
                elif key in ai_set:
                    est_tokens += 100
                else:
                    est_tokens += 20

            # Build a WorkflowResult summary for this phase
            wr = WorkflowResult(
                success=True,
                error=None,
                artifacts=[],
                tokens_used=est_tokens,
                steps_completed=len(steps),
                coordination_id=coordination_id,
                execution_time=0.0,
            )
            workflow_results[phase.get("id", "phase")] = wr

        total_tokens = sum(r.tokens_used for r in workflow_results.values())
        total_time = time.time() - start

        return CoordinatedWorkflowResult(
            success=True,
            coordination_id=coordination_id or f"coord-{int(time.time())}",
            workflow_results=workflow_results,
            total_tokens_used=total_tokens,
            total_execution_time=total_time,
            conflicts_detected=[],
            parallel_efficiency=0.0,
        )
