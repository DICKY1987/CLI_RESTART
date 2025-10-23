#!/usr/bin/env python3
"""
Tests for Enhanced AdapterRegistry

Verifies factory integration, backward compatibility, and deprecation warnings.
"""

import pytest
import warnings
from unittest.mock import Mock, patch

from cli_multi_rapid.adapters.adapter_registry import AdapterRegistry
from cli_multi_rapid.adapters.base_adapter import BaseAdapter, AdapterType, AdapterResult


class MockAdapter(BaseAdapter):
    """Mock adapter for testing."""

    def __init__(self, name="mock"):
        super().__init__(name=name, adapter_type=AdapterType.DETERMINISTIC, description="Mock adapter")

    def execute(self, step, context=None, files=None):
        return AdapterResult(success=True, output="Mock execution")

    def validate_step(self, step):
        return True

    def estimate_cost(self, step):
        return 0


class TestAdapterRegistry:
    """Test suite for enhanced AdapterRegistry."""

    def test_registry_initialization_with_factory(self):
        """Test registry initializes with factory enabled by default."""
        registry = AdapterRegistry(use_factory=True)

        assert registry._use_factory is True
        assert registry._factory is not None

        # Should have core adapters from factory
        adapters = registry.list_adapters()
        assert len(adapters) > 0

    def test_registry_initialization_legacy_mode(self):
        """Test registry initialization in legacy mode (no factory)."""
        registry = AdapterRegistry(use_factory=False)

        assert registry._use_factory is False
        assert registry._factory is None

        # Legacy mode auto-registers core adapters
        adapters = registry.list_adapters()
        assert "code_fixers" in adapters

    def test_register_instance(self):
        """Test registering an adapter instance."""
        registry = AdapterRegistry(use_factory=True)
        mock_adapter = MockAdapter(name="test_instance")

        registry.register(mock_adapter)

        # Should be registered locally
        assert "test_instance" in registry._adapters

        # Should also be registered in factory
        assert registry._factory.is_registered("test_instance")

    def test_register_class_with_deprecation_warning(self):
        """Test that register_class() emits deprecation warning."""
        registry = AdapterRegistry(use_factory=True)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            registry.register_class("test_class", MockAdapter)

            # Should emit DeprecationWarning
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()

    def test_get_adapter_from_factory(self):
        """Test getting an adapter via factory."""
        registry = AdapterRegistry(use_factory=True)

        # Get a core adapter (should load from factory)
        adapter = registry.get_adapter("code_fixers")

        assert adapter is not None
        assert adapter.name == "code_fixers"

        # Should be cached locally
        assert "code_fixers" in registry._adapters

    def test_get_adapter_legacy_mode(self):
        """Test getting an adapter in legacy mode (no factory)."""
        registry = AdapterRegistry(use_factory=False)

        # Register an adapter class
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Suppress deprecation warning for test
            registry.register_class("test_legacy", MockAdapter)

        # Get adapter (should use legacy instantiation)
        adapter = registry.get_adapter("test_legacy")

        assert adapter is not None
        assert isinstance(adapter, MockAdapter)

    def test_get_adapter_caching(self):
        """Test that get_adapter() caches instances."""
        registry = AdapterRegistry(use_factory=True)

        adapter1 = registry.get_adapter("code_fixers")
        adapter2 = registry.get_adapter("code_fixers")

        # Should return same instance
        assert adapter1 is adapter2

    def test_get_adapter_nonexistent(self):
        """Test getting a nonexistent adapter."""
        registry = AdapterRegistry(use_factory=True)

        adapter = registry.get_adapter("nonexistent_adapter")

        assert adapter is None

    def test_get_available_adapters(self):
        """Test getting all available adapters with metadata."""
        registry = AdapterRegistry(use_factory=True)

        available = registry.get_available_adapters()

        assert isinstance(available, dict)
        assert len(available) > 0

        # Check metadata structure
        if "code_fixers" in available:
            adapter_meta = available["code_fixers"]
            assert "name" in adapter_meta
            assert "type" in adapter_meta
            assert "description" in adapter_meta

    def test_get_adapters_by_type(self):
        """Test filtering adapters by type."""
        registry = AdapterRegistry(use_factory=True)

        # Get deterministic adapters
        deterministic = registry.get_adapters_by_type(AdapterType.DETERMINISTIC)

        assert isinstance(deterministic, list)
        # Note: May be empty if adapters not instantiated yet

        # Register a mock adapter to ensure we have at least one
        mock_adapter = MockAdapter(name="test_deterministic")
        registry.register(mock_adapter)

        deterministic = registry.get_adapters_by_type(AdapterType.DETERMINISTIC)
        assert "test_deterministic" in deterministic

    def test_is_available(self):
        """Test checking adapter availability."""
        registry = AdapterRegistry(use_factory=True)

        # code_fixers should be available (no external dependencies)
        is_available = registry.is_available("code_fixers")

        # May be True or False depending on environment, just verify no crash
        assert isinstance(is_available, bool)

    def test_validate_step(self):
        """Test validating a step with an adapter."""
        registry = AdapterRegistry(use_factory=True)

        step = {"actor": "code_fixers", "with": {"tools": ["black"]}}

        # Should validate (or return False if adapter not available)
        result = registry.validate_step("code_fixers", step)

        assert isinstance(result, bool)

    def test_estimate_cost(self):
        """Test estimating cost with an adapter."""
        registry = AdapterRegistry(use_factory=True)

        step = {"actor": "code_fixers"}

        # Deterministic adapter should return 0 cost
        cost = registry.estimate_cost("code_fixers", step)

        assert cost == 0

    def test_list_adapters_includes_factory_adapters(self):
        """Test that list_adapters() includes factory-registered adapters."""
        registry = AdapterRegistry(use_factory=True)

        adapters = registry.list_adapters()

        # Should include core adapters from factory
        assert "code_fixers" in adapters
        assert "ai_editor" in adapters
        assert "deepseek" in adapters

    def test_list_available_adapters_alias(self):
        """Test backward compatibility alias for list_available_adapters()."""
        registry = AdapterRegistry(use_factory=True)

        available = registry.list_available_adapters()

        assert isinstance(available, dict)
        assert available == registry.get_available_adapters()


class TestAdapterRegistryIntegration:
    """Integration tests for AdapterRegistry with Router."""

    def test_registry_with_router(self):
        """Test registry integration with Router."""
        from cli_multi_rapid.router import Router

        # Router should initialize with factory-enabled registry
        router = Router()

        assert router.registry is not None
        assert router.registry._use_factory is True

        # Should have adapters loaded
        adapters = router.registry.list_adapters()
        assert len(adapters) > 0

    def test_router_adapter_lazy_loading(self):
        """Test that Router lazy-loads adapters via factory."""
        from cli_multi_rapid.router import Router

        router = Router()

        # Adapters should not be instantiated yet (lazy loading)
        # Factory has module paths but not instances

        # Get an adapter (should trigger lazy load)
        adapter = router.registry.get_adapter("code_fixers")

        assert adapter is not None
        assert adapter.name == "code_fixers"

    def test_router_routing_with_factory_adapters(self):
        """Test Router.route_step() works with factory-loaded adapters."""
        from cli_multi_rapid.router import Router

        router = Router()

        step = {
            "id": "test",
            "name": "Test Step",
            "actor": "code_fixers",
            "with": {"tools": ["black"]}
        }

        decision = router.route_step(step)

        assert decision is not None
        assert decision.adapter_name in ["code_fixers", "vscode_diagnostics"]  # May route to alternative

    def test_circular_dependency_eliminated(self):
        """Verify that circular dependencies are eliminated."""
        # This test verifies that importing doesn't cause circular import errors

        try:
            from cli_multi_rapid.router import Router
            from cli_multi_rapid.adapters.factory import AdapterFactory
            from cli_multi_rapid.adapters import AdapterRegistry

            # Should import successfully without circular dependency errors
            router = Router()
            factory = AdapterFactory()
            registry = AdapterRegistry()

            # All should work
            assert router is not None
            assert factory is not None
            assert registry is not None

        except ImportError as e:
            pytest.fail(f"Circular dependency detected: {e}")


class TestBackwardCompatibility:
    """Test backward compatibility with existing code."""

    def test_direct_adapter_registration_still_works(self):
        """Test that old code using direct registration still works."""
        registry = AdapterRegistry(use_factory=True)

        # Old code pattern: direct instance registration
        mock_adapter = MockAdapter(name="test_old_style")
        registry.register(mock_adapter)

        # Should still work
        adapter = registry.get_adapter("test_old_style")
        assert adapter is mock_adapter

    def test_legacy_registry_mode_still_works(self):
        """Test that legacy mode (no factory) still works for old code."""
        registry = AdapterRegistry(use_factory=False)

        # Old auto-registration should still work
        adapters = registry.list_adapters()

        # Should have some adapters from auto-registration
        assert len(adapters) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
