from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from ..models import GateResult


def _basic_validation(artifact: dict[str, Any]) -> bool:
    required_fields = ["timestamp", "type"]
    return all(field in artifact for field in required_fields)


def _validate_against_schema(artifact: dict[str, Any], schema_file: Path) -> bool:
    try:
        import jsonschema
        with open(schema_file, encoding="utf-8") as f:
            schema = json.load(f)
        jsonschema.validate(artifact, schema)
        return True
    except ImportError:
        return _basic_validation(artifact)
    except Exception:
        return False


def verify_artifact(artifact_file: Path, schema_file: Optional[Path] = None) -> bool:
    try:
        if not artifact_file.exists():
            return False
        with open(artifact_file, encoding="utf-8") as f:
            artifact = json.load(f)
        if schema_file and schema_file.exists():
            return _validate_against_schema(artifact, schema_file)
        return _basic_validation(artifact)
    except Exception:
        return False


class SchemaGate:
    """Check if specified artifacts are valid against schemas or basic checks."""

    def check(self, gate_config: dict, artifacts_dir: Path) -> GateResult:
        try:
            artifacts = gate_config.get("artifacts", [])
            schema_dir = Path(gate_config.get("schema_dir", ".ai/schemas"))
            mapping: dict[str, str] = gate_config.get("schema_map", {})
            if not artifacts:
                return GateResult(gate_name="schema_valid", passed=True, message="No artifacts specified")

            all_ok = True
            details: dict[str, Any] = {}
            for art in artifacts:
                art_path = artifacts_dir / art if not art.startswith("/") else Path(art)
                schema_file: Optional[Path] = None
                if mapping and art in mapping:
                    schema_file = Path(mapping[art])
                else:
                    name = Path(art).name
                    if "code-review" in name:
                        schema_file = schema_dir / "ai_code_review.schema.json"
                    elif "architecture" in name:
                        schema_file = schema_dir / "ai_architecture_analysis.schema.json"
                    elif "refactor-plan" in name:
                        schema_file = schema_dir / "ai_refactor_plan.schema.json"
                    elif "test-plan" in name:
                        schema_file = schema_dir / "ai_test_plan.schema.json"
                    elif "improvements" in name:
                        schema_file = schema_dir / "ai_improvements.schema.json"

                ok = verify_artifact(art_path, schema_file)
                details[str(art_path)] = ok
                all_ok = all_ok and ok
            return GateResult(
                gate_name="schema_valid",
                passed=all_ok,
                message=("All artifacts valid" if all_ok else "One or more artifacts invalid"),
                details=details,
            )
        except Exception as e:
            return GateResult(gate_name="schema_valid", passed=False, message=f"Schema gate error: {e}")


class YamlSchemaGate:
    """Validate a YAML file against a JSON schema."""

    def check(self, gate_config: dict, artifacts_dir: Path) -> GateResult:
        try:
            import json
            import jsonschema  # type: ignore
            import yaml  # type: ignore

            yaml_path = Path(gate_config.get("file", ""))
            schema_path = Path(gate_config.get("schema", ""))
            if not yaml_path.exists():
                return GateResult(gate_name="yaml_schema_valid", passed=False, message=f"YAML file not found: {yaml_path}")
            if not schema_path.exists():
                return GateResult(gate_name="yaml_schema_valid", passed=False, message=f"Schema file not found: {schema_path}")
            with open(yaml_path, encoding="utf-8") as yf:
                data = yaml.safe_load(yf)
            with open(schema_path, encoding="utf-8") as sf:
                schema = json.load(sf)
            jsonschema.validate(data, schema)
            return GateResult(gate_name="yaml_schema_valid", passed=True, message="YAML schema validation passed")
        except ImportError as e:
            return GateResult(gate_name="yaml_schema_valid", passed=False, message=f"Missing dependency for YAML/JSON schema validation: {e}")
        except Exception as e:
            return GateResult(gate_name="yaml_schema_valid", passed=False, message=f"YAML schema validation failed: {e}")

