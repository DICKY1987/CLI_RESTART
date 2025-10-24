import os
from pathlib import Path
import pytest

# Define the root of your project and the source directory
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIRECTORY = PROJECT_ROOT / "src" / "cli_multi_rapid"

# Define architectural constraints
MAX_FILE_SIZE_LINES = 400

def get_all_python_files(directory):
    """Recursively finds all Python files in a directory."""
    return list(directory.rglob("*.py"))

@pytest.mark.architecture
def test_file_size_limits():
    """Tests that all Python files in the source directory are within size limits."""
    all_files = get_all_python_files(SRC_DIRECTORY)
    oversized_files = []

    for file_path in all_files:
        # ignore __init__.py files for file size limits
        if file_path.name == "__init__.py":
            continue
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                line_count = len(f.readlines())
                if line_count > MAX_FILE_SIZE_LINES:
                    relative_path = file_path.relative_to(PROJECT_ROOT)
                    oversized_files.append(f"{relative_path} ({line_count} lines)")
            except UnicodeDecodeError:
                relative_path = file_path.relative_to(PROJECT_ROOT)
                oversized_files.append(f"{relative_path} (UnicodeDecodeError)")

    assert not oversized_files, f"The following files exceed the {MAX_FILE_SIZE_LINES}-line limit:\n" + "\n".join(oversized_files)

@pytest.mark.architecture
def test_domain_does_not_import_adapters():
    """Ensures the domain layer does not import from the adapters layer."""
    domain_directory = SRC_DIRECTORY / "domain"
    adapters_package = "cli_multi_rapid.adapters"
    illegal_imports = []

    for file_path in get_all_python_files(domain_directory):
        with open(file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                if f"from {adapters_package}" in line or f"import {adapters_package}" in line:
                    relative_path = file_path.relative_to(PROJECT_ROOT)
                    illegal_imports.append(f"{relative_path}:{i}: {line.strip()}")

    assert not illegal_imports, "Illegal imports from adapters layer found in domain layer:\n" + "\n".join(illegal_imports)

@pytest.mark.architecture
def test_no_circular_imports():
    """Checks for circular imports in the source directory."""
    try:
        import networkx as nx
    except ImportError:
        pytest.skip("networkx not installed, skipping circular import test.")

    graph = nx.DiGraph()
    all_files = get_all_python_files(SRC_DIRECTORY)
    module_map = {file_path.relative_to(PROJECT_ROOT).with_suffix("").as_posix().replace("/", "."): file_path for file_path in all_files}

    for module_name, file_path in module_map.items():
        graph.add_node(module_name)
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                content = f.read()
                for other_module in module_map:
                    if f"import {other_module}" in content or f"from {other_module}" in content:
                        if module_name != other_module:
                            graph.add_edge(module_name, other_module)
            except UnicodeDecodeError:
                continue

    try:
        cycles = list(nx.simple_cycles(graph))
        assert not cycles, "Circular dependencies found:\n" + "\n".join(" -> ".join(cycle) for cycle in cycles)
    except nx.NetworkXError as e:
        pytest.fail(f"Error checking for circular dependencies: {e}")

