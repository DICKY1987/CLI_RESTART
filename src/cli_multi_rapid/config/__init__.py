"""
Configuration management for CLI Orchestrator.

Unified configuration system using Pydantic Settings.
Part of Phase 3 configuration consolidation.
"""

# Phase 3 unified configuration
from .settings import (
    OrchestratorSettings,
    get_settings,
    validate_settings,
)

from .defaults import (
    VERSION,
    DEFAULT_DIRECTORIES,
    AI_MODELS,
    BUDGET_TIERS,
    get_default_for_environment,
    get_model_config,
    estimate_cost,
)

from .validator import (
    ConfigurationValidator,
    ValidationResult,
    validate_config,
    validate_and_print,
    quick_validate,
)

# Legacy configuration (maintained for backward compatibility)
from .github_config import GitHubConfig, get_github_config, validate_github_setup

__all__ = [
    # Settings
    "OrchestratorSettings",
    "get_settings",
    "validate_settings",
    # Defaults
    "VERSION",
    "DEFAULT_DIRECTORIES",
    "AI_MODELS",
    "BUDGET_TIERS",
    "get_default_for_environment",
    "get_model_config",
    "estimate_cost",
    # Validation
    "ConfigurationValidator",
    "ValidationResult",
    "validate_config",
    "validate_and_print",
    "quick_validate",
    # Legacy
    "GitHubConfig",
    "validate_github_setup",
    "get_github_config",
]
