from __future__ import annotations

from CLI_RESTART.scripts.check_schema_compatibility import compare_schemas


def test_compare_schemas_detects_removing_required() -> None:
    base = {"required": ["a", "b"], "properties": {"a": {"type": "string"}, "b": {"type": "number"}}}
    curr = {"required": ["a"], "properties": {"a": {"type": "string"}, "b": {"type": "number"}}}
    ok, reasons = compare_schemas(base, curr)
    assert not ok and any("Removed required" in r for r in reasons)


def test_compare_schemas_allows_optional_add() -> None:
    base = {"required": ["a"], "properties": {"a": {"type": "string"}}}
    curr = {"required": ["a"], "properties": {"a": {"type": "string"}, "c": {"type": "boolean"}}}
    ok, reasons = compare_schemas(base, curr)
    assert ok and reasons == []


def test_compare_schemas_detects_type_change() -> None:
    base = {"required": ["a"], "properties": {"a": {"type": "string"}}}
    curr = {"required": ["a"], "properties": {"a": {"type": "number"}}}
    ok, reasons = compare_schemas(base, curr)
    assert not ok and any("Changed type" in r for r in reasons)

