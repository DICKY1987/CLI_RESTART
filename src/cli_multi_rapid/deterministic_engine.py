#!/usr/bin/env python3
"""
Deterministic Engine for 400-Atom Pipeline

Scaffolding to classify atoms and orchestrate phase execution leveraging
existing coordinator constructs. Keeps behavior deterministic and side-effect free.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from rich.console import Console

from .workflow_runner import CoordinatedWorkflowResult, WorkflowResult

console = Console()


@dataclass
class AtomClassification:
    deterministic: List[Dict[str, Any]]
    ai_required: List[Dict[str, Any]]
    uncertain: List[Dict[str, Any]]
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

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def classify_atoms(self, atoms: List[Dict[str, Any]]) -> Dict[str, Any]:
        det: List[Dict[str, Any]] = []
        ai: List[Dict[str, Any]] = []
        unc: List[Dict[str, Any]] = []
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
        phases: List[Dict[str, Any]] = []
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
        classification: Dict[str, Any],
        coordination_id: Optional[str] = None,
        execution_mode: str = "production",
    ) -> CoordinatedWorkflowResult:
        phases = classification.get("phases") or []
        start = time.time()
        workflow_results: Dict[str, WorkflowResult] = {}

        for phase in phases:
            atoms: List[Dict[str, Any]] = phase.get("atoms") or []
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
