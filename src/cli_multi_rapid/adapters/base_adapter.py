#!/usr/bin/env python3
"""
Base Adapter Interface

Defines the abstract interface that all CLI Orchestrator adapters must implement.
Supports both deterministic tools and AI services with consistent execution patterns.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AdapterType(Enum):
    """Types of adapters supported by the orchestrator."""

    DETERMINISTIC = "deterministic"
    AI = "ai"


@dataclass
class AdapterPerformanceProfile:
    """Performance profile for adapter metadata."""

    complexity_threshold: float = 0.5  # Max complexity this adapter handles well
    preferred_file_types: List[str] = field(default_factory=list)
    max_files: int = 100  # Maximum files to process efficiently
    max_file_size: int = 1000000  # Maximum total file size (bytes)
    operation_types: List[str] = field(default_factory=list)
    avg_execution_time: float = 1.0  # seconds
    success_rate: float = 1.0
    cost_efficiency: float = 1.0  # tokens per operation
    parallel_capable: bool = True
    requires_network: bool = False
    requires_api_key: bool = False


@dataclass
class AdapterResult:
    """Standard result format for all adapter executions."""

    success: bool
    tokens_used: int = 0
    artifacts: List[str] = field(default_factory=list)
    output: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format expected by workflow runner."""
        return {
            "success": self.success,
            "tokens_used": self.tokens_used,
            "artifacts": self.artifacts,
            "output": self.output or "",
            "error": self.error,
            "metadata": self.metadata,
        }


class BaseAdapter(ABC):
    """Abstract base class for all workflow step adapters."""

    def __init__(self, name: str, adapter_type: AdapterType, description: str):
        self.name = name
        self.adapter_type = adapter_type
        self.description = description
        self.logger = logging.getLogger(f"adapter.{name}")

    @abstractmethod
    def execute(
        self,
        step: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        files: Optional[str] = None,
    ) -> AdapterResult:
        """
        Execute a workflow step.

        Args:
            step: The workflow step definition containing actor, with, emits, etc.
            context: Additional context from workflow execution
            files: File pattern for operations (e.g., "src/**/*.py")

        Returns:
            AdapterResult with execution details
        """
        pass

    @abstractmethod
    def validate_step(self, step: Dict[str, Any]) -> bool:
        """
        Validate that this adapter can execute the given step.

        Args:
            step: The workflow step definition

        Returns:
            True if step is valid for this adapter
        """
        pass

    @abstractmethod
    def estimate_cost(self, step: Dict[str, Any]) -> int:
        """
        Estimate the token cost of executing this step.

        Args:
            step: The workflow step definition

        Returns:
            Estimated token usage (0 for deterministic tools)
        """
        pass

    def can_handle_complexity(self, complexity_score: float) -> bool:
        """Check if this adapter can handle the given complexity level."""
        profile = self.get_performance_profile()
        return complexity_score <= profile.complexity_threshold

    def supports_operation_type(self, operation_type: str) -> bool:
        """Check if this adapter supports the given operation type."""
        profile = self.get_performance_profile()
        return operation_type in profile.operation_types or "*" in profile.operation_types

    def supports_file_type(self, file_extension: str) -> bool:
        """Check if this adapter optimally supports the given file type."""
        profile = self.get_performance_profile()
        return (
            "*" in profile.preferred_file_types or
            file_extension in profile.preferred_file_types or
            f".{file_extension}" in profile.preferred_file_types
        )

    def estimate_performance(self, file_count: int, total_file_size: int) -> float:
        """Estimate performance score for given file parameters (0.0 to 1.0)."""
        profile = self.get_performance_profile()

        # File count penalty
        file_penalty = 0.0
        if file_count > profile.max_files:
            file_penalty = min(0.5, (file_count - profile.max_files) / profile.max_files)

        # File size penalty
        size_penalty = 0.0
        if total_file_size > profile.max_file_size:
            size_penalty = min(0.5, (total_file_size - profile.max_file_size) / profile.max_file_size)

        # Base performance from success rate
        base_performance = profile.success_rate

        # Apply penalties
        final_performance = base_performance - file_penalty - size_penalty
        return max(0.0, min(1.0, final_performance))

    def get_metadata(self) -> Dict[str, Any]:
        """Get adapter metadata for router registration."""
        profile = self.get_performance_profile()
        return {
            "type": self.adapter_type.value,
            "description": self.description,
            "cost": self.estimate_cost({}),  # Base cost estimate
            "available": self.is_available(),
            "performance_profile": {
                "complexity_threshold": profile.complexity_threshold,
                "preferred_file_types": profile.preferred_file_types,
                "max_files": profile.max_files,
                "max_file_size": profile.max_file_size,
                "operation_types": profile.operation_types,
                "avg_execution_time": profile.avg_execution_time,
                "success_rate": profile.success_rate,
                "cost_efficiency": profile.cost_efficiency,
                "parallel_capable": profile.parallel_capable,
                "requires_network": profile.requires_network,
                "requires_api_key": profile.requires_api_key,
            }
        }

    def get_performance_profile(self) -> AdapterPerformanceProfile:
        """Get detailed performance profile for this adapter."""
        # Default implementation - should be overridden by specific adapters
        return AdapterPerformanceProfile(
            complexity_threshold=0.5,
            preferred_file_types=["*"],
            operation_types=["unknown"],
            parallel_capable=True
        )

    def is_available(self) -> bool:
        """Check if this adapter is available and can be used."""
        return True

    def supports_files(self) -> bool:
        """Whether this adapter supports file pattern operations."""
        return True

    def supports_with_params(self) -> bool:
        """Whether this adapter supports 'with' parameters."""
        return True

    def _extract_with_params(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Extract 'with' parameters from step definition."""
        return step.get("with", {})

    def _extract_emit_paths(self, step: Dict[str, Any]) -> List[str]:
        """Extract 'emits' artifact paths from step definition."""
        emits = step.get("emits", [])
        if isinstance(emits, str):
            return [emits]
        return emits if isinstance(emits, list) else []

    def _log_execution_start(self, step: Dict[str, Any]) -> None:
        """Log the start of step execution."""
        step_name = step.get("name", "Unnamed step")
        self.logger.info(f"Starting execution: {step_name}")

    def _log_execution_complete(self, result: AdapterResult) -> None:
        """Log the completion of step execution."""
        status = "SUCCESS" if result.success else "FAILED"
        self.logger.info(
            f"Execution {status}: tokens={result.tokens_used}, artifacts={len(result.artifacts)}"
        )
        if result.error:
            self.logger.error(f"Error: {result.error}")

    def update_performance_metrics(self, execution_time: float, success: bool, tokens_used: int = 0) -> None:
        """Update performance metrics after execution (to be implemented by router)."""
        # This is a hook for the router to update performance tracking
        pass
