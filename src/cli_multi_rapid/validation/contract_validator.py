#!/usr/bin/env python3
"""
Contract Validator

Provides runtime schema validation for adapter inputs/outputs and contract enforcement
at system boundaries. Integrates with JSON Schema for validation.
"""

import json
import logging
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

try:
    import jsonschema
    from jsonschema import Draft7Validator
    from jsonschema import ValidationError as JSONSchemaValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    JSONSchemaValidationError = Exception

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when schema validation fails."""

    def __init__(self, message: str, schema_path: Optional[str] = None, errors: Optional[list] = None):
        self.schema_path = schema_path
        self.validation_errors = errors or []
        super().__init__(message)

    def __str__(self):
        msg = super().__str__()
        if self.schema_path:
            msg += f"\nSchema: {self.schema_path}"
        if self.validation_errors:
            msg += "\nValidation errors:"
            for error in self.validation_errors:
                msg += f"\n  - {error}"
        return msg


class ContractValidator:
    """Validates data against JSON schemas and enforces contracts."""

    def __init__(self, schema_dir: Optional[Path] = None):
        """
        Initialize contract validator.

        Args:
            schema_dir: Directory containing JSON schema files.
                       Defaults to .ai/schemas/ in repository root.
        """
        if schema_dir is None:
            # Default to repository's schema directory
            repo_root = Path(__file__).parents[3]
            schema_dir = repo_root / ".ai" / "schemas"

        self.schema_dir = Path(schema_dir)
        self._schema_cache: dict[str, dict] = {}
        self._validator_cache: dict[str, Draft7Validator] = {}

        if not JSONSCHEMA_AVAILABLE:
            logger.warning("jsonschema package not available - schema validation disabled")

    def load_schema(self, schema_name: str) -> dict:
        """
        Load a JSON schema file.

        Args:
            schema_name: Name of schema file (with or without .json extension)

        Returns:
            Loaded schema dictionary

        Raises:
            FileNotFoundError: If schema file doesn't exist
            json.JSONDecodeError: If schema file is invalid JSON
        """
        # Add .json extension if not present
        if not schema_name.endswith('.json'):
            schema_name += '.json'

        # Check cache first
        if schema_name in self._schema_cache:
            return self._schema_cache[schema_name]

        # Load from file
        schema_path = self.schema_dir / schema_name

        if not schema_path.exists():
            # Try with .schema.json suffix
            alt_path = self.schema_dir / schema_name.replace('.json', '.schema.json')
            if alt_path.exists():
                schema_path = alt_path
            else:
                raise FileNotFoundError(f"Schema not found: {schema_path}")

        logger.debug(f"Loading schema from {schema_path}")

        with open(schema_path) as f:
            schema = json.load(f)

        # Cache the schema
        self._schema_cache[schema_name] = schema

        return schema

    def get_validator(self, schema_name: str) -> Optional[Draft7Validator]:
        """
        Get a JSON schema validator for the given schema.

        Args:
            schema_name: Name of schema file

        Returns:
            Draft7Validator instance or None if jsonschema not available
        """
        if not JSONSCHEMA_AVAILABLE:
            return None

        # Check cache first
        if schema_name in self._validator_cache:
            return self._validator_cache[schema_name]

        # Load schema and create validator
        schema = self.load_schema(schema_name)
        validator = Draft7Validator(schema)

        # Cache the validator
        self._validator_cache[schema_name] = validator

        return validator

    def validate(
        self,
        data: Any,
        schema_name: str,
        raise_on_error: bool = True
    ) -> tuple[bool, list[str]]:
        """
        Validate data against a JSON schema.

        Args:
            data: Data to validate
            schema_name: Name of schema file
            raise_on_error: Whether to raise ValidationError on failure

        Returns:
            Tuple of (is_valid, error_messages)

        Raises:
            ValidationError: If validation fails and raise_on_error=True
        """
        if not JSONSCHEMA_AVAILABLE:
            logger.warning(f"Skipping validation for {schema_name} - jsonschema not available")
            return True, []

        try:
            validator = self.get_validator(schema_name)
            if validator is None:
                return True, []

            # Validate the data
            errors = list(validator.iter_errors(data))

            if errors:
                error_messages = [
                    f"{'.'.join(map(str, error.path))}: {error.message}"
                    for error in errors
                ]

                if raise_on_error:
                    raise ValidationError(
                        f"Validation failed for schema {schema_name}",
                        schema_path=str(self.schema_dir / schema_name),
                        errors=error_messages
                    )

                return False, error_messages

            return True, []

        except FileNotFoundError as e:
            logger.error(f"Schema not found: {schema_name}")
            if raise_on_error:
                raise ValidationError(f"Schema not found: {schema_name}") from e
            return False, [str(e)]

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON schema {schema_name}: {e}")
            if raise_on_error:
                raise ValidationError(f"Invalid JSON schema: {schema_name}") from e
            return False, [str(e)]

    def validate_input(self, data: Any, schema_name: str) -> None:
        """
        Validate input data against schema.

        Args:
            data: Input data to validate
            schema_name: Name of input schema

        Raises:
            ValidationError: If validation fails
        """
        logger.debug(f"Validating input against schema: {schema_name}")
        self.validate(data, schema_name, raise_on_error=True)

    def validate_output(self, data: Any, schema_name: str) -> None:
        """
        Validate output data against schema.

        Args:
            data: Output data to validate
            schema_name: Name of output schema

        Raises:
            ValidationError: If validation fails
        """
        logger.debug(f"Validating output against schema: {schema_name}")
        self.validate(data, schema_name, raise_on_error=True)


# Global validator instance
_default_validator = ContractValidator()


def validate_contract(
    input_schema: Optional[str] = None,
    output_schema: Optional[str] = None
):
    """
    Decorator to validate function inputs and outputs against schemas.

    Args:
        input_schema: Name of JSON schema for input validation
        output_schema: Name of JSON schema for output validation

    Returns:
        Decorated function with contract validation

    Example:
        @validate_contract(input_schema="adapter_input", output_schema="adapter_result")
        def execute(self, step, context):
            # Function implementation
            return result
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Validate inputs if schema provided
            if input_schema:
                # For methods, args[0] is self, args[1] is first param
                # For functions, args[0] is first param
                input_data = args[1] if len(args) > 1 else kwargs.get('step')
                if input_data is not None:
                    try:
                        _default_validator.validate_input(input_data, input_schema)
                        logger.debug(f"Input validation passed for {func.__name__}")
                    except ValidationError as e:
                        logger.error(f"Input validation failed for {func.__name__}: {e}")
                        raise

            # Execute function
            result = func(*args, **kwargs)

            # Validate outputs if schema provided
            if output_schema:
                try:
                    # Support both AdapterResult objects and dicts
                    output_data = result.to_dict() if hasattr(result, 'to_dict') else result
                    _default_validator.validate_output(output_data, output_schema)
                    logger.debug(f"Output validation passed for {func.__name__}")
                except ValidationError as e:
                    logger.error(f"Output validation failed for {func.__name__}: {e}")
                    raise

            return result

        return wrapper

    return decorator


# Convenience function for direct validation
def validate_data(data: Any, schema_name: str) -> bool:
    """
    Validate data against a schema.

    Args:
        data: Data to validate
        schema_name: Schema file name

    Returns:
        True if valid, False otherwise
    """
    is_valid, _ = _default_validator.validate(data, schema_name, raise_on_error=False)
    return is_valid
