#!/usr/bin/env python3
"""
Adapter Registry

Central registry for managing and discovering available adapters.
Integrates with the Router system to provide dynamic adapter availability.
"""

import logging
from typing import Dict, List, Optional, Type

from .base_adapter import AdapterType, BaseAdapter

logger = logging.getLogger(__name__)


class AdapterRegistry:
    """Central registry for all available adapters."""

    def __init__(self):
        self._adapters: Dict[str, BaseAdapter] = {}
        self._adapter_classes: Dict[str, Type[BaseAdapter]] = {}
        self._auto_register_core_adapters()

    def register(self, adapter: BaseAdapter) -> None:
        """Register an adapter instance."""
        self._adapters[adapter.name] = adapter
        logger.info(
            f"Registered adapter: {adapter.name} ({adapter.adapter_type.value})"
        )

    def register_class(self, name: str, adapter_class: Type[BaseAdapter]) -> None:
        """Register an adapter class for lazy instantiation."""
        self._adapter_classes[name] = adapter_class
        logger.debug(f"Registered adapter class: {name}")

    def get_adapter(self, name: str) -> Optional[BaseAdapter]:
        """Get an adapter by name, instantiating if necessary."""
        # Check if already instantiated
        if name in self._adapters:
            return self._adapters[name]

        # Try to instantiate from registered class
        if name in self._adapter_classes:
            try:
                adapter_class = self._adapter_classes[name]
                # Note: This assumes adapters have a default constructor
                # More complex adapters may need factory methods
                adapter = adapter_class()
                self._adapters[name] = adapter
                logger.info(f"Instantiated adapter: {name}")
                return adapter
            except Exception as e:
                logger.error(f"Failed to instantiate adapter {name}: {e}")
                return None

        logger.warning(f"Adapter not found: {name}")
        return None

    def get_available_adapters(self) -> Dict[str, Dict[str, any]]:
        """Get metadata for all available adapters."""
        available = {}

        # Check instantiated adapters
        for name, adapter in self._adapters.items():
            if adapter.is_available():
                available[name] = adapter.get_metadata()

        # Check registered classes (assume available unless proven otherwise)
        for name in self._adapter_classes:
            if name not in available:
                # For registry compatibility, provide basic metadata
                available[name] = {
                    "name": name,
                    "type": "deterministic",  # Default assumption
                    "adapter_type": "deterministic",
                    "description": f"Adapter: {name}",
                    "cost": 0,
                    "available": True,
                }

        return available

    def get_adapters_by_type(self, adapter_type: AdapterType) -> List[str]:
        """Get all adapter names of a specific type."""
        result = []
        for name, adapter in self._adapters.items():
            if adapter.adapter_type == adapter_type and adapter.is_available():
                result.append(name)
        return result

    def is_available(self, name: str) -> bool:
        """Check if an adapter is available."""
        adapter = self.get_adapter(name)
        return adapter is not None and adapter.is_available()

    def validate_step(self, name: str, step: Dict[str, any]) -> bool:
        """Validate that an adapter can execute a given step."""
        adapter = self.get_adapter(name)
        if not adapter:
            return False
        return adapter.validate_step(step)

    def estimate_cost(self, name: str, step: Dict[str, any]) -> int:
        """Estimate the cost of executing a step with the given adapter."""
        adapter = self.get_adapter(name)
        if not adapter:
            return 0
        return adapter.estimate_cost(step)

    def list_adapters(self) -> List[str]:
        """List all registered adapter names."""
        all_names = set(self._adapters.keys()) | set(self._adapter_classes.keys())
        return sorted(all_names)

    # Backwards-compatibility alias expected by some tests
    def list_available_adapters(self) -> Dict[str, Dict[str, any]]:
        """Alias for get_available_adapters for compatibility with older tests."""
        return self.get_available_adapters()

    def _auto_register_core_adapters(self) -> None:
        """Register core adapters by class for discovery without eager instantiation."""
        try:
            from .ai_editor import AIEditorAdapter
            from .ai_analyst import AIAnalystAdapter
            from .code_fixers import CodeFixersAdapter
            from .git_ops import GitOpsAdapter
            from .pytest_runner import PytestRunnerAdapter
            from .vscode_diagnostics import VSCodeDiagnosticsAdapter

            self.register_class("ai_editor", AIEditorAdapter)
            self.register_class("ai_analyst", AIAnalystAdapter)
            self.register_class("code_fixers", CodeFixersAdapter)
            self.register_class("git_ops", GitOpsAdapter)
            self.register_class("pytest_runner", PytestRunnerAdapter)
            self.register_class("vscode_diagnostics", VSCodeDiagnosticsAdapter)
        except Exception as e:
            logger.debug(f"Core adapter auto-registration skipped: {e}")


# Global registry instance
registry = AdapterRegistry()
