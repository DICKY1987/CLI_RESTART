#!/usr/bin/env python3
"""
CLI Orchestrator Router System

Routes workflow steps between deterministic tools and AI adapters based on
configured policies and step requirements.
"""

import glob
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from rich.console import Console

from .adapters import AdapterRegistry
from .adapters.ai_analyst import AIAnalystAdapter
from .adapters.ai_editor import AIEditorAdapter
from .adapters.code_fixers import CodeFixersAdapter
from .adapters.pytest_runner import PytestRunnerAdapter
from .adapters.vscode_diagnostics import VSCodeDiagnosticsAdapter
from .coordination import FileClaim, FileScopeManager, ScopeConflict, ScopeMode

console = Console()


@dataclass
class RoutingDecision:
    """Result of routing decision for a workflow step."""

    adapter_name: str
    adapter_type: str  # "deterministic" or "ai"
    reasoning: str
    estimated_tokens: int = 0
    complexity_score: float = 0.0
    confidence: float = 1.0
    performance_hint: Optional[str] = None


@dataclass
class ParallelRoutingPlan:
    """Plan for parallel execution of multiple steps."""

    routing_decisions: List[Tuple[Dict[str, Any], RoutingDecision]]
    execution_groups: List[List[int]]  # Groups of step indices that can run in parallel
    total_estimated_cost: int = 0
    conflicts: List[ScopeConflict] = None
    resource_allocation: Dict[str, List[int]] = (
        None  # adapter_name -> list of step indices
    )

    def __post_init__(self):
        if self.conflicts is None:
            self.conflicts = []
        if self.resource_allocation is None:
            self.resource_allocation = {}


@dataclass
class ComplexityAnalysis:
    """Analysis of step complexity for routing decisions."""

    score: float  # 0.0 (simple) to 1.0 (complex)
    factors: Dict[str, float]  # Individual complexity factors
    file_count: int = 0
    estimated_file_size: int = 0  # bytes
    operation_type: str = "unknown"
    deterministic_confidence: float = 0.0


@dataclass
class AllocationPlan:
    """Resource allocation plan for coordinated workflows."""

    assignments: Dict[str, Dict[str, Any]]  # step_id -> allocation info
    total_estimated_cost: int = 0
    estimated_usd_cost: float = 0.0
    within_budget: bool = True
    parallel_groups: List[List[str]] = None

    def __post_init__(self):
        if self.parallel_groups is None:
            self.parallel_groups = []


class Router:
    """Routes workflow steps to appropriate adapters."""

    def __init__(self):
        self.console = Console()
        self.registry = AdapterRegistry()
        self._initialize_adapters()
        self.adapters = self.registry.get_available_adapters()
        self.scope_manager = FileScopeManager()
        self.performance_history = {}  # adapter_name -> performance metrics
        self._load_performance_history()

    def _initialize_adapters(self) -> None:
        """Initialize available adapters in the registry."""
        # Register deterministic adapters
        self.registry.register(CodeFixersAdapter())
        self.registry.register(PytestRunnerAdapter())
        self.registry.register(VSCodeDiagnosticsAdapter())
        from .adapters.git_ops import GitOpsAdapter

        self.registry.register(GitOpsAdapter())
        from .adapters.github_integration import GitHubIntegrationAdapter

        self.registry.register(GitHubIntegrationAdapter())

        # Register tool adapter bridges
        from .adapters.tool_adapter_bridge import ToolAdapterBridge

        self.registry.register(ToolAdapterBridge("vcs"))
        self.registry.register(ToolAdapterBridge("containers"))
        self.registry.register(ToolAdapterBridge("editor"))
        self.registry.register(ToolAdapterBridge("js_runtime"))
        self.registry.register(ToolAdapterBridge("ai_cli"))
        self.registry.register(ToolAdapterBridge("python_quality"))
        self.registry.register(ToolAdapterBridge("precommit"))

        # Register AI-powered adapters
        self.registry.register(AIEditorAdapter())
        self.registry.register(AIAnalystAdapter())

        # Register Codex pipeline adapters
        from .adapters.backup_manager import BackupManagerAdapter
        from .adapters.bundle_loader import BundleLoaderAdapter
        from .adapters.contract_validator import ContractValidatorAdapter
        from .adapters.enhanced_bundle_applier import EnhancedBundleApplierAdapter
        from .adapters.state_capture import StateCaptureAdapter

        self.registry.register(ContractValidatorAdapter())
        self.registry.register(StateCaptureAdapter())
        self.registry.register(BackupManagerAdapter())
        self.registry.register(BundleLoaderAdapter())
        self.registry.register(EnhancedBundleApplierAdapter())

        # Register verification gate adapters
        from .adapters.certificate_generator import CertificateGeneratorAdapter
        from .adapters.import_resolver import ImportResolverAdapter
        from .adapters.security_scanner import SecurityScannerAdapter
        from .adapters.syntax_validator import SyntaxValidatorAdapter
        from .adapters.type_checker import TypeCheckerAdapter

        self.registry.register(SyntaxValidatorAdapter())
        self.registry.register(ImportResolverAdapter())
        self.registry.register(TypeCheckerAdapter())
        self.registry.register(SecurityScannerAdapter())
        self.registry.register(CertificateGeneratorAdapter())

        # Register verifier adapter (quality gates)
        from .adapters.verifier_adapter import VerifierAdapter

        self.registry.register(VerifierAdapter())

        self.console.print(
            f"[dim]Initialized {len(self.registry.list_adapters())} adapters[/dim]"
        )

    def _load_performance_history(self) -> None:
        """Load performance history for adapters from state files."""
        try:
            state_dir = Path("state/routing")
            state_dir.mkdir(parents=True, exist_ok=True)

            history_file = state_dir / "performance_history.json"
            if history_file.exists():
                import json
                with open(history_file, 'r') as f:
                    self.performance_history = json.load(f)
        except Exception:
            # Non-fatal if loading fails
            self.performance_history = {}

    def _save_performance_history(self) -> None:
        """Save performance history for adapters."""
        try:
            state_dir = Path("state/routing")
            state_dir.mkdir(parents=True, exist_ok=True)

            history_file = state_dir / "performance_history.json"
            import json
            with open(history_file, 'w') as f:
                json.dump(self.performance_history, f, indent=2)
        except Exception:
            # Non-fatal if saving fails
            pass

    def update_performance_metrics(
        self, adapter_name: str, execution_time: float, success: bool, tokens_used: int = 0
    ) -> None:
        """Update performance metrics for an adapter."""
        if adapter_name not in self.performance_history:
            self.performance_history[adapter_name] = {
                "total_executions": 0,
                "successful_executions": 0,
                "average_time": 0.0,
                "average_tokens": 0.0,
                "success_rate": 1.0,
            }

        metrics = self.performance_history[adapter_name]

        # Update counters
        metrics["total_executions"] += 1
        if success:
            metrics["successful_executions"] += 1

        # Update averages with exponential moving average
        alpha = 0.1  # Learning rate
        metrics["average_time"] = (1 - alpha) * metrics["average_time"] + alpha * execution_time
        if tokens_used > 0:
            metrics["average_tokens"] = (1 - alpha) * metrics["average_tokens"] + alpha * tokens_used

        # Update success rate
        metrics["success_rate"] = metrics["successful_executions"] / metrics["total_executions"]

        self._save_performance_history()

    def route_step(
        self, step: Dict[str, Any], policy: Optional[Dict[str, Any]] = None
    ) -> RoutingDecision:
        """Route a workflow step to the appropriate adapter with complexity analysis."""

        actor = step.get("actor", "unknown")
        step_name = step.get("name", "Unnamed step")

        # Perform complexity analysis
        complexity = self._analyze_step_complexity(step)

        # Check if actor is available in registry
        if not self.registry.is_available(actor):
            fallback_decision = self._route_with_complexity_fallback(complexity, step_name)
            return fallback_decision

        # Get adapter metadata
        adapter_info = self.adapters.get(actor, {})

        # Apply routing policy with complexity awareness
        prefer_deterministic = True
        complexity_threshold = 0.7  # Above this, prefer AI

        if policy:
            prefer_deterministic = policy.get("prefer_deterministic", True)
            complexity_threshold = policy.get("complexity_threshold", 0.7)
        # Early preference: if actor is AI and deterministic is preferred and feasible, switch
        if adapter_info.get("type") == "ai" and prefer_deterministic:
            try:
                alt_adapter = self._find_deterministic_alternative(actor)
                if alt_adapter and self.registry.is_available(alt_adapter):
                    det_confidence = self._calculate_deterministic_confidence(complexity, alt_adapter)
                    if det_confidence > 0.6 and complexity.score <= complexity_threshold:
                        return RoutingDecision(
                            adapter_name=alt_adapter,
                            adapter_type="deterministic",
                            reasoning=f"Prefer deterministic: routed {actor} -> {alt_adapter} (score: {complexity.score:.2f})",
                            estimated_tokens=0,
                            complexity_score=complexity.score,
                            confidence=det_confidence,
                            performance_hint="prefer_deterministic"
                        )
            except Exception:
                # Non-fatal; continue with normal routing
                pass

        # Enhanced routing logic with complexity scoring
        if adapter_info["type"] == "deterministic":
            # Check if deterministic tool can handle complexity
            confidence = self._calculate_deterministic_confidence(complexity, actor)

            if complexity.score > complexity_threshold and confidence < 0.5:
                # Complex task, low confidence - suggest AI alternative
                ai_alternative = self._find_ai_alternative(actor)
                if ai_alternative and self.registry.is_available(ai_alternative):
                    ai_tokens = self._estimate_ai_tokens(complexity, ai_alternative)
                    return RoutingDecision(
                        adapter_name=ai_alternative,
                        adapter_type="ai",
                        reasoning=f"Complex task (score: {complexity.score:.2f}) - upgraded from {actor} to {ai_alternative}",
                        estimated_tokens=ai_tokens,
                        complexity_score=complexity.score,
                        confidence=confidence,
                        performance_hint="complex_upgrade"
                    )

            return RoutingDecision(
                adapter_name=actor,
                adapter_type="deterministic",
                reasoning=f"Deterministic tool: {adapter_info['description']} (complexity: {complexity.score:.2f})",
                estimated_tokens=0,
                complexity_score=complexity.score,
                confidence=confidence,
                performance_hint=self._get_performance_hint(actor, complexity)
            )

        elif adapter_info["type"] == "ai":
            if prefer_deterministic and complexity.score < (1.0 - complexity_threshold):
                # Simple task - check for deterministic alternative
                alt_adapter = self._find_deterministic_alternative(actor)
                if alt_adapter and self.registry.is_available(alt_adapter):
                    det_confidence = self._calculate_deterministic_confidence(complexity, alt_adapter)
                    if det_confidence > 0.7:
                        return RoutingDecision(
                            adapter_name=alt_adapter,
                            adapter_type="deterministic",
                            reasoning=f"Simple task (score: {complexity.score:.2f}) - downgraded from {actor} to {alt_adapter}",
                            estimated_tokens=0,
                            complexity_score=complexity.score,
                            confidence=det_confidence,
                            performance_hint="simple_downgrade"
                        )

            ai_tokens = self._estimate_ai_tokens(complexity, actor)
            ai_confidence = self._calculate_ai_confidence(complexity, actor)

            return RoutingDecision(
                adapter_name=actor,
                adapter_type="ai",
                reasoning=f"AI tool: {adapter_info['description']} (complexity: {complexity.score:.2f})",
                estimated_tokens=ai_tokens,
                complexity_score=complexity.score,
                confidence=ai_confidence,
                performance_hint=self._get_performance_hint(actor, complexity)
            )

        # Fallback
        return RoutingDecision(
            adapter_name="fallback",
            adapter_type="ai",
            reasoning="Fallback routing due to configuration error",
            estimated_tokens=500,
            complexity_score=complexity.score,
            confidence=0.5
        )

    def _find_deterministic_alternative(self, ai_actor: str) -> Optional[str]:
        """Suggest a deterministic alternative for a given AI actor, if any.

        This provides a conservative mapping to help uphold a determinism-first
        policy. If no sensible alternative exists, returns None.
        """
        mapping = {
            # Prefer quick, cheap diagnostics/fixes when possible
            "ai_editor": "code_fixers",
            "ai_analyst": "vscode_diagnostics",
        }
        return mapping.get(ai_actor)

    def _find_ai_alternative(self, deterministic_actor: str) -> Optional[str]:
        """Find an AI alternative for a deterministic actor when complexity is high."""
        mapping = {
            "code_fixers": "ai_editor",
            "vscode_diagnostics": "ai_analyst",
            "pytest_runner": "ai_editor",  # For complex test generation
        }
        return mapping.get(deterministic_actor)

    def _analyze_step_complexity(self, step: Dict[str, Any]) -> ComplexityAnalysis:
        """Analyze the complexity of a workflow step."""
        factors = {}
        score = 0.0

        # File-based complexity factors
        files = step.get("files", [])
        file_scope = step.get("file_scope", [])
        all_files = []

        if isinstance(files, list):
            all_files.extend(files)
        elif isinstance(files, str):
            all_files.append(files)

        if isinstance(file_scope, list):
            all_files.extend(file_scope)
        elif isinstance(file_scope, str):
            all_files.append(file_scope)

        # Count actual files if patterns are provided
        file_count = 0
        estimated_size = 0
        for pattern in all_files:
            try:
                if "*" in pattern or "?" in pattern:
                    matched_files = glob.glob(pattern, recursive=True)
                    file_count += len(matched_files)
                    # Estimate size for performance (sample a few files)
                    sample_files = matched_files[:5]
                    for file_path in sample_files:
                        try:
                            size = Path(file_path).stat().st_size
                            estimated_size += size * (len(matched_files) / len(sample_files))
                        except:
                            estimated_size += 1000  # Default estimate
                else:
                    # Single file
                    file_count += 1
                    try:
                        estimated_size += Path(pattern).stat().st_size
                    except:
                        estimated_size += 1000
            except:
                # Pattern matching failed, estimate conservatively
                file_count += 5
                estimated_size += 5000

        # File count complexity (0.0 to 0.4)
        if file_count == 0:
            factors["file_count"] = 0.1  # No files = simple
        elif file_count <= 3:
            factors["file_count"] = 0.2
        elif file_count <= 10:
            factors["file_count"] = 0.3
        else:
            factors["file_count"] = 0.4

        # File size complexity (0.0 to 0.3)
        if estimated_size < 10000:  # < 10KB
            factors["file_size"] = 0.1
        elif estimated_size < 100000:  # < 100KB
            factors["file_size"] = 0.2
        else:
            factors["file_size"] = 0.3

        # Operation type complexity (0.0 to 0.3)
        operation_type = self._infer_operation_type(step)
        operation_complexity = {
            "read": 0.1,
            "format": 0.1,
            "lint": 0.15,
            "test": 0.2,
            "edit": 0.25,
            "refactor": 0.3,
            "generate": 0.3,
            "analyze": 0.25,
            "unknown": 0.2
        }
        factors["operation_type"] = operation_complexity.get(operation_type, 0.2)

        # Step configuration complexity (0.0 to 0.2)
        with_params = step.get("with", {})
        if isinstance(with_params, dict):
            param_count = len(with_params)
            nested_complexity = any(isinstance(v, (dict, list)) for v in with_params.values())

            if param_count == 0:
                factors["configuration"] = 0.05
            elif param_count <= 3 and not nested_complexity:
                factors["configuration"] = 0.1
            elif param_count <= 6 or nested_complexity:
                factors["configuration"] = 0.15
            else:
                factors["configuration"] = 0.2
        else:
            factors["configuration"] = 0.1

        # Context dependencies complexity (0.0 to 0.2)
        context_deps = step.get("context", {})
        retry_config = step.get("retry", {})
        when_condition = step.get("when")

        context_score = 0.0
        if context_deps:
            context_score += 0.1
        if retry_config:
            context_score += 0.05
        if when_condition:
            context_score += 0.05

        factors["context_deps"] = min(context_score, 0.2)

        # Calculate overall score
        score = sum(factors.values())
        score = min(score, 1.0)  # Cap at 1.0

        # Calculate deterministic confidence
        deterministic_confidence = max(0.0, 1.0 - score)
        if operation_type in ["read", "format", "lint"]:
            deterministic_confidence += 0.2
        if file_count <= 5 and estimated_size < 50000:
            deterministic_confidence += 0.1
        deterministic_confidence = min(deterministic_confidence, 1.0)

        return ComplexityAnalysis(
            score=score,
            factors=factors,
            file_count=file_count,
            estimated_file_size=estimated_size,
            operation_type=operation_type,
            deterministic_confidence=deterministic_confidence
        )

    def _infer_operation_type(self, step: Dict[str, Any]) -> str:
        """Infer the type of operation from step configuration."""
        actor = step.get("actor", "")
        name = step.get("name", "").lower()
        with_params = step.get("with", {})

        # Check actor name patterns
        if "diagnostic" in actor or "lint" in actor:
            return "lint"
        elif "test" in actor or "pytest" in actor:
            return "test"
        elif "fix" in actor or "format" in actor:
            return "format"
        elif "edit" in actor or "ai_" in actor:
            return "edit"
        elif "git" in actor:
            return "read"

        # Check step name patterns
        if any(word in name for word in ["read", "get", "fetch", "load"]):
            return "read"
        elif any(word in name for word in ["format", "fix", "clean"]):
            return "format"
        elif any(word in name for word in ["lint", "check", "validate"]):
            return "lint"
        elif any(word in name for word in ["test", "verify"]):
            return "test"
        elif any(word in name for word in ["edit", "modify", "change", "update"]):
            return "edit"
        elif any(word in name for word in ["refactor", "restructure"]):
            return "refactor"
        elif any(word in name for word in ["generate", "create", "build"]):
            return "generate"
        elif any(word in name for word in ["analyze", "review", "assess"]):
            return "analyze"

        return "unknown"

    def _route_with_complexity_fallback(self, complexity: ComplexityAnalysis, step_name: str) -> RoutingDecision:
        """Route to fallback adapter based on complexity analysis."""
        if complexity.score < 0.4:
            # Simple task - try deterministic fallback first
            for adapter_name in ["code_fixers", "vscode_diagnostics", "pytest_runner"]:
                if self.registry.is_available(adapter_name):
                    return RoutingDecision(
                        adapter_name=adapter_name,
                        adapter_type="deterministic",
                        reasoning=f"Fallback to {adapter_name} for simple task (complexity: {complexity.score:.2f})",
                        estimated_tokens=0,
                        complexity_score=complexity.score,
                        confidence=0.6,
                        performance_hint="fallback_simple"
                    )

        # Complex task or no deterministic available - use AI fallback
        ai_tokens = int(500 + complexity.score * 1500)  # Scale with complexity
        return RoutingDecision(
            adapter_name="ai_editor",
            adapter_type="ai",
            reasoning=f"AI fallback for complex task (complexity: {complexity.score:.2f})",
            estimated_tokens=ai_tokens,
            complexity_score=complexity.score,
            confidence=0.7,
            performance_hint="fallback_complex"
        )

    def _calculate_deterministic_confidence(self, complexity: ComplexityAnalysis, adapter_name: str) -> float:
        """Calculate confidence that a deterministic adapter can handle the complexity."""
        base_confidence = complexity.deterministic_confidence

        # Adjust based on adapter capabilities
        adapter_boosts = {
            "code_fixers": {"format": 0.2, "lint": 0.1},
            "vscode_diagnostics": {"lint": 0.2, "analyze": 0.1},
            "pytest_runner": {"test": 0.2},
            "git_ops": {"read": 0.2}
        }

        if adapter_name in adapter_boosts:
            operation_boosts = adapter_boosts[adapter_name]
            boost = operation_boosts.get(complexity.operation_type, 0.0)
            base_confidence += boost

        # Consider performance history
        if adapter_name in self.performance_history:
            history = self.performance_history[adapter_name]
            success_rate = history.get("success_rate", 1.0)
            base_confidence *= success_rate

        return min(base_confidence, 1.0)

    def _calculate_ai_confidence(self, complexity: ComplexityAnalysis, adapter_name: str) -> float:
        """Calculate confidence that an AI adapter can handle the complexity."""
        # AI adapters generally more confident with complex tasks
        base_confidence = 0.6 + (complexity.score * 0.3)

        # Consider performance history
        if adapter_name in self.performance_history:
            history = self.performance_history[adapter_name]
            success_rate = history.get("success_rate", 1.0)
            base_confidence *= success_rate

        return min(base_confidence, 1.0)

    def _estimate_ai_tokens(self, complexity: ComplexityAnalysis, adapter_name: str) -> int:
        """Estimate token usage for AI adapter based on complexity."""
        base_tokens = 1000

        # Scale with complexity factors
        complexity_multiplier = 1.0 + complexity.score
        file_multiplier = 1.0 + (complexity.file_count * 0.1)
        size_multiplier = 1.0 + (complexity.estimated_file_size / 100000)  # Per 100KB

        total_tokens = base_tokens * complexity_multiplier * file_multiplier * size_multiplier

        # Consider historical usage
        if adapter_name in self.performance_history:
            history = self.performance_history[adapter_name]
            avg_tokens = history.get("average_tokens", base_tokens)
            if avg_tokens > 0:
                # Blend historical average with complexity estimate
                total_tokens = (total_tokens + avg_tokens) / 2

        return int(total_tokens)

    def _get_performance_hint(self, adapter_name: str, complexity: ComplexityAnalysis) -> Optional[str]:
        """Get performance hint for the routing decision."""
        if complexity.score > 0.8:
            return "high_complexity"
        elif complexity.score < 0.2:
            return "low_complexity"
        elif complexity.file_count > 20:
            return "many_files"
        elif complexity.estimated_file_size > 500000:
            return "large_files"
        elif complexity.operation_type in ["refactor", "generate"]:
            return "complex_operation"
        else:
            return None

    def route_with_budget_awareness(
        self,
        step: Dict[str, Any],
        role: str,
        budget_remaining: Optional[int] = None,
    ) -> RoutingDecision:
        """Route a step considering a budget and role preferences.

        - role: 'ipt' or 'wt' (case-insensitive)
        - budget_remaining: if None, falls back to route_step
        """
        try:
            if budget_remaining is None:
                return self.route_step(step)

            role_lc = (role or "").lower()
            if role_lc == "ipt":
                preferred: List[str] = ["ai_analyst", "ai_editor"]
            else:  # default to WT
                preferred = ["code_fixers", "pytest_runner", "vscode_diagnostics"]

            # Try preferred in order within budget
            for name in preferred:
                if not self.registry.is_available(name):
                    continue
                est = self.registry.estimate_cost(name, step)
                if est <= (budget_remaining or 0):
                    adapter = self.registry.get_adapter(name)
                    a_type = getattr(adapter, "adapter_type", None)
                    a_type_str = (
                        getattr(a_type, "value", "deterministic")
                        if a_type
                        else "deterministic"
                    )
                    return RoutingDecision(
                        adapter_name=name,
                        adapter_type=a_type_str,
                        reasoning=f"Selected {name} for role={role_lc} within budget",
                        estimated_tokens=est,
                    )

            # If none fit budget, choose cheapest available deterministic as fallback
            cheapest_name = None
            cheapest_cost = None
            for name, meta in self.adapters.items():
                if meta.get("type") == "deterministic" and self.registry.is_available(
                    name
                ):
                    est = self.registry.estimate_cost(name, step)
                    if cheapest_cost is None or est < cheapest_cost:
                        cheapest_name = name
                        cheapest_cost = est

            if cheapest_name:
                return RoutingDecision(
                    adapter_name=cheapest_name,
                    adapter_type="deterministic",
                    reasoning=f"Budget exceeded; using cheapest deterministic: {cheapest_name}",
                    estimated_tokens=cheapest_cost or 0,
                )

            # Final fallback: original policy routing
            return self.route_step(step)
        except Exception as e:
            return RoutingDecision(
                adapter_name="fallback",
                adapter_type="ai",
                reasoning=f"Budget-aware routing failed: {e}",
                estimated_tokens=0,
            )

    def route_parallel_steps(
        self, steps: List[Dict[str, Any]], policy: Optional[Dict[str, Any]] = None
    ) -> ParallelRoutingPlan:
        """Route multiple steps to appropriate adapters with conflict detection."""

        routing_decisions = []
        file_claims = []

        # Route each step and collect file claims
        for i, step in enumerate(steps):
            decision = self.route_step(step, policy)
            routing_decisions.append((step, decision))

            # Extract file scope for conflict detection
            files = step.get("files", [])
            file_scope = step.get("file_scope", [])

            if files or file_scope:
                # Convert files to patterns for scope checking
                patterns = []
                if files:
                    patterns.extend(files if isinstance(files, list) else [files])
                if file_scope:
                    patterns.extend(
                        file_scope if isinstance(file_scope, list) else [file_scope]
                    )

                if patterns:
                    claim = FileClaim(
                        workflow_id=f"step_{i}_{step.get('id', 'unknown')}",
                        file_patterns=patterns,
                        mode=ScopeMode(step.get("scope_mode", "exclusive")),
                    )
                    file_claims.append(claim)

        # Detect conflicts
        conflicts = self.scope_manager.detect_conflicts(file_claims)

        # Create execution groups based on conflicts
        execution_groups = self._create_execution_groups(steps, conflicts)

        # Calculate resource allocation
        resource_allocation = self._calculate_resource_allocation(routing_decisions)

        # Calculate total cost
        total_cost = sum(decision.estimated_tokens for _, decision in routing_decisions)

        return ParallelRoutingPlan(
            routing_decisions=routing_decisions,
            execution_groups=execution_groups,
            total_estimated_cost=total_cost,
            conflicts=conflicts,
            resource_allocation=resource_allocation,
        )

    def create_allocation_plan(
        self,
        workflows: List[Dict[str, Any]],
        budget: Optional[float] = None,
        max_parallel: int = 3,
    ) -> AllocationPlan:
        """Create resource allocation plan for coordinated workflows."""

        adapter_assignments = {}
        cost_estimates = {}
        total_cost = 0

        for workflow in workflows:
            workflow_name = workflow.get("name", "unnamed_workflow")

            # Process phases or steps
            phases = workflow.get("phases", [])
            steps = workflow.get("steps", [])

            # Handle phases (IPT-WT pattern)
            if phases:
                for phase in phases:
                    phase_id = phase.get("id", "unknown_phase")
                    tasks = phase.get("tasks", [])

                    for task in tasks:
                        task_id = (
                            f"{workflow_name}_{phase_id}_{task}"
                            if isinstance(task, str)
                            else f"{workflow_name}_{phase_id}_{task.get('id', 'unknown')}"
                        )

                        # Convert task to step format for routing
                        if isinstance(task, str):
                            step = {"id": task, "actor": "unknown", "name": task}
                        else:
                            step = task

                        # Route to appropriate adapter
                        adapter_decision = self.route_step(step)
                        cost = adapter_decision.estimated_tokens

                        adapter_assignments[task_id] = {
                            "adapter": adapter_decision.adapter_name,
                            "adapter_type": adapter_decision.adapter_type,
                            "estimated_cost": cost,
                            "priority": phase.get("priority", 1),
                            "workflow": workflow_name,
                            "phase": phase_id,
                        }
                        total_cost += cost

            # Handle direct steps (traditional workflow)
            elif steps:
                for step in steps:
                    step_id = f"{workflow_name}_{step.get('id', 'unknown_step')}"

                    adapter_decision = self.route_step(step)
                    cost = adapter_decision.estimated_tokens

                    adapter_assignments[step_id] = {
                        "adapter": adapter_decision.adapter_name,
                        "adapter_type": adapter_decision.adapter_type,
                        "estimated_cost": cost,
                        "priority": step.get("priority", 1),
                        "workflow": workflow_name,
                    }
                    total_cost += cost

        # Calculate parallel groups
        parallel_groups = self._create_workflow_parallel_groups(workflows)

        # Check budget constraints
        estimated_usd_cost = (
            total_cost * 0.0005
        )  # Rough estimate: $0.50 per 1000 tokens
        within_budget = budget is None or estimated_usd_cost <= budget

        return AllocationPlan(
            assignments=adapter_assignments,
            total_estimated_cost=total_cost,
            estimated_usd_cost=estimated_usd_cost,
            within_budget=within_budget,
            parallel_groups=parallel_groups,
        )

    def estimate_parallel_cost(self, steps: List[Dict[str, Any]]) -> int:
        """Estimate cost for parallel step execution."""

        total_cost = 0
        for step in steps:
            decision = self.route_step(step)
            total_cost += decision.estimated_tokens

        return total_cost

    def get_adapter_availability(self) -> Dict[str, bool]:
        """Get availability status of all adapters."""

        availability = {}
        for adapter_name in self.adapters.keys():
            availability[adapter_name] = self.registry.is_available(adapter_name)

        return availability

    def _create_execution_groups(
        self, steps: List[Dict[str, Any]], conflicts: List[ScopeConflict]
    ) -> List[List[int]]:
        """Create groups of step indices that can run in parallel."""

        groups = []

        if not conflicts:
            # No conflicts, all steps can potentially run in parallel
            # Group by adapter type to avoid resource contention
            deterministic_steps = []
            ai_steps = []

            for i, step in enumerate(steps):
                decision = self.route_step(step)
                if decision.adapter_type == "deterministic":
                    deterministic_steps.append(i)
                else:
                    ai_steps.append(i)

            if deterministic_steps:
                groups.append(deterministic_steps)
            if ai_steps:
                # Limit AI steps to avoid overwhelming AI services
                while ai_steps:
                    batch = ai_steps[:3]  # Max 3 AI steps in parallel
                    groups.append(batch)
                    ai_steps = ai_steps[3:]
        else:
            # Create groups avoiding conflicts
            conflicting_step_ids = set()
            for conflict in conflicts:
                for workflow_id in conflict.workflow_ids:
                    # Extract step index from workflow_id (format: step_{i}_{step_id})
                    if workflow_id.startswith("step_"):
                        try:
                            step_index = int(workflow_id.split("_")[1])
                            conflicting_step_ids.add(step_index)
                        except (IndexError, ValueError):
                            pass

            # Group non-conflicting steps together
            non_conflicting = []
            for i in range(len(steps)):
                if i not in conflicting_step_ids:
                    non_conflicting.append(i)

            if non_conflicting:
                groups.append(non_conflicting)

            # Add conflicting steps as individual groups
            for step_id in conflicting_step_ids:
                groups.append([step_id])

        return groups

    def _calculate_resource_allocation(
        self, routing_decisions: List[Tuple[Dict[str, Any], RoutingDecision]]
    ) -> Dict[str, List[int]]:
        """Calculate which steps will use which adapters."""

        allocation = {}

        for i, (step, decision) in enumerate(routing_decisions):
            adapter_name = decision.adapter_name
            if adapter_name not in allocation:
                allocation[adapter_name] = []
            allocation[adapter_name].append(i)

        return allocation

    def _create_workflow_parallel_groups(
        self, workflows: List[Dict[str, Any]]
    ) -> List[List[str]]:
        """Create parallel groups for multiple workflows."""

        # Simple implementation: group workflows by priority
        priority_groups = {}

        for workflow in workflows:
            workflow_name = workflow.get("name", "unnamed_workflow")
            priority = (
                workflow.get("metadata", {}).get("coordination", {}).get("priority", 1)
            )

            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(workflow_name)

        # Convert to list of groups, ordered by priority (highest first)
        groups = []
        for priority in sorted(priority_groups.keys(), reverse=True):
            groups.append(priority_groups[priority])

        return groups
