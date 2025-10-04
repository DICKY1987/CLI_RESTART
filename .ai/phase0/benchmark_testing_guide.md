# Benchmark Testing Guide

## Overview
Performance benchmarks are optional and require the `pytest-benchmark` plugin. They are skipped by default during regular test runs.

## Installation
```bash
# Install benchmark plugin
pip install pytest-benchmark

# Or install benchmark optional dependency group
pip install -e .[benchmark]
```

## Running Benchmarks
```bash
# Run only benchmark tests
pytest -m benchmark

# Run benchmarks with comparison
pytest -m benchmark --benchmark-compare

# Save benchmark results
pytest -m benchmark --benchmark-save=baseline
```

## Affected Test Files
- tests/benchmarks/test_gdw_bench.py
- tests/performance/test_workflow_performance.py

## Why Skipped by Default
Benchmark tests are slow and not needed during regular development. They should be run:
- Before major releases
- When optimizing performance (Phase 10)
- When investigating performance regressions
- In dedicated performance CI jobs
