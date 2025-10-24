#!/usr/bin/env python3
"""
Configuration Validator - Validate configuration settings

Provides comprehensive validation for all configuration options.
Part of Phase 3 configuration consolidation.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from .defaults import (
    BUDGET_TIERS,
    LOG_LEVELS,
    MAX_TOKEN_BUDGET,
)
from .settings import OrchestratorSettings, get_settings


class ValidationResult:
    """Result of configuration validation."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

    @property
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)."""
        return len(self.errors) == 0

    @property
    def has_warnings(self) -> bool:
        """Check if there are warnings."""
        return len(self.warnings) > 0

    def add_error(self, message: str) -> None:
        """Add validation error."""
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        """Add validation warning."""
        self.warnings.append(message)

    def add_info(self, message: str) -> None:
        """Add informational message."""
        self.info.append(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
        }


class ConfigurationValidator:
    """
    Comprehensive configuration validator.

    Validates all configuration settings and provides detailed feedback.
    """

    def __init__(self, settings: Optional[OrchestratorSettings] = None):
        """
        Initialize validator.

        Args:
            settings: Settings to validate (uses global settings if None)
        """
        self.settings = settings or get_settings()
        self.result = ValidationResult()

    def validate_all(self) -> ValidationResult:
        """
        Run all validation checks.

        Returns:
            ValidationResult with all issues
        """
        self.validate_api_keys()
        self.validate_directories()
        self.validate_token_budget()
        self.validate_log_level()
        self.validate_timeouts()
        self.validate_git_settings()
        self.validate_cost_settings()
        self.validate_adapter_settings()
        self.validate_environment()

        return self.result

    def validate_api_keys(self) -> None:
        """Validate API key configuration."""
        has_anthropic = self.settings.anthropic_api_key is not None
        has_openai = self.settings.openai_api_key is not None
        has_google = self.settings.google_api_key is not None
        has_ollama = self.settings.enable_deepseek

        # Check if at least one AI provider is configured
        if not any([has_anthropic, has_openai, has_google, has_ollama]):
            self.result.add_error(
                "No AI providers configured. "
                "Set at least one API key or enable DeepSeek"
            )

        # Warn about missing GitHub token
        if not self.settings.github_token:
            self.result.add_warning(
                "GitHub token not set. Some features may not work. "
                "Set GITHUB_TOKEN environment variable"
            )

        # Info about configured providers
        providers = []
        if has_anthropic:
            providers.append("Anthropic (Claude)")
        if has_openai:
            providers.append("OpenAI (GPT)")
        if has_google:
            providers.append("Google (Gemini)")
        if has_ollama:
            providers.append("Ollama (DeepSeek - local)")

        if providers:
            self.result.add_info(f"Configured AI providers: {', '.join(providers)}")

    def validate_directories(self) -> None:
        """Validate directory configuration."""
        required_dirs = {
            "workflow_dir": "Workflow definitions",
            "schemas_dir": "JSON schemas",
        }

        optional_dirs = {
            "artifacts_dir": "Workflow artifacts",
            "logs_dir": "Execution logs",
            "cost_dir": "Cost tracking",
            "state_dir": "Workflow state",
        }

        # Check required directories
        for dir_field, description in required_dirs.items():
            dir_path: Path = getattr(self.settings, dir_field)

            if not dir_path.exists():
                self.result.add_error(
                    f"Required directory does not exist: {description} ({dir_path}). "
                    f"Create it or update {dir_field.upper()} environment variable"
                )

        # Warn about missing optional directories
        for dir_field, description in optional_dirs.items():
            dir_path: Path = getattr(self.settings, dir_field)

            if not dir_path.exists():
                self.result.add_warning(
                    f"Optional directory does not exist: {description} ({dir_path}). "
                    f"It will be created automatically when needed"
                )

    def validate_token_budget(self) -> None:
        """Validate token budget settings."""
        budget = self.settings.max_token_budget

        if budget < 1000:
            self.result.add_error(
                f"Token budget is too low: {budget}. "
                f"Must be at least 1,000 tokens"
            )
        elif budget < 10000:
            self.result.add_warning(
                f"Token budget is very low: {budget}. "
                f"Consider increasing to at least 10,000 for most workflows"
            )

        # Check against standard tiers
        env = self.settings.cli_orchestrator_env.lower()
        expected_budget = BUDGET_TIERS.get(env, MAX_TOKEN_BUDGET)

        if budget < expected_budget:
            self.result.add_warning(
                f"Token budget ({budget:,}) is lower than recommended "
                f"for {env} environment ({expected_budget:,})"
            )

        # Check cost alert threshold
        if not (0.0 <= self.settings.cost_alert_threshold <= 1.0):
            self.result.add_error(
                f"Cost alert threshold must be between 0.0 and 1.0, "
                f"got {self.settings.cost_alert_threshold}"
            )

    def validate_log_level(self) -> None:
        """Validate logging configuration."""
        log_level = self.settings.log_level.upper()

        if log_level not in LOG_LEVELS:
            self.result.add_error(
                f"Invalid log level: {log_level}. "
                f"Must be one of: {', '.join(LOG_LEVELS)}"
            )

        # Warn if debug mode in production
        if self.settings.debug and self.settings.cli_orchestrator_env.lower() == "production":
            self.result.add_warning(
                "Debug mode is enabled in production environment. "
                "This may expose sensitive information"
            )

    def validate_timeouts(self) -> None:
        """Validate timeout settings."""
        if self.settings.default_workflow_timeout < 1:
            self.result.add_error(
                f"Workflow timeout must be at least 1 minute, "
                f"got {self.settings.default_workflow_timeout}"
            )

        if self.settings.default_workflow_timeout > 120:
            self.result.add_warning(
                f"Workflow timeout is very high: {self.settings.default_workflow_timeout} minutes. "
                f"Long-running workflows may cause issues"
            )

    def validate_git_settings(self) -> None:
        """Validate git-related settings."""
        # Validate lane pattern
        lane = self.settings.default_git_lane

        if not lane.startswith("lane/"):
            self.result.add_warning(
                f"Default git lane '{lane}' does not follow standard pattern (lane/...)"
            )

        # Warn about auto-commit
        if self.settings.git_auto_commit:
            self.result.add_warning(
                "Git auto-commit is enabled. Changes will be automatically committed"
            )

    def validate_cost_settings(self) -> None:
        """Validate cost tracking settings."""
        if not self.settings.enable_cost_tracking:
            self.result.add_warning(
                "Cost tracking is disabled. "
                "Token usage will not be tracked"
            )

        # Validate cost directory
        if self.settings.enable_cost_tracking and not self.settings.cost_dir.exists():
            self.result.add_info(
                f"Cost directory will be created: {self.settings.cost_dir}"
            )

    def validate_adapter_settings(self) -> None:
        """Validate adapter configuration."""
        default_adapter = self.settings.default_ai_adapter

        valid_adapters = ["ai_editor", "ai_analyst", "deepseek"]

        if default_adapter not in valid_adapters:
            self.result.add_error(
                f"Invalid default AI adapter: {default_adapter}. "
                f"Must be one of: {', '.join(valid_adapters)}"
            )

        # Check if default adapter is available
        if default_adapter == "deepseek" and not self.settings.enable_deepseek:
            self.result.add_error(
                "Default AI adapter is 'deepseek' but DeepSeek is disabled. "
                "Enable DeepSeek or change default_ai_adapter"
            )

        # Validate parallel execution
        if self.settings.parallel_execution:
            self.result.add_warning(
                "Parallel execution is enabled (experimental feature)"
            )

            if self.settings.max_parallel_steps < 1:
                self.result.add_error(
                    f"Max parallel steps must be at least 1, "
                    f"got {self.settings.max_parallel_steps}"
                )

    def validate_environment(self) -> None:
        """Validate environment configuration."""
        env = self.settings.cli_orchestrator_env.lower()

        valid_envs = ["development", "testing", "production"]

        if env not in valid_envs:
            self.result.add_warning(
                f"Unrecognized environment: {env}. "
                f"Expected one of: {', '.join(valid_envs)}"
            )

        # Environment-specific checks
        if env == "production":
            if self.settings.dry_run:
                self.result.add_warning(
                    "Dry-run mode is enabled in production"
                )

            if not self.settings.strict_schema_validation:
                self.result.add_warning(
                    "Strict schema validation is disabled in production"
                )

    def get_summary(self) -> str:
        """
        Get validation summary as formatted string.

        Returns:
            Formatted summary string
        """
        lines = []
        lines.append("=== Configuration Validation Summary ===\n")

        if self.result.is_valid:
            lines.append("✓ Configuration is valid")
        else:
            lines.append("✗ Configuration has errors")

        if self.result.errors:
            lines.append(f"\nErrors ({len(self.result.errors)}):")
            for error in self.result.errors:
                lines.append(f"  - {error}")

        if self.result.warnings:
            lines.append(f"\nWarnings ({len(self.result.warnings)}):")
            for warning in self.result.warnings:
                lines.append(f"  - {warning}")

        if self.result.info:
            lines.append(f"\nInfo ({len(self.result.info)}):")
            for info in self.result.info:
                lines.append(f"  - {info}")

        return "\n".join(lines)


# Convenience functions

def validate_config(settings: Optional[OrchestratorSettings] = None) -> ValidationResult:
    """
    Validate configuration settings.

    Args:
        settings: Settings to validate (uses global settings if None)

    Returns:
        ValidationResult with all issues
    """
    validator = ConfigurationValidator(settings)
    return validator.validate_all()


def validate_and_print(settings: Optional[OrchestratorSettings] = None) -> bool:
    """
    Validate configuration and print summary.

    Args:
        settings: Settings to validate (uses global settings if None)

    Returns:
        True if valid, False otherwise
    """
    validator = ConfigurationValidator(settings)
    result = validator.validate_all()

    print(validator.get_summary())

    return result.is_valid


def quick_validate() -> bool:
    """
    Quick validation check (errors only).

    Returns:
        True if no errors, False otherwise
    """
    result = validate_config()
    return result.is_valid
