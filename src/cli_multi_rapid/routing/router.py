from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from rich.console import Console

from ..adapters import AdapterRegistry
from ..coordination import FileScopeManager
from .complexity_analyzer import ComplexityAnalyzer
from .models import (
    AllocationPlan,
    ComplexityAnalysis,
    ParallelRoutingPlan,
    RoutingDecision,
)
from .parallel_planner import ParallelPlanner
from .resource_allocator import ResourceAllocator


class Router:
    """Routes workflow steps to appropriate adapters (decomposed components)."""

    def __init__(
        self,
        complexity_analyzer: Optional[ComplexityAnalyzer] = None,
        parallel_planner: Optional[ParallelPlanner] = None,
        resource_allocator: Optional[ResourceAllocator] = None,
    ) -> None:
        self.console = Console()
        self.registry = AdapterRegistry()
        self._initialize_adapters()
        self.adapters = self.registry.get_available_adapters()
        self.scope_manager = FileScopeManager()
        self.performance_history: dict[str, dict[str, Any]] = {}
        self._load_performance_history()

        # Lazy import to avoid circular imports during package initialization
        from ..deterministic_engine import DeterministicEngine  # type: ignore
        self.deterministic_engine = DeterministicEngine(mode="strict")
        self.complexity_analyzer = complexity_analyzer or ComplexityAnalyzer()
        self.parallel_planner = parallel_planner or ParallelPlanner(self.scope_manager)
        # allocator needs route_step callback; we bind it after creation
        self.resource_allocator = resource_allocator or ResourceAllocator(self.route_step)

    # Backward-compatible helper used by code/tests
    def get_adapter(self, actor: str):
        return self.registry.get_adapter(actor) if actor else None

    def _initialize_adapters(self) -> None:
        adapter_count = len(self.registry.list_adapters())
        self.console.print(f"[dim]Initialized {adapter_count} adapters (lazy-loaded via factory)[/dim]")

    def _load_performance_history(self) -> None:
        try:
            state_dir = Path("state/routing")
            state_dir.mkdir(parents=True, exist_ok=True)
            history_file = state_dir / "performance_history.json"
            if history_file.exists():
                import json

                with open(history_file) as f:
                    self.performance_history = json.load(f)
        except Exception:
            self.performance_history = {}

    def _save_performance_history(self) -> None:
        try:
            state_dir = Path("state/routing")
            state_dir.mkdir(parents=True, exist_ok=True)
            history_file = state_dir / "performance_history.json"
            import json

            with open(history_file, "w") as f:
                json.dump(self.performance_history, f, indent=2)
        except Exception:
            pass

    def update_performance_metrics(
        self, adapter_name: str, execution_time: float, success: bool, tokens_used: int = 0
    ) -> None:
        if adapter_name not in self.performance_history:
            self.performance_history[adapter_name] = {
                "total_executions": 0,
                "successful_executions": 0,
                "average_time": 0.0,
                "average_tokens": 0.0,
                "success_rate": 1.0,
            }
        metrics = self.performance_history[adapter_name]
        metrics["total_executions"] += 1
        if success:
            metrics["successful_executions"] += 1
        alpha = 0.1
        metrics["average_time"] = (1 - alpha) * metrics["average_time"] + alpha * execution_time
        if tokens_used > 0:
            metrics["average_tokens"] = (1 - alpha) * metrics["average_tokens"] + alpha * tokens_used
        metrics["success_rate"] = metrics["successful_executions"] / metrics["total_executions"]
        self._save_performance_history()

    def route_step(self, step: dict[str, Any], policy: Optional[dict[str, Any]] = None) -> RoutingDecision:
        actor = step.get("actor", "unknown")
        step_name = step.get("name", "Unnamed step")

        complexity: ComplexityAnalysis = self.complexity_analyzer.analyze_step(step)
        determinism = self.deterministic_engine.analyze_step(step, context=None)

        if not self.registry.is_available(actor):
            return self._route_with_complexity_fallback(complexity, step_name)

        adapter_info = self.adapters.get(actor, {})
        adapter_type = adapter_info.get("type") or adapter_info.get("adapter_type", "unknown")

        prefer_deterministic = True
        complexity_threshold = 0.7
        if policy:
            prefer_deterministic = policy.get("prefer_deterministic", True)
            complexity_threshold = policy.get("complexity_threshold", 0.7)

        if adapter_type == "ai" and prefer_deterministic:
            try:
                if determinism.deterministic or (not determinism.issues and complexity.score < complexity_threshold):
                    alt_adapter = self._find_deterministic_alternative(actor)
                    if alt_adapter and self.registry.is_available(alt_adapter):
                        det_conf = self._calculate_deterministic_confidence(complexity, alt_adapter)
                        if det_conf > 0.6 and complexity.score <= complexity_threshold:
                            reasoning_parts = [
                                f"Prefer deterministic: routed {actor} -> {alt_adapter}",
                                f"complexity: {complexity.score:.2f}",
                            ]
                            if getattr(determinism, "deterministic", False):
                                reasoning_parts.append("deterministic analysis: PASS")
                            if getattr(determinism, "issues", None):
                                reasoning_parts.append(f"issues: {', '.join(determinism.issues)}")
                            return RoutingDecision(
                                adapter_name=alt_adapter,
                                adapter_type="deterministic",
                                reasoning="; ".join(reasoning_parts),
                                estimated_tokens=0,
                                complexity_score=complexity.score,
                                confidence=det_conf,
                                performance_hint="prefer_deterministic",
                            )
            except Exception:
                pass

        # Default decision uses adapter metadata and complexity for token estimate
        estimated_tokens = 0
        if adapter_type == "ai":
            estimated_tokens = int(500 + complexity.score * 1500)
        return RoutingDecision(
            adapter_name=actor,
            adapter_type=adapter_type or "unknown",
            reasoning=f"Direct route to {actor}",
            estimated_tokens=estimated_tokens,
            complexity_score=complexity.score,
            confidence=1.0,
        )

    def route_parallel_steps(
        self, steps: list[dict[str, Any]], policy: Optional[dict[str, Any]] = None
    ) -> ParallelRoutingPlan:
        return self.parallel_planner.create_parallel_plan(steps, lambda s: self.route_step(s, policy))

    def create_allocation_plan(
        self, workflows: list[dict[str, Any]], budget: Optional[float] = None, max_parallel: int = 3
    ) -> AllocationPlan:
        return self.resource_allocator.create_allocation_plan(workflows, budget=budget, max_parallel=max_parallel)

    def _route_with_complexity_fallback(self, complexity: ComplexityAnalysis, step_name: str) -> RoutingDecision:
        if complexity.score < 0.4:
            for adapter_name in ["code_fixers", "vscode_diagnostics", "pytest_runner"]:
                if self.registry.is_available(adapter_name):
                    return RoutingDecision(
                        adapter_name=adapter_name,
                        adapter_type="deterministic",
                        reasoning=f"Fallback to {adapter_name} for simple task (complexity: {complexity.score:.2f})",
                        estimated_tokens=0,
                        complexity_score=complexity.score,
                        confidence=0.6,
                        performance_hint="fallback_simple",
                    )
        ai_tokens = int(500 + complexity.score * 1500)
        return RoutingDecision(
            adapter_name="ai_editor",
            adapter_type="ai",
            reasoning=f"AI fallback for complex task (complexity: {complexity.score:.2f})",
            estimated_tokens=ai_tokens,
            complexity_score=complexity.score,
            confidence=0.7,
            performance_hint="fallback_complex",
        )

    def _find_deterministic_alternative(self, ai_actor: str) -> Optional[str]:
        mapping = {
            "ai_editor": "code_fixers",
            "ai_analyst": "vscode_diagnostics",
        }
        return mapping.get(ai_actor)

    def _calculate_deterministic_confidence(self, complexity: ComplexityAnalysis, adapter_name: str) -> float:
        base_confidence = complexity.deterministic_confidence
        adapter_boosts = {
            "code_fixers": {"format": 0.2, "lint": 0.1},
            "vscode_diagnostics": {"lint": 0.2, "analyze": 0.1},
            "pytest_runner": {"test": 0.2},
            "git_ops": {"read": 0.2},
        }
        if adapter_name in adapter_boosts:
            boost = adapter_boosts[adapter_name].get(complexity.operation_type, 0.0)
            base_confidence += boost
        if adapter_name in self.performance_history:
            history = self.performance_history[adapter_name]
            success_rate = history.get("success_rate", 1.0)
            base_confidence *= success_rate
        return min(base_confidence, 1.0)
