from __future__ import annotations

import pytest

from cli_multi_rapid.adapters.base_adapter import (
    AdapterResult,
    AdapterType,
    BaseAdapter,
)
from cli_multi_rapid.validation.contract_validator import ValidationError


class DemoAdapter(BaseAdapter):
    def __init__(self) -> None:
        super().__init__(name="demo", adapter_type=AdapterType.DETERMINISTIC, description="demo")

    def get_input_schema(self):
        return "workflow.schema.json"

    def get_output_schema(self):
        # Validate against minimal adapter result schema we provide
        return "adapter_result.schema.json"

    def execute(self, step, context=None, files=None):
        # Just echo a minimal result conforming to test_report expectations
        return AdapterResult(success=True, output="ok", metadata={})

    def validate_step(self, step):
        return True

    def estimate_cost(self, step):
        return 0


def test_adapter_input_schema_validation_passes():
    adapter = DemoAdapter()
    step = {
        "name": "demo",
        "simplified": True,
        "framework_version": "simplified-25ops",
        "operations": [],
    }
    # Should not raise
    adapter.validate_input_schema(step)


def test_adapter_input_schema_validation_fails():
    adapter = DemoAdapter()
    bad_step = {"simplified": "invalid"}
    with pytest.raises(ValidationError):
        adapter.validate_input_schema(bad_step)


def test_adapter_output_schema_validation_passes():
    adapter = DemoAdapter()
    result = adapter.execute({})
    # Should not raise
    adapter.validate_output_schema(result)
