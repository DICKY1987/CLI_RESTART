#!/usr/bin/env python3
"""Manifest Validator for CLI Multi-Rapid."""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

try:
    import jsonschema
    from jsonschema import validate, ValidationError
except ImportError:
    print("jsonschema not installed. Run: pip install jsonschema")
    sys.exit(1)

try:
    import yaml  # noqa: F401
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ManifestValidator:
    def __init__(self, schema_dir: Path = Path("schemas")):
        self.schema_dir = schema_dir
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def load_schema(self, schema_name: str) -> Dict[str, Any]:
        schema_path = self.schema_dir / schema_name
        if not schema_path.exists():
            self.warnings.append(f"Schema not found: {schema_path}")
            return {}
        with open(schema_path) as f:
            return json.load(f)

    def validate_json_file(self, file_path: Path, schema_name: str) -> bool:
        if not file_path.exists():
            self.errors.append(f"File not found: {file_path}")
            return False
        try:
            with open(file_path) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in {file_path}: {e}")
            return False
        schema = self.load_schema(schema_name)
        if not schema:
            return True
        try:
            validate(instance=data, schema=schema)
            return True
        except ValidationError as e:
            self.errors.append(f"Validation failed for {file_path}: {e.message}")
            return False

    def validate_all(self) -> bool:
        results = []
        tasks_json = Path(".ai/tasks.json")
        if tasks_json.exists():
            results.append(self.validate_json_file(tasks_json, "job.schema.json"))
        return all(results) and len(self.errors) == 0

    def print_report(self):
        if self.errors:
            print("\nValidation Errors:")
            for error in self.errors:
                print(f"  - {error}")
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"  - {warning}")
        if not self.errors and not self.warnings:
            print("All manifests validated successfully")


def main():
    validator = ManifestValidator()
    success = validator.validate_all()
    validator.print_report()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

