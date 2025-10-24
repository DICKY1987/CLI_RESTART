
import importlib
import inspect
import pkgutil
from pathlib import Path
import pytest

from cli_multi_rapid.adapters.base_adapter import BaseAdapter, AdapterResult

def get_all_adapter_classes():
    """Dynamically imports and discovers all adapter classes."""
    adapters_package = "cli_multi_rapid.adapters"
    package = importlib.import_module(adapters_package)
    adapter_classes = []

    for _, name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        if not is_pkg:
            try:
                module = importlib.import_module(name)
                for class_name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseAdapter) and obj is not BaseAdapter and not inspect.isabstract(obj):
                        adapter_classes.append(obj)
            except Exception as e:
                print(f"Could not import {name}: {e}")
    return adapter_classes

ALL_ADAPTERS = get_all_adapter_classes()

@pytest.mark.architecture
@pytest.mark.parametrize("adapter_class", ALL_ADAPTERS)
def test_adapters_implement_base_adapter(adapter_class):
    """Tests that all discovered adapters inherit from BaseAdapter."""
    assert issubclass(adapter_class, BaseAdapter), f"{adapter_class.__name__} does not implement BaseAdapter."

@pytest.mark.architecture
@pytest.mark.parametrize("adapter_class", ALL_ADAPTERS)
def test_execute_returns_adapter_result(adapter_class):
    """Tests that the execute method of all adapters has the correct return type hint."""
    execute_method = getattr(adapter_class, 'execute', None)
    assert execute_method is not None, f"{adapter_class.__name__} does not have an execute method."

    signature = inspect.signature(execute_method)
    return_annotation = signature.return_annotation

    # Check if the return annotation is AdapterResult or the string 'AdapterResult'
    assert return_annotation is AdapterResult or return_annotation == 'AdapterResult', f"{adapter_class.__name__}.execute has incorrect return type hint: {return_annotation}. Expected AdapterResult."

