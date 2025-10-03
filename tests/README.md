# Tests Directory

## Overview

This directory contains the test suite for the CLI Orchestrator project. We maintain ≥85% code coverage and comprehensive test categories.

## Directory Structure

```
tests/
├── conftest.py              # Shared pytest fixtures and configuration
├── unit/                    # Fast, isolated unit tests
│   ├── adapters/           # Adapter tests
│   ├── coordination/       # Coordination logic tests
│   ├── validation/         # Validation framework tests
│   └── ...
├── integration/            # Integration tests requiring services
│   ├── conftest.py        # Integration-specific fixtures
│   ├── workflows/         # End-to-end workflow tests
│   └── fixtures/          # Test data and helpers
└── examples/               # Example tests demonstrating patterns
    └── test_example_adapter.py
```

## Quick Start

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific category
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m "not slow"        # Exclude slow tests

# Run in parallel
pytest -n auto              # Auto-detect CPU count
pytest -n 4                 # Use 4 workers
```

### Writing Tests

1. Create test file with `test_` prefix
2. Import fixtures from conftest.py
3. Use appropriate markers
4. Follow Arrange-Act-Assert pattern

Example:

```python
import pytest
from src.cli_multi_rapid.adapters.base_adapter import AdapterResult

@pytest.mark.unit
def test_adapter_execution(mock_adapters):
    """Test adapter executes successfully."""
    # Arrange
    adapter = mock_adapters['mock_deterministic']
    step = {'id': '1.001', 'actor': 'mock_deterministic'}

    # Act
    result = adapter.execute(step)

    # Assert
    assert result.success is True
    assert isinstance(result, AdapterResult)
```

## Test Categories

### Markers

- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Tests requiring external services
- `@pytest.mark.e2e` - End-to-end workflow tests
- `@pytest.mark.contract` - API/schema contract tests
- `@pytest.mark.performance` - Performance benchmarking tests
- `@pytest.mark.security` - Security-focused tests
- `@pytest.mark.slow` - Long-running tests

### Test Organization

**Unit Tests (`unit/`):**
- Test individual functions/classes
- No external dependencies
- Fast execution (< 100ms per test)
- Mock all external interactions

**Integration Tests (`integration/`):**
- Test component interactions
- May use real services (isolated)
- Slower execution (< 5s per test)
- Use fixtures for setup/teardown

**E2E Tests (`e2e/`):**
- Test complete workflows
- Real system interactions
- Slowest execution
- Run in dedicated CI jobs

## Available Fixtures

### Core Fixtures (from conftest.py)

- `temp_dir` - Temporary directory for test files
- `test_config` - Service configuration for testing
- `mock_adapters` - Mock adapters (deterministic and AI)
- `sample_workflow` - Sample workflow definition
- `workflow_file` - Sample workflow YAML file
- `workflow_schema` - JSON schema for validation
- `test_data_factory` - Factory for generating test data
- `test_utils` - Testing utilities
- `performance_monitor` - Performance monitoring
- `contract_validator` - Contract validation

### Using Fixtures

```python
def test_with_fixtures(temp_dir, mock_adapters, test_data_factory):
    """Example using multiple fixtures."""
    # Create test workflow
    workflow = test_data_factory.create_workflow_data(
        name="Test Workflow"
    )

    # Use temp directory
    output_file = temp_dir / "output.json"

    # Use mock adapter
    adapter = mock_adapters['mock_deterministic']
    result = adapter.execute({'id': '1.001', 'actor': 'mock_deterministic'})

    assert result.success is True
```

## Coverage Requirements

- **Overall**: ≥85% coverage
- **Critical paths**: ≥95% recommended
- **New code**: Must not decrease coverage

### Checking Coverage

```bash
# Terminal report
pytest --cov=src --cov-report=term-missing

# HTML report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# XML report (for CI)
pytest --cov=src --cov-report=xml

# Fail if below threshold
pytest --cov=src --cov-fail-under=85
```

## Integration Test Setup

Integration tests use isolated fixtures:

```python
@pytest.fixture
async def isolated_service(temp_dir):
    """Create isolated service for testing."""
    service = await create_service(temp_dir)
    yield service
    await service.cleanup()

@pytest.mark.integration
async def test_service_operation(isolated_service):
    """Test service in isolation."""
    result = await isolated_service.execute()
    assert result.success is True
```

## Continuous Integration

Tests run automatically in CI:

- **On Push**: Full test suite with coverage
- **On PR**: Coverage check with PR comments
- **Nightly**: Extended test suite including slow tests

### Local CI Simulation

```bash
# Run what CI runs
pytest --cov=src --cov-report=xml --cov-fail-under=85 -v
```

## Troubleshooting

### Common Issues

1. **Import errors**: `pip install -e .`
2. **Fixture not found**: Check conftest.py location
3. **Slow tests**: Use `pytest -m "not slow"`
4. **Coverage gaps**: `pytest --cov=src --cov-report=html` then check htmlcov/

### Debug Mode

```bash
# Verbose output
pytest -vv

# Show print statements
pytest -s

# Drop into debugger on failure
pytest --pdb

# Run single test with debugging
pytest tests/unit/test_something.py::test_function -vv -s
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Speed**: Keep unit tests fast
3. **Coverage**: Test edge cases and error paths
4. **Documentation**: Document complex setups
5. **Naming**: Use descriptive test names
6. **Structure**: Follow Arrange-Act-Assert
7. **Cleanup**: Always clean up resources

## Resources

- [Testing Guide](../docs/development/testing-guide.md) - Comprehensive testing documentation
- [pytest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [CONTRIBUTING.md](../CONTRIBUTING.md)
