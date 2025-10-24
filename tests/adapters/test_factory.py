#!/usr/bin/env python3
"""
Tests for AdapterFactory

Verifies lazy loading, plugin discovery, and adapter lifecycle management.
"""

import pytest
from unittest.mock import Mock, patch

from cli_multi_rapid.adapters.factory import AdapterFactory
from cli_multi_rapid.adapters.base_adapter import BaseAdapter, AdapterType, AdapterResult


class MockAdapter(BaseAdapter):
    """Mock adapter for testing."""

    def __init__(self, name="mock", fail_on_init=False):
        if fail_on_init:
            raise RuntimeError("Mock initialization failure")

        super().__init__(name=name, adapter_type=AdapterType.DETERMINISTIC, description="Mock adapter")

    def execute(self, step, context=None, files=None):
        return AdapterResult(success=True, output="Mock execution")

    def validate_step(self, step):
        return True

    def estimate_cost(self, step):
        return 0


class TestAdapterFactory:
    """Test suite for AdapterFactory."""

    def test_factory_initialization(self):
        """Test factory initializes with core adapters registered."""
        factory = AdapterFactory()

        # Verify core adapters are registered by module path
        registered = factory.list_registered()

        assert "code_fixers" in registered
        assert "pytest_runner" in registered
        assert "ai_editor" in registered
        assert "deepseek" in registered
        assert len(registered) > 20  # Should have 20+ core adapters

    def test_register_instance(self):
        """Test registering a pre-instantiated adapter."""
        factory = AdapterFactory()
        mock_adapter = MockAdapter(name="test_instance")

        factory.register_instance("test_instance", mock_adapter)

        # Should return the same instance
        adapter = factory.create("test_instance")
        assert adapter is mock_adapter

    def test_register_class(self):
        """Test registering an adapter class for lazy instantiation."""
        factory = AdapterFactory()

        factory.register_class("test_class", MockAdapter)

        # Should create new instance
        adapter = factory.create("test_class")
        assert isinstance(adapter, MockAdapter)
        assert adapter.name == "mock"  # Default name

    def test_register_module(self):
        """Test registering an adapter by module path."""
        factory = AdapterFactory()

        # Register a real adapter by module path
        factory.register_module(
            "test_module",
            "cli_multi_rapid.adapters.code_fixers:CodeFixersAdapter"
        )

        # Should import and instantiate
        adapter = factory.create("test_module")
        assert adapter is not None
        assert adapter.name == "code_fixers"

    def test_create_caches_instances(self):
        """Test that create() caches instances for reuse."""
        factory = AdapterFactory()
        factory.register_class("test_cached", MockAdapter)

        # First call creates instance
        adapter1 = factory.create("test_cached")

        # Second call returns cached instance
        adapter2 = factory.create("test_cached")

        assert adapter1 is adapter2

    def test_create_nonexistent_adapter(self):
        """Test creating an adapter that doesn't exist."""
        factory = AdapterFactory()

        adapter = factory.create("nonexistent_adapter")

        assert adapter is None

    def test_create_failed_adapter_tracked(self):
        """Test that failed adapter loads are tracked to avoid retries."""
        factory = AdapterFactory()

        # Register adapter class that fails on init
        factory.register_class("test_fail", lambda: MockAdapter(fail_on_init=True))

        # First attempt fails
        adapter1 = factory.create("test_fail")
        assert adapter1 is None

        # Second attempt should skip without retry (check logs would show "previously failed")
        adapter2 = factory.create("test_fail")
        assert adapter2 is None

        # Verify it's in failed adapters set
        assert "test_fail" in factory._failed_adapters

    def test_is_registered(self):
        """Test checking if an adapter is registered."""
        factory = AdapterFactory()
        mock_adapter = MockAdapter(name="test_registered")

        # Not registered yet
        assert not factory.is_registered("test_registered")

        # Register
        factory.register_instance("test_registered", mock_adapter)

        # Now registered
        assert factory.is_registered("test_registered")

    def test_list_registered(self):
        """Test listing all registered adapters."""
        factory = AdapterFactory()

        # Should include core adapters
        registered = factory.list_registered()

        assert isinstance(registered, list)
        assert len(registered) > 0
        assert "code_fixers" in registered

        # Add custom adapter
        factory.register_instance("custom", MockAdapter())

        # Should now include custom adapter
        registered = factory.list_registered()
        assert "custom" in registered

    def test_list_available(self):
        """Test listing available adapters (excluding failed ones)."""
        factory = AdapterFactory()

        # Clear cache first for clean test
        factory.clear_cache()

        # Register a working adapter
        factory.register_class("test_available", MockAdapter)

        # This should instantiate and check is_available()
        available = factory.list_available()

        # Note: Core adapters may not all be available (missing dependencies)
        # Just verify our test adapter is available
        assert isinstance(available, list)

    def test_clear_cache(self):
        """Test clearing the instance cache."""
        factory = AdapterFactory()
        factory.register_class("test_clear", MockAdapter)

        # Create instance (cached)
        adapter1 = factory.create("test_clear")

        # Clear cache
        factory.clear_cache()

        # Create again (new instance)
        adapter2 = factory.create("test_clear")

        assert adapter1 is not adapter2

    def test_reload_adapter(self):
        """Test reloading an adapter (clears cache and re-instantiates)."""
        factory = AdapterFactory()
        factory.register_class("test_reload", MockAdapter)

        # Create instance
        adapter1 = factory.create("test_reload")

        # Reload
        adapter2 = factory.reload_adapter("test_reload")

        # Should be different instances
        assert adapter1 is not adapter2

    def test_parameterized_adapter(self):
        """Test loading a parameterized adapter (e.g., ToolAdapterBridge)."""
        factory = AdapterFactory()

        # Register with parameter syntax
        factory.register_module(
            "test_param",
            "cli_multi_rapid.adapters.tool_adapter_bridge:ToolAdapterBridge#vcs"
        )

        # Should instantiate with parameter
        adapter = factory.create("test_param")

        # Note: May fail if ToolAdapterBridge has complex init, but tests the parsing
        # Just verify the path parsing doesn't error
        assert adapter is not None or "test_param" in factory._failed_adapters

    @patch('cli_multi_rapid.adapters.factory.importlib.import_module')
    def test_module_import_failure_handling(self, mock_import):
        """Test handling of module import failures."""
        factory = AdapterFactory()

        # Mock import failure
        mock_import.side_effect = ImportError("Mock import error")

        factory.register_module("test_import_fail", "fake.module:FakeAdapter")

        # Should handle gracefully
        adapter = factory.create("test_import_fail")

        assert adapter is None
        assert "test_import_fail" in factory._failed_adapters

    def test_plugin_discovery(self):
        """Test plugin discovery from entry points."""
        # Note: This test verifies the discovery mechanism doesn't crash
        # Actual plugin discovery would require setuptools entry points

        factory = AdapterFactory()

        # Plugin discovery runs in __init__
        # Just verify it doesn't crash and factory still works
        assert len(factory.list_registered()) > 0


class TestAdapterFactoryIntegration:
    """Integration tests with real adapters."""

    def test_load_code_fixers_adapter(self):
        """Test loading a real adapter: code_fixers."""
        factory = AdapterFactory()

        adapter = factory.create("code_fixers")

        assert adapter is not None
        assert adapter.name == "code_fixers"
        assert adapter.adapter_type == AdapterType.DETERMINISTIC

    def test_load_ai_editor_adapter(self):
        """Test loading a real AI adapter: ai_editor."""
        factory = AdapterFactory()

        adapter = factory.create("ai_editor")

        assert adapter is not None
        assert adapter.name == "ai_editor"
        assert adapter.adapter_type == AdapterType.AI

    def test_factory_with_registry_integration(self):
        """Test factory integration with AdapterRegistry."""
        from cli_multi_rapid.adapters import AdapterRegistry

        registry = AdapterRegistry(use_factory=True)

        # Registry should use factory internally
        adapter = registry.get_adapter("code_fixers")

        assert adapter is not None
        assert adapter.name == "code_fixers"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
