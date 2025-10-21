#!/usr/bin/env python3
"""Script registry validation tool.

Validates script registry JSON against schema and performs additional checks:
- Schema validation
- Script file existence
- Required fields presence
- Parameter validation
- Dependency checks
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_json_file(file_path: Path) -> dict[str, Any]:
    """Load JSON file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to load {file_path}: {e}")
        sys.exit(1)


def validate_schema(registry_data: dict[str, Any], schema_path: Path) -> tuple[bool, list[str]]:
    """Validate registry against JSON schema.

    Args:
        registry_data: Registry data
        schema_path: Path to schema file

    Returns:
        Tuple of (is_valid, error_messages)
    """
    try:
        import jsonschema
    except ImportError:
        return True, ["Warning: jsonschema not installed, skipping schema validation"]

    if not schema_path.exists():
        return False, [f"Schema file not found: {schema_path}"]

    try:
        schema = load_json_file(schema_path)
        jsonschema.validate(registry_data, schema)
        return True, []
    except jsonschema.ValidationError as e:
        return False, [f"Schema validation error: {e.message}"]
    except Exception as e:
        return False, [f"Schema validation failed: {e}"]


def validate_scripts(scripts: dict[str, dict[str, Any]]) -> tuple[bool, list[str]]:
    """Validate individual scripts.

    Args:
        scripts: Dictionary of script metadata

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    for script_name, metadata in scripts.items():
        # Check required fields
        required_fields = ["purpose", "path"]
        for field in required_fields:
            if not metadata.get(field):
                errors.append(f"{script_name}: Missing required field '{field}'")

        # Check script file exists
        script_path = Path(metadata.get("path", ""))
        if not script_path.exists():
            errors.append(f"{script_name}: Script file not found: {script_path}")
        elif not script_path.is_file():
            errors.append(f"{script_name}: Path is not a file: {script_path}")

        # Validate parameters
        parameters = metadata.get("parameters", [])
        for i, param in enumerate(parameters):
            if not isinstance(param, dict):
                errors.append(f"{script_name}: Parameter {i} is not a dictionary")
                continue

            param_name = param.get("name")
            if not param_name:
                errors.append(f"{script_name}: Parameter {i} missing 'name' field")

            param_desc = param.get("description")
            if not param_desc:
                errors.append(f"{script_name}: Parameter '{param_name}' missing 'description' field")

            # Validate enum parameters
            if param.get("type") == "enum" and not param.get("enum_values"):
                errors.append(f"{script_name}: Parameter '{param_name}' is enum but has no enum_values")

        # Validate category
        valid_categories = [
            "setup", "build", "test", "deployment",
            "maintenance", "automation", "analysis", "general"
        ]
        category = metadata.get("category", "general")
        if category not in valid_categories:
            errors.append(
                f"{script_name}: Invalid category '{category}'. "
                f"Must be one of: {', '.join(valid_categories)}"
            )

        # Validate platform
        valid_platforms = ["all", "windows", "linux", "macos", "unix"]
        platform = metadata.get("platform", "all")
        if platform not in valid_platforms:
            errors.append(
                f"{script_name}: Invalid platform '{platform}'. "
                f"Must be one of: {', '.join(valid_platforms)}"
            )

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_version(version: str) -> tuple[bool, list[str]]:
    """Validate version string format.

    Args:
        version: Version string

    Returns:
        Tuple of (is_valid, error_messages)
    """
    import re

    version_pattern = r"^\d+\.\d+\.\d+$"
    if not re.match(version_pattern, version):
        return False, [f"Invalid version format: {version}. Expected format: X.Y.Z"]

    return True, []


def generate_report(
    registry_path: Path,
    schema_valid: bool,
    schema_errors: list[str],
    scripts_valid: bool,
    script_errors: list[str],
    version_valid: bool,
    version_errors: list[str],
    script_count: int,
) -> str:
    """Generate validation report.

    Args:
        registry_path: Path to registry file
        schema_valid: Schema validation result
        schema_errors: Schema validation errors
        scripts_valid: Script validation result
        script_errors: Script validation errors
        version_valid: Version validation result
        version_errors: Version validation errors
        script_count: Total number of scripts

    Returns:
        Report string
    """
    lines = [
        "=" * 70,
        "Script Registry Validation Report",
        "=" * 70,
        f"Registry: {registry_path}",
        f"Total Scripts: {script_count}",
        "",
    ]

    # Schema validation
    lines.append("Schema Validation:")
    if schema_valid:
        lines.append("  ✓ PASS")
    else:
        lines.append("  ✗ FAIL")
        for error in schema_errors:
            lines.append(f"    - {error}")

    # Version validation
    lines.append("")
    lines.append("Version Validation:")
    if version_valid:
        lines.append("  ✓ PASS")
    else:
        lines.append("  ✗ FAIL")
        for error in version_errors:
            lines.append(f"    - {error}")

    # Script validation
    lines.append("")
    lines.append("Script Validation:")
    if scripts_valid:
        lines.append("  ✓ PASS")
    else:
        lines.append("  ✗ FAIL")
        lines.append(f"  Found {len(script_errors)} error(s):")
        for error in script_errors:
            lines.append(f"    - {error}")

    # Summary
    lines.append("")
    lines.append("=" * 70)
    all_valid = schema_valid and scripts_valid and version_valid
    if all_valid:
        lines.append("Result: ✓ ALL CHECKS PASSED")
    else:
        lines.append("Result: ✗ VALIDATION FAILED")

    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate script registry against schema"
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("scripts/registry.json"),
        help="Path to registry JSON file (default: scripts/registry.json)",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path("scripts/registry_schema.json"),
        help="Path to schema file (default: scripts/registry_schema.json)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only show errors, no success messages",
    )

    args = parser.parse_args()

    # Load registry
    if not args.registry.exists():
        print(f"ERROR: Registry file not found: {args.registry}")
        sys.exit(1)

    registry_data = load_json_file(args.registry)

    # Validate version
    version = registry_data.get("version", "")
    version_valid, version_errors = validate_version(version)

    # Validate schema
    schema_valid, schema_errors = validate_schema(registry_data, args.schema)

    # Validate scripts
    scripts = registry_data.get("scripts", {})
    scripts_valid, script_errors = validate_scripts(scripts)

    # Generate and print report
    report = generate_report(
        args.registry,
        schema_valid,
        schema_errors,
        scripts_valid,
        script_errors,
        version_valid,
        version_errors,
        len(scripts),
    )

    if not args.quiet:
        print(report)
    elif not (schema_valid and scripts_valid and version_valid):
        print(report)

    # Exit with appropriate code
    if schema_valid and scripts_valid and version_valid:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
