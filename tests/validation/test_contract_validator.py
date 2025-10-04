from __future__ import annotations

import pytest

from cli_multi_rapid.validation.contract_validator import (
    ContractValidator,
    ValidationError,
    validate_data,
)


def test_validate_data_workflow_valid_minimal():
    data = {
        "name": "demo",
        "simplified": True,
        "framework_version": "simplified-25ops",
        "operations": [],
    }
    assert validate_data(data, "workflow.schema.json") is True


def test_validate_data_workflow_invalid_type():
    # invalid type for simplified (should be boolean or null per schema)
    data = {"simplified": "yes"}
    assert validate_data(data, "workflow.schema.json") is False


def test_direct_validator_raises_on_error():
    validator = ContractValidator()
    with pytest.raises(ValidationError):
        validator.validate_input({"simplified": "nope"}, "workflow.schema.json")
