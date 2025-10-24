#!/usr/bin/env python3
"""
Adapter Factory

Provides centralized adapter instantiation with lazy loading, plugin discovery,
and dependency injection. Breaks circular dependencies by deferring imports
until adapters are actually needed.
"""

import importlib
import logging
from typing import Optional, Type

from .base_adapter import BaseAdapter

logger = logging.getLogger(__name__)


class AdapterFactory:
    """
    Factory for creating adapter instances with lazy loading and plugin discovery.

    Supports three modes of adapter registration:
    1. Direct instance registration (eager)
    2. Class registration with lazy instantiation
    3. Module path registration with deferred import and instantiation
    """

    def __init__(self):
        self._instances: dict[str, BaseAdapter] = {}
        self._classes: dict[str, Type[BaseAdapter]] = {}
        self._module_paths: dict[str, str] = {}
        self._failed_adapters: set[str] = set()

        # Register core adapters by module path (lazy loading)
        self._register_core_adapters()

        # Discover plugins from entry points
        self._discover_plugins()

    def _register_core_adapters(self) -> None:
        """Register core adapters by module path for lazy loading."""

        # Core adapters
        core_adapters = {
            # Deterministic tools
            "code_fixers": "cli_multi_rapid.adapters.code_fixers:CodeFixersAdapter",
            "pytest_runner": "cli_multi_rapid.adapters.pytest_runner:PytestRunnerAdapter",
            "vscode_diagnostics": "cli_multi_rapid.adapters.vscode_diagnostics:VSCodeDiagnosticsAdapter",
            "git_ops": "cli_multi_rapid.adapters.git_ops:GitOpsAdapter",
            "github_integration": "cli_multi_rapid.adapters.github_integration:GitHubIntegrationAdapter",
            "syntax_validator": "cli_multi_rapid.adapters.syntax_validator:SyntaxValidatorAdapter",
            "type_checker": "cli_multi_rapid.adapters.type_checker:TypeCheckerAdapter",
            "import_resolver": "cli_multi_rapid.adapters.import_resolver:ImportResolverAdapter",
            "security_scanner": "cli_multi_rapid.adapters.security_scanner:SecurityScannerAdapter",
            "verifier": "cli_multi_rapid.adapters.verifier_adapter:VerifierAdapter",
            "certificate_generator": "cli_multi_rapid.adapters.certificate_generator:CertificateGeneratorAdapter",
            "cost_estimator": "cli_multi_rapid.adapters.cost_estimator:CostEstimatorAdapter",

            # AI-powered tools
            "ai_editor": "cli_multi_rapid.adapters.ai_editor:AIEditorAdapter",
            "ai_analyst": "cli_multi_rapid.adapters.ai_analyst:AIAnalystAdapter",
            "deepseek": "cli_multi_rapid.adapters.deepseek_adapter:DeepSeekAdapter",

            # Codex pipeline
            "contract_validator": "cli_multi_rapid.adapters.contract_validator:ContractValidatorAdapter",
            "bundle_loader": "cli_multi_rapid.adapters.bundle_loader:BundleLoaderAdapter",
            "enhanced_bundle_applier": "cli_multi_rapid.adapters.enhanced_bundle_applier:EnhancedBundleApplierAdapter",
        }

        # Tool adapter bridges (dynamic registration)
        bridge_tools = ["vcs", "containers", "editor", "js_runtime", "ai_cli", "python_quality", "precommit"]
        for tool in bridge_tools:
            core_adapters[f"tool_{tool}"] = f"cli_multi_rapid.adapters.tool_adapter_bridge:ToolAdapterBridge#{tool}"

        self._module_paths.update(core_adapters)
        logger.debug(f"Registered {len(core_adapters)} core adapters for lazy loading")

    def _discover_plugins(self) -> None:
        """Discover adapter plugins from setuptools entry points."""
        try:
            # Try modern importlib.metadata first (Python 3.10+)
            try:
                from importlib.metadata import entry_points
            except ImportError:
                # Fallback to importlib_metadata for Python 3.9
                from importlib_metadata import entry_points

            # Discover plugins registered under 'cli_orchestrator.adapters' entry point
            discovered = entry_points(group='cli_orchestrator.adapters')

            for entry_point in discovered:
                plugin_name = entry_point.name
                module_path = f"{entry_point.value}"

                if plugin_name not in self._module_paths:
                    self._module_paths[plugin_name] = module_path
                    logger.info(f"Discovered plugin adapter: {plugin_name} from {module_path}")

        except Exception as e:
            logger.debug(f"Plugin discovery skipped: {e}")

    def register_instance(self, name: str, adapter: BaseAdapter) -> None:
        """Register a pre-instantiated adapter instance (eager loading)."""
        self._instances[name] = adapter
        logger.debug(f"Registered adapter instance: {name}")

    def register_class(self, name: str, adapter_class: Type[BaseAdapter]) -> None:
        """Register an adapter class for lazy instantiation."""
        self._classes[name] = adapter_class
        logger.debug(f"Registered adapter class: {name}")

    def register_module(self, name: str, module_path: str) -> None:
        """
        Register an adapter by module path for deferred import.

        Format: "module.path:ClassName" or "module.path:ClassName#arg" for parameterized adapters
        """
        self._module_paths[name] = module_path
        logger.debug(f"Registered adapter module: {name} -> {module_path}")

    def create(self, name: str) -> Optional[BaseAdapter]:
        """
        Create or retrieve an adapter instance.

        Follows this resolution order:
        1. Return cached instance if exists
        2. Instantiate from registered class
        3. Import and instantiate from module path
        4. Return None if not found or failed
        """

        # Check if already instantiated
        if name in self._instances:
            return self._instances[name]

        # Check if previously failed
        if name in self._failed_adapters:
            logger.warning(f"Adapter {name} previously failed to load, skipping")
            return None

        # Try to instantiate from registered class
        if name in self._classes:
            try:
                adapter_class = self._classes[name]
                adapter = adapter_class()
                self._instances[name] = adapter
                logger.info(f"Instantiated adapter from class: {name}")
                return adapter
            except Exception as e:
                logger.error(f"Failed to instantiate adapter {name} from class: {e}")
                self._failed_adapters.add(name)
                return None

        # Try to import and instantiate from module path
        if name in self._module_paths:
            try:
                module_path = self._module_paths[name]
                adapter = self._load_from_module_path(module_path)

                if adapter:
                    self._instances[name] = adapter
                    logger.info(f"Loaded adapter from module: {name}")
                    return adapter

            except Exception as e:
                logger.error(f"Failed to load adapter {name} from module path: {e}")
                self._failed_adapters.add(name)
                return None

        logger.warning(f"Adapter not found: {name}")
        return None

    def _load_from_module_path(self, module_path: str) -> Optional[BaseAdapter]:
        """
        Load an adapter from a module path string.

        Supports:
        - "module.path:ClassName" - Standard class import
        - "module.path:ClassName#arg" - Parameterized adapter (e.g., ToolAdapterBridge)
        """

        # Parse module path
        if "#" in module_path:
            # Parameterized adapter
            class_path, param = module_path.split("#", 1)
            module_name, class_name = class_path.rsplit(":", 1)

            # Import module
            module = importlib.import_module(module_name)
            adapter_class = getattr(module, class_name)

            # Instantiate with parameter
            return adapter_class(param)

        else:
            # Standard adapter
            module_name, class_name = module_path.rsplit(":", 1)

            # Import module
            module = importlib.import_module(module_name)
            adapter_class = getattr(module, class_name)

            # Instantiate
            return adapter_class()

    def is_registered(self, name: str) -> bool:
        """Check if an adapter is registered (but not necessarily instantiated)."""
        return (
            name in self._instances or
            name in self._classes or
            name in self._module_paths
        )

    def list_registered(self) -> list[str]:
        """List all registered adapter names (including non-instantiated)."""
        all_names = set(self._instances.keys()) | set(self._classes.keys()) | set(self._module_paths.keys())
        return sorted(all_names)

    def list_available(self) -> list[str]:
        """List adapters that are available (can be instantiated)."""
        available = []

        for name in self.list_registered():
            if name in self._failed_adapters:
                continue

            # Try to create it (will use cache if already exists)
            adapter = self.create(name)
            if adapter and adapter.is_available():
                available.append(name)

        return available

    def clear_cache(self) -> None:
        """Clear the instance cache (useful for testing)."""
        self._instances.clear()
        self._failed_adapters.clear()
        logger.debug("Cleared adapter instance cache")

    def reload_adapter(self, name: str) -> Optional[BaseAdapter]:
        """Force reload an adapter (clears cache and re-instantiates)."""
        if name in self._instances:
            del self._instances[name]
        if name in self._failed_adapters:
            self._failed_adapters.remove(name)

        return self.create(name)


# Global factory instance
factory = AdapterFactory()
