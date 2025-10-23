#!/usr/bin/env python3
"""
Settings - Unified configuration from environment variables

Uses Pydantic Settings for type-safe configuration loading from multiple sources.
Part of Phase 3 configuration consolidation.
"""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OrchestratorSettings(BaseSettings):
    """
    Unified orchestrator configuration.

    Loads configuration from:
    1. Environment variables
    2. .env file (if present)
    3. Default values (defined here)

    All settings can be overridden via environment variables with the same name (case-insensitive).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra environment variables
    )

    # ========================================================================
    # GitHub Integration
    # ========================================================================

    github_token: Optional[str] = Field(
        default=None,
        description="GitHub Personal Access Token for API access",
    )

    github_api_base: str = Field(
        default="https://api.github.com",
        description="GitHub API base URL",
    )

    # ========================================================================
    # AI API Keys
    # ========================================================================

    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key for Claude models",
    )

    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key for GPT models",
    )

    google_api_key: Optional[str] = Field(
        default=None,
        description="Google API key for Gemini models",
    )

    # ========================================================================
    # Ollama Configuration (Local AI)
    # ========================================================================

    ollama_api_base: str = Field(
        default="http://localhost:11434",
        description="Ollama API base URL for local DeepSeek inference",
    )

    ollama_model: str = Field(
        default="deepseek-coder-v2:lite",
        description="Default Ollama model to use",
    )

    # ========================================================================
    # Workflow Settings
    # ========================================================================

    max_token_budget: int = Field(
        default=500000,
        description="Maximum token budget for AI operations",
        ge=0,  # Greater than or equal to 0
    )

    default_workflow_timeout: int = Field(
        default=30,
        description="Default workflow timeout in minutes",
        ge=1,
    )

    prefer_deterministic: bool = Field(
        default=True,
        description="Prefer deterministic tools over AI when possible",
    )

    # ========================================================================
    # Directories
    # ========================================================================

    workflow_dir: Path = Field(
        default=Path(".ai/workflows"),
        description="Directory containing workflow YAML files",
    )

    artifacts_dir: Path = Field(
        default=Path("artifacts"),
        description="Directory for workflow artifacts",
    )

    logs_dir: Path = Field(
        default=Path("logs"),
        description="Directory for execution logs",
    )

    cost_dir: Path = Field(
        default=Path("cost"),
        description="Directory for cost tracking data",
    )

    state_dir: Path = Field(
        default=Path("state"),
        description="Directory for workflow state",
    )

    schemas_dir: Path = Field(
        default=Path(".ai/schemas"),
        description="Directory for JSON schemas",
    )

    # ========================================================================
    # Environment & Debugging
    # ========================================================================

    cli_orchestrator_env: str = Field(
        default="development",
        description="Environment mode (development, production, testing)",
    )

    debug: bool = Field(
        default=False,
        description="Enable debug logging",
    )

    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    # ========================================================================
    # Execution Settings
    # ========================================================================

    dry_run: bool = Field(
        default=False,
        description="Global dry-run mode (no changes made)",
    )

    fail_fast: bool = Field(
        default=True,
        description="Stop workflow execution on first failure",
    )

    parallel_execution: bool = Field(
        default=False,
        description="Enable parallel step execution (experimental)",
    )

    max_parallel_steps: int = Field(
        default=3,
        description="Maximum number of parallel steps",
        ge=1,
    )

    # ========================================================================
    # Adapter Settings
    # ========================================================================

    default_ai_adapter: str = Field(
        default="ai_editor",
        description="Default AI adapter to use (ai_editor, deepseek)",
    )

    enable_deepseek: bool = Field(
        default=True,
        description="Enable DeepSeek local AI integration",
    )

    # ========================================================================
    # Git Settings
    # ========================================================================

    git_auto_commit: bool = Field(
        default=False,
        description="Automatically commit changes after workflow execution",
    )

    git_commit_sign: bool = Field(
        default=True,
        description="Sign git commits",
    )

    default_git_lane: str = Field(
        default="lane/ai-coding/auto",
        description="Default git workflow lane",
    )

    # ========================================================================
    # Cost Tracking Settings
    # ========================================================================

    enable_cost_tracking: bool = Field(
        default=True,
        description="Enable cost tracking for AI operations",
    )

    cost_alert_threshold: float = Field(
        default=0.90,
        description="Alert when budget usage exceeds this threshold (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )

    # ========================================================================
    # Performance Settings
    # ========================================================================

    cache_enabled: bool = Field(
        default=True,
        description="Enable caching for adapter results",
    )

    cache_ttl: int = Field(
        default=3600,
        description="Cache time-to-live in seconds",
        ge=0,
    )

    # ========================================================================
    # Validation & Quality Gates
    # ========================================================================

    enable_gates: bool = Field(
        default=True,
        description="Enable verification gates",
    )

    strict_schema_validation: bool = Field(
        default=True,
        description="Enforce strict JSON schema validation",
    )

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def ensure_directories(self) -> None:
        """Create required directories if they don't exist."""
        for dir_field in ["workflow_dir", "artifacts_dir", "logs_dir", "cost_dir", "state_dir", "schemas_dir"]:
            dir_path: Path = getattr(self, dir_field)
            dir_path.mkdir(parents=True, exist_ok=True)

    def validate_configuration(self) -> dict[str, list[str]]:
        """
        Validate configuration and return issues.

        Returns:
            Dictionary with 'errors' and 'warnings' lists
        """
        errors = []
        warnings = []

        # Check for at least one AI API key
        if not any([self.anthropic_api_key, self.openai_api_key, self.google_api_key, self.enable_deepseek]):
            warnings.append("No AI API keys configured and DeepSeek is disabled")

        # Validate directories exist
        for dir_field in ["workflow_dir", "schemas_dir"]:
            dir_path: Path = getattr(self, dir_field)
            if not dir_path.exists():
                warnings.append(f"{dir_field} does not exist: {dir_path}")

        # Validate token budget
        if self.max_token_budget < 10000:
            warnings.append(f"Token budget is very low: {self.max_token_budget}")

        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            errors.append(f"Invalid log level: {self.log_level}. Must be one of {valid_log_levels}")

        return {"errors": errors, "warnings": warnings}

    def get_api_key_status(self) -> dict[str, bool]:
        """Get status of all API keys."""
        return {
            "github": self.github_token is not None,
            "anthropic": self.anthropic_api_key is not None,
            "openai": self.openai_api_key is not None,
            "google": self.google_api_key is not None,
            "ollama": self.enable_deepseek,
        }


# Singleton instance
_settings: Optional[OrchestratorSettings] = None


def get_settings(reload: bool = False) -> OrchestratorSettings:
    """
    Get or create settings singleton.

    Args:
        reload: If True, reload settings from environment

    Returns:
        OrchestratorSettings instance
    """
    global _settings

    if _settings is None or reload:
        _settings = OrchestratorSettings()

    return _settings


def validate_settings() -> tuple[bool, dict[str, list[str]]]:
    """
    Validate current settings.

    Returns:
        Tuple of (is_valid, issues_dict)
    """
    settings = get_settings()
    issues = settings.validate_configuration()

    is_valid = len(issues["errors"]) == 0

    return is_valid, issues
