#!/usr/bin/env python3
"""
CLI Orchestrator Adapter Framework

Base classes and interfaces for implementing tool and AI adapters that execute
workflow steps in a deterministic and auditable manner.

Refactored to use lazy loading via AdapterFactory. Direct adapter imports are
deprecated - use factory.create() or registry.get_adapter() instead.
"""

import warnings

# Core interfaces - always available
from .adapter_registry import AdapterRegistry
from .base_adapter import AdapterResult, AdapterType, BaseAdapter
from .factory import AdapterFactory, factory


# Legacy exports for backward compatibility (deprecated)
# These trigger eager loading and should be avoided in new code
def __getattr__(name: str):
    """
    Lazy import handler for backward compatibility.

    Deprecated: Direct adapter imports trigger eager loading. Use factory.create()
    or registry.get_adapter() instead.
    """

    # Map of legacy imports to module paths
    _legacy_imports = {
        "AIAnalystAdapter": "ai_analyst",
        "AIEditorAdapter": "ai_editor",
        "CodeFixersAdapter": "code_fixers",
        "CostEstimatorAdapter": "cost_estimator",
        "DeepSeekAdapter": "deepseek_adapter",
        "GitOpsAdapter": "git_ops",
        "PytestRunnerAdapter": "pytest_runner",
        "VSCodeDiagnosticsAdapter": "vscode_diagnostics",
    }

    if name in _legacy_imports:
        warnings.warn(
            f"Direct import of {name} is deprecated. "
            f"Use factory.create('{_legacy_imports[name]}') or "
            f"registry.get_adapter('{_legacy_imports[name]}') instead.",
            DeprecationWarning,
            stacklevel=2
        )

        # Lazy import the module
        module_name = _legacy_imports[name]
        module = __import__(f"cli_multi_rapid.adapters.{module_name}", fromlist=[name])
        return getattr(module, name)

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Public API
__all__ = [
    # Core interfaces
    "BaseAdapter",
    "AdapterResult",
    "AdapterType",
    "AdapterRegistry",
    "AdapterFactory",
    "factory",

    # Deprecated legacy exports (use factory.create() instead)
    "AIAnalystAdapter",
    "AIEditorAdapter",
    "CodeFixersAdapter",
    "CostEstimatorAdapter",
    "DeepSeekAdapter",
    "GitOpsAdapter",
    "PytestRunnerAdapter",
    "VSCodeDiagnosticsAdapter",
]
