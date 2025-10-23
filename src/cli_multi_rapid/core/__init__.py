#!/usr/bin/env python3
"""
Core Workflow Execution Modules

This package contains the core workflow execution components:
- executor: Step execution through adapters
- coordinator: Multi-step workflow orchestration
- gate_manager: Verification gates and quality checks
- artifact_manager: Artifact tracking and management

These modules replace the monolithic workflow_runner.py with focused,
single-responsibility components for better testability and extensibility.
"""

from .artifact_manager import ArtifactManager, Artifact
from .coordinator import WorkflowCoordinator, WorkflowResult
from .executor import StepExecutor, StepExecutionResult
from .gate_manager import GateManager, GateResult, GateType

__all__ = [
    # Executor
    "StepExecutor",
    "StepExecutionResult",
    # Coordinator
    "WorkflowCoordinator",
    "WorkflowResult",
    # Gate Manager
    "GateManager",
    "GateResult",
    "GateType",
    # Artifact Manager
    "ArtifactManager",
    "Artifact",
]
