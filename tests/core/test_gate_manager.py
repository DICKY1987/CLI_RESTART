#!/usr/bin/env python3
"""
Tests for core.gate_manager module

Test coverage for GateManager class and verification gate logic.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.cli_multi_rapid.core.gate_manager import GateManager, GateResult, GateType


# Fixtures

@pytest.fixture
def gate_manager():
    """Create a GateManager instance."""
    return GateManager()


@pytest.fixture
def test_report_file():
    """Create a temporary test report JSON file."""
    report = {
        "passed": 10,
        "failed": 0,
        "skipped": 2
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(report, f)
        return f.name


@pytest.fixture
def failed_test_report_file():
    """Create a temporary test report with failures."""
    report = {
        "passed": 8,
        "failed": 2,
        "skipped": 1
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(report, f)
        return f.name


# Test Gate Manager Initialization

def test_gate_manager_initialization():
    """Test GateManager initialization."""
    manager = GateManager()

    assert len(manager._gate_handlers) == 3  # TESTS_PASS, DIFF_LIMITS, SCHEMA_VALID
    assert GateType.TESTS_PASS in manager._gate_handlers
    assert GateType.DIFF_LIMITS in manager._gate_handlers
    assert GateType.SCHEMA_VALID in manager._gate_handlers


# Test Tests Pass Gate

def test_check_tests_pass_success(gate_manager, test_report_file):
    """Test tests_pass gate with passing tests."""
    gate = {
        "id": "gate1",
        "type": "tests_pass",
        "artifact": test_report_file
    }

    result = gate_manager.execute_gate(gate, [], None)

    assert result.success is True
    assert result.gate_id == "gate1"
    assert result.gate_type == GateType.TESTS_PASS
    assert "10 passed, 0 failed" in result.message
    assert result.details["passed"] == 10
    assert result.details["failed"] == 0


def test_check_tests_pass_failure(gate_manager, failed_test_report_file):
    """Test tests_pass gate with failing tests."""
    gate = {
        "id": "gate1",
        "type": "tests_pass",
        "artifact": failed_test_report_file
    }

    result = gate_manager.execute_gate(gate, [], None)

    assert result.success is False
    assert "8 passed, 2 failed" in result.message


def test_check_tests_pass_report_not_found(gate_manager):
    """Test tests_pass gate when report file doesn't exist."""
    gate = {
        "id": "gate1",
        "type": "tests_pass",
        "artifact": "nonexistent_report.json"
    }

    result = gate_manager.execute_gate(gate, [], None)

    assert result.success is False
    assert "not found" in result.message


def test_check_tests_pass_invalid_json(gate_manager):
    """Test tests_pass gate with invalid JSON file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("invalid json content")
        temp_path = f.name

    gate = {
        "id": "gate1",
        "type": "tests_pass",
        "artifact": temp_path
    }

    result = gate_manager.execute_gate(gate, [], None)

    assert result.success is False
    assert "Failed to load" in result.message


# Test Diff Limits Gate

def test_check_diff_limits_within_limits(gate_manager):
    """Test diff_limits gate when changes are within limits."""
    gate = {
        "id": "gate2",
        "type": "diff_limits",
        "max_files": 10,
        "max_lines": 500
    }

    context = {
        "diff_stats": {
            "files_changed": 5,
            "lines_changed": 200
        }
    }

    result = gate_manager.execute_gate(gate, [], context)

    assert result.success is True
    assert result.gate_type == GateType.DIFF_LIMITS
    assert "5/10 files" in result.message
    assert "200/500 lines" in result.message


def test_check_diff_limits_exceeds_file_limit(gate_manager):
    """Test diff_limits gate when file limit is exceeded."""
    gate = {
        "id": "gate2",
        "type": "diff_limits",
        "max_files": 10,
        "max_lines": 500
    }

    context = {
        "diff_stats": {
            "files_changed": 15,
            "lines_changed": 200
        }
    }

    result = gate_manager.execute_gate(gate, [], context)

    assert result.success is False


def test_check_diff_limits_exceeds_line_limit(gate_manager):
    """Test diff_limits gate when line limit is exceeded."""
    gate = {
        "id": "gate2",
        "type": "diff_limits",
        "max_files": 10,
        "max_lines": 500
    }

    context = {
        "diff_stats": {
            "files_changed": 5,
            "lines_changed": 600
        }
    }

    result = gate_manager.execute_gate(gate, [], context)

    assert result.success is False


def test_check_diff_limits_no_context(gate_manager):
    """Test diff_limits gate with no context (defaults to zero)."""
    gate = {
        "id": "gate2",
        "type": "diff_limits",
        "max_files": 10,
        "max_lines": 500
    }

    result = gate_manager.execute_gate(gate, [], None)

    assert result.success is True  # 0 files/lines within limits


# Test Schema Valid Gate

def test_check_schema_valid_missing_artifact_path(gate_manager):
    """Test schema_valid gate with missing artifact path."""
    gate = {
        "id": "gate3",
        "type": "schema_valid",
        "schema": "schema.json"
    }

    result = gate_manager.execute_gate(gate, [], None)

    assert result.success is False
    assert "Missing artifact or schema path" in result.message


def test_check_schema_valid_missing_schema_path(gate_manager):
    """Test schema_valid gate with missing schema path."""
    gate = {
        "id": "gate3",
        "type": "schema_valid",
        "artifact": "artifact.json"
    }

    result = gate_manager.execute_gate(gate, [], None)

    assert result.success is False
    assert "Missing artifact or schema path" in result.message


def test_check_schema_valid_artifact_not_found(gate_manager):
    """Test schema_valid gate when artifact doesn't exist."""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        schema_path = f.name

    gate = {
        "id": "gate3",
        "type": "schema_valid",
        "artifact": "nonexistent_artifact.json",
        "schema": schema_path
    }

    result = gate_manager.execute_gate(gate, [], None)

    assert result.success is False
    assert "Artifact not found" in result.message


def test_check_schema_valid_schema_not_found(gate_manager):
    """Test schema_valid gate when schema doesn't exist."""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        artifact_path = f.name

    gate = {
        "id": "gate3",
        "type": "schema_valid",
        "artifact": artifact_path,
        "schema": "nonexistent_schema.json"
    }

    result = gate_manager.execute_gate(gate, [], None)

    assert result.success is False
    assert "Schema not found" in result.message


# Test Custom Gate Registration

def test_register_custom_gate(gate_manager):
    """Test registering a custom gate handler."""
    def custom_handler(gate, artifacts, context):
        return GateResult(
            gate_id=gate["id"],
            gate_type=GateType.CUSTOM,
            success=True,
            message="Custom gate passed"
        )

    gate_manager.register_custom_gate("my_custom_gate", custom_handler)

    gate = {
        "id": "gate4",
        "type": "custom",
        "custom_type": "my_custom_gate"
    }

    result = gate_manager.execute_gate(gate, [], None)

    assert result.success is True
    assert "Custom gate passed" in result.message


def test_unregister_custom_gate(gate_manager):
    """Test unregistering a custom gate handler."""
    def custom_handler(gate, artifacts, context):
        return GateResult(
            gate_id=gate["id"],
            gate_type=GateType.CUSTOM,
            success=True,
            message="Custom"
        )

    gate_manager.register_custom_gate("my_gate", custom_handler)
    assert gate_manager.unregister_custom_gate("my_gate") is True
    assert gate_manager.unregister_custom_gate("my_gate") is False  # Already removed


def test_get_registered_gates(gate_manager):
    """Test getting list of registered gate types."""
    gates = gate_manager.get_registered_gates()

    assert "tests_pass" in gates
    assert "diff_limits" in gates
    assert "schema_valid" in gates


def test_get_registered_gates_with_custom(gate_manager):
    """Test getting registered gates including custom ones."""
    def custom_handler(gate, artifacts, context):
        return GateResult("id", GateType.CUSTOM, True, "OK")

    gate_manager.register_custom_gate("custom1", custom_handler)
    gate_manager.register_custom_gate("custom2", custom_handler)

    gates = gate_manager.get_registered_gates()

    assert "custom1" in gates
    assert "custom2" in gates


# Test Execute Multiple Gates

def test_execute_gates_multiple(gate_manager):
    """Test executing multiple gates."""
    context = {
        "diff_stats": {
            "files_changed": 3,
            "lines_changed": 100
        }
    }

    gates = [
        {"id": "gate1", "type": "diff_limits", "max_files": 10, "max_lines": 500},
        {"id": "gate2", "type": "diff_limits", "max_files": 5, "max_lines": 200},
    ]

    results = gate_manager.execute_gates(gates, [], context)

    assert len(results) == 2
    assert results[0].success is True
    assert results[1].success is True


def test_execute_gates_empty_list(gate_manager):
    """Test executing empty gate list."""
    results = gate_manager.execute_gates([], [], None)

    assert results == []


# Test Aggregate Results

def test_aggregate_gate_results_all_pass(gate_manager):
    """Test aggregating gate results when all pass."""
    results = [
        GateResult("gate1", GateType.TESTS_PASS, True, "OK"),
        GateResult("gate2", GateType.DIFF_LIMITS, True, "OK"),
    ]

    summary = gate_manager.aggregate_gate_results(results)

    assert summary["overall_success"] is True
    assert summary["total_gates"] == 2
    assert summary["gates_passed"] == 2
    assert summary["gates_failed"] == 0


def test_aggregate_gate_results_some_fail(gate_manager):
    """Test aggregating gate results with failures."""
    results = [
        GateResult("gate1", GateType.TESTS_PASS, True, "OK"),
        GateResult("gate2", GateType.DIFF_LIMITS, False, "Failed"),
    ]

    summary = gate_manager.aggregate_gate_results(results)

    assert summary["overall_success"] is False
    assert summary["total_gates"] == 2
    assert summary["gates_passed"] == 1
    assert summary["gates_failed"] == 1


def test_aggregate_gate_results_empty(gate_manager):
    """Test aggregating empty gate results."""
    summary = gate_manager.aggregate_gate_results([])

    assert summary["overall_success"] is True  # No failures = success
    assert summary["total_gates"] == 0
    assert summary["gates_passed"] == 0
    assert summary["gates_failed"] == 0


# Test Error Handling

def test_execute_gate_invalid_type(gate_manager):
    """Test executing gate with invalid type."""
    gate = {
        "id": "gate1",
        "type": "invalid_type"
    }

    result = gate_manager.execute_gate(gate, [], None)

    assert result.success is False
    assert result.gate_type == GateType.CUSTOM


def test_execute_gate_handler_exception(gate_manager):
    """Test gate execution when handler raises exception."""
    def broken_handler(gate, artifacts, context):
        raise Exception("Handler error")

    gate_manager.register_custom_gate("broken", broken_handler)

    gate = {
        "id": "gate1",
        "type": "custom",
        "custom_type": "broken"
    }

    result = gate_manager.execute_gate(gate, [], None)

    assert result.success is False
    assert "Gate execution failed" in result.message
