# CLI Multi-Rapid Development Makefile
# Cross-platform development commands for Python/TypeScript/MQL4

.PHONY: help install install-dev test test\:py test\:ps test\:js test-integration lint format type-check security-check clean build package ci docs coverage

POWERSHELL := pwsh
ifeq ($(OS),Windows_NT)
POWERSHELL := powershell
endif

# Default target
help:
	@echo "CLI Multi-Rapid Development Commands"
	@echo "===================================="
	@echo ""
	@echo "Installation:"
	@echo "  install          Install production dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo ""
	@echo "Testing:"
        @echo "  test             Run all automated test suites"
        @echo "  test:py          Run only Python unit tests"
        @echo "  test:ps          Run only PowerShell tests"
        @echo "  test:js          Run only JavaScript tests (if configured)"
        @echo "  test-integration Run integration tests"
        @echo "  coverage        Generate coverage reports"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint             Run linting (ruff, eslint)"
	@echo "  format           Format code (black, prettier)"
	@echo "  type-check       Run type checking (mypy, tsc)"
	@echo "  security-check   Run security scans (bandit, audit)"
	@echo ""
	@echo "Build & Package:"
	@echo "  clean            Clean build artifacts"
	@echo "  build            Build all components"
	@echo "  package          Package for distribution"
	@echo ""
	@echo "Development:"
	@echo "  ci               Run full CI pipeline locally"
	@echo "  pre-commit       Run pre-commit hooks"
	@echo "  docs             Generate documentation"

# Installation targets
install:
	pip install -e .

install-dev:
	pip install -e .[dev,ai,test]
	cd vscode-extension && npm ci
	pre-commit install

# Testing targets
test:
        $(POWERSHELL) -NoProfile -ExecutionPolicy Bypass -File scripts/run_all_tests.ps1

test\:py:
        $(POWERSHELL) -NoProfile -ExecutionPolicy Bypass -File scripts/run_all_tests.ps1 -SkipPowerShell -SkipNode

test\:ps:
        $(POWERSHELL) -NoProfile -ExecutionPolicy Bypass -File scripts/run_all_tests.ps1 -SkipPython -SkipNode

test\:js:
        $(POWERSHELL) -NoProfile -ExecutionPolicy Bypass -File scripts/run_all_tests.ps1 -SkipPython -SkipPowerShell

test-integration:
        pytest tests/integration/ -v --tb=short -m "not slow"

coverage: test

# Code quality targets
lint:
	@echo "Running Python linting..."
	ruff check src/ tests/ --output-format=github
	@echo "Running TypeScript linting..."
	cd vscode-extension && npm run lint

format:
	@echo "Formatting Python code..."
	black src/ tests/
	isort src/ tests/ --profile black
	@echo "Formatting TypeScript code..."
	cd vscode-extension && npm run lint:fix

type-check:
	@echo "Running Python type checking..."
	mypy src/ --ignore-missing-imports
	@echo "Running TypeScript type checking..."
	cd vscode-extension && npx tsc --noEmit

security-check:
	@echo "Running Python security checks..."
	bandit -r src/ -f json -o bandit-report.json || echo "Security scan completed with findings"
	safety check --output json || echo "Dependency scan completed with findings"
	@echo "Running TypeScript security checks..."
	cd vscode-extension && npm audit || echo "npm audit completed with findings"

# Build targets
clean:
	@echo "Cleaning Python artifacts..."
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .coverage htmlcov/
	rm -rf src/**/__pycache__/ tests/**/__pycache__/
	@echo "Cleaning TypeScript artifacts..."
	cd vscode-extension && npm run clean
	@echo "Cleaning MQL4 artifacts..."
	rm -rf artifacts/mql4/

build:
	@echo "Building Python package..."
	pip install build
	python -m build
	@echo "Building TypeScript extension..."
	cd vscode-extension && npm run build
	@echo "Processing MQL4 files..."
	powershell -File scripts/compile_mql4.ps1 -ValidateOnly

package:
	@echo "Packaging Python distribution..."
	python -m build
	@echo "Packaging VS Code extension..."
	cd vscode-extension && npm run package
	@echo "Packaging complete"

# CI pipeline
ci: lint type-check security-check test build
	@echo "CI pipeline completed successfully"

# Development helpers
pre-commit:
	pre-commit run --all-files

docs:
	@echo "Documentation generation not implemented yet"
	@echo "Future: Generate API docs, workflow schemas, etc."

# Windows-specific targets (PowerShell)
ifeq ($(OS),Windows_NT)
mql4-compile:
	powershell -File scripts/compile_mql4.ps1

mql4-validate:
	powershell -File scripts/compile_mql4.ps1 -ValidateOnly
else
mql4-compile:
	@echo "MQL4 compilation only supported on Windows"

mql4-validate:
	@echo "MQL4 validation only supported on Windows"
endif
