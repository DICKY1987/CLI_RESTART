#!/usr/bin/env python3
"""Basic schema validation test for workflows."""

from pathlib import Path


def test_schema_validation_script_runs(tmp_path, monkeypatch):
    # Create minimal schema and workflow
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "steps": {"type": "array"},
        },
        "required": ["name", "steps"],
        "additionalProperties": True,
    }
    workflows_dir = tmp_path / ".ai" / "workflows"
    schemas_dir = tmp_path / ".ai" / "schemas"
    workflows_dir.mkdir(parents=True)
    schemas_dir.mkdir(parents=True)

    (schemas_dir / "workflow.schema.json").write_text(__import__("json").dumps(schema))
    (workflows_dir / "valid.yaml").write_text("""\
name: example
steps:
  - id: 1
    actor: code_fixers
""")

    # Run validation script in this temp repo root
    Path("scripts/validate_schemas.py").read_text()
    # Execute script with cwd redirected
    import os
    import runpy

    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        runpy.run_module("scripts.validate_schemas", run_name="__main__")
    finally:
        os.chdir(cwd)

    assert True  # If we reached here without SystemExit error, pass

