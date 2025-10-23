#!/usr/bin/env python3
"""
Configuration Defaults - Default values and constants

Provides centralized default values for all configuration options.
Part of Phase 3 configuration consolidation.
"""

from pathlib import Path

# ============================================================================
# Version Information
# ============================================================================

VERSION = "1.0.0"
VERSION_CODENAME = "Phase 3 Refactored"

# ============================================================================
# API Endpoints
# ============================================================================

GITHUB_API_BASE = "https://api.github.com"
OLLAMA_API_BASE = "http://localhost:11434"

# ============================================================================
# Default Models
# ============================================================================

DEFAULT_OLLAMA_MODEL = "deepseek-coder-v2:lite"
DEFAULT_AI_ADAPTER = "ai_editor"

# AI Model configurations
AI_MODELS = {
    "claude-sonnet-4": {
        "provider": "anthropic",
        "cost_per_1k_tokens": 0.015,
        "max_tokens": 200000,
        "supports_vision": True,
    },
    "claude-opus-4": {
        "provider": "anthropic",
        "cost_per_1k_tokens": 0.075,
        "max_tokens": 200000,
        "supports_vision": True,
    },
    "gpt-4-turbo": {
        "provider": "openai",
        "cost_per_1k_tokens": 0.01,
        "max_tokens": 128000,
        "supports_vision": True,
    },
    "gemini-pro": {
        "provider": "google",
        "cost_per_1k_tokens": 0.00025,
        "max_tokens": 30720,
        "supports_vision": False,
    },
    "deepseek-coder-v2": {
        "provider": "ollama",
        "cost_per_1k_tokens": 0.0,  # Local, no cost
        "max_tokens": 16000,
        "supports_vision": False,
    },
}

# ============================================================================
# Token Budgets
# ============================================================================

MAX_TOKEN_BUDGET = 500000
DEFAULT_TOKEN_BUDGET_WARNING = 0.75  # 75% usage
DEFAULT_TOKEN_BUDGET_CRITICAL = 0.90  # 90% usage

# Budget tiers (for different environments)
BUDGET_TIERS = {
    "development": 100000,
    "testing": 50000,
    "production": 500000,
    "unlimited": 999999999,
}

# ============================================================================
# Timeout Settings
# ============================================================================

DEFAULT_WORKFLOW_TIMEOUT = 30  # minutes
DEFAULT_STEP_TIMEOUT = 10  # minutes
DEFAULT_ADAPTER_TIMEOUT = 5  # minutes
DEFAULT_API_TIMEOUT = 30  # seconds

# ============================================================================
# Directory Structure
# ============================================================================

DEFAULT_DIRECTORIES = {
    "workflow_dir": Path(".ai/workflows"),
    "artifacts_dir": Path("artifacts"),
    "logs_dir": Path("logs"),
    "cost_dir": Path("cost"),
    "state_dir": Path("state"),
    "schemas_dir": Path(".ai/schemas"),
    "bundles_dir": Path(".ai/bundles"),
    "prompts_dir": Path(".ai/prompts"),
}

# ============================================================================
# Logging Configuration
# ============================================================================

LOG_LEVEL_DEFAULT = "INFO"
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

LOG_FORMAT_DEFAULT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FORMAT_DETAILED = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"

# ============================================================================
# Git Configuration
# ============================================================================

DEFAULT_GIT_LANE = "lane/ai-coding/auto"
GIT_COMMIT_FOOTER = """
🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
"""

# Git lane patterns
GIT_LANES = {
    "ai-coding-fix": "lane/ai-coding/fix-*",
    "ai-coding-feature": "lane/ai-coding/feature-*",
    "ai-coding-refactor": "lane/ai-coding/refactor-*",
    "quality-quick-fix": "lane/quality/quick-fix",
    "quality-comprehensive": "lane/quality/comprehensive",
}

# ============================================================================
# Execution Settings
# ============================================================================

MAX_PARALLEL_STEPS = 3
ENABLE_PARALLEL_EXECUTION = False  # Experimental

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
RETRY_BACKOFF = 2  # exponential backoff multiplier

# ============================================================================
# Adapter Settings
# ============================================================================

# Adapter complexity thresholds (0.0-1.0)
ADAPTER_COMPLEXITY_THRESHOLDS = {
    "code_fixers": 0.3,
    "vscode_diagnostics": 0.4,
    "pytest_runner": 0.5,
    "ai_editor": 0.9,
    "ai_analyst": 0.95,
    "deepseek": 0.85,
}

# Adapter file size limits (bytes)
ADAPTER_FILE_SIZE_LIMITS = {
    "code_fixers": 1_000_000,  # 1MB
    "vscode_diagnostics": 5_000_000,  # 5MB
    "pytest_runner": 10_000_000,  # 10MB
    "ai_editor": 100_000,  # 100KB per file for AI
}

# ============================================================================
# Cache Settings
# ============================================================================

CACHE_ENABLED = True
CACHE_TTL = 3600  # 1 hour in seconds
CACHE_MAX_SIZE = 1000  # Maximum number of cached entries

# ============================================================================
# Verification Gate Settings
# ============================================================================

ENABLE_GATES = True
STRICT_SCHEMA_VALIDATION = True

# Default gate thresholds
GATE_THRESHOLDS = {
    "diff_max_files": 100,
    "diff_max_lines": 1000,
    "test_min_coverage": 85,
    "complexity_max": 10,
}

# ============================================================================
# Workflow Policy Defaults
# ============================================================================

WORKFLOW_POLICY_DEFAULTS = {
    "max_tokens": MAX_TOKEN_BUDGET,
    "prefer_deterministic": True,
    "fail_fast": True,
    "enable_gates": True,
    "cost_limit_usd": 10.0,
}

# ============================================================================
# File Patterns
# ============================================================================

# Python file patterns
PYTHON_FILE_PATTERNS = [
    "**/*.py",
    "**/*.pyi",
]

# JavaScript/TypeScript file patterns
JS_TS_FILE_PATTERNS = [
    "**/*.js",
    "**/*.jsx",
    "**/*.ts",
    "**/*.tsx",
    "**/*.mjs",
    "**/*.cjs",
]

# Configuration file patterns
CONFIG_FILE_PATTERNS = [
    "**/*.yaml",
    "**/*.yml",
    "**/*.json",
    "**/*.toml",
    "**/*.ini",
    "**/*.cfg",
]

# Excluded patterns (for file searches)
EXCLUDED_PATTERNS = [
    "**/node_modules/**",
    "**/.git/**",
    "**/.venv/**",
    "**/venv/**",
    "**/__pycache__/**",
    "**/*.pyc",
    "**/.pytest_cache/**",
    "**/build/**",
    "**/dist/**",
]

# ============================================================================
# Schema Validation
# ============================================================================

# JSON Schema file mappings (artifact -> schema)
SCHEMA_MAPPINGS = {
    "diagnostics.json": "diagnostics.schema.json",
    "test_report.json": "test_report.schema.json",
    "cost_report.json": "cost_report.schema.json",
    "workflow_result.json": "workflow_result.schema.json",
}

# ============================================================================
# Environment Detection
# ============================================================================

ENVIRONMENT_INDICATORS = {
    "development": ["dev", "develop", "local"],
    "testing": ["test", "ci", "qa"],
    "production": ["prod", "production", "live"],
}

# ============================================================================
# Cost Tracking
# ============================================================================

COST_TRACKING_ENABLED = True
COST_ALERT_THRESHOLD = 0.90  # 90% of budget
COST_LOG_FORMAT = "jsonl"  # JSON Lines format

# ============================================================================
# Help & Documentation
# ============================================================================

DOCUMENTATION_URL = "https://github.com/DICKY1987/CLI_RESTART"
ISSUES_URL = "https://github.com/DICKY1987/CLI_RESTART/issues"
CLAUDE_CODE_URL = "https://claude.com/claude-code"

# ============================================================================
# Helper Functions
# ============================================================================


def get_default_for_environment(env: str) -> dict:
    """
    Get default configuration values for a specific environment.

    Args:
        env: Environment name (development, testing, production)

    Returns:
        Dictionary of configuration values
    """
    base_config = {
        "max_token_budget": BUDGET_TIERS.get(env.lower(), MAX_TOKEN_BUDGET),
        "log_level": "DEBUG" if env.lower() == "development" else "INFO",
        "debug": env.lower() == "development",
        "enable_gates": True,
        "strict_schema_validation": env.lower() in ["production", "testing"],
    }

    return base_config


def get_model_config(model_name: str) -> dict:
    """
    Get configuration for a specific AI model.

    Args:
        model_name: Name of the AI model

    Returns:
        Dictionary with model configuration
    """
    return AI_MODELS.get(model_name, {})


def estimate_cost(tokens: int, model_name: str = "claude-sonnet-4") -> float:
    """
    Estimate cost for a given number of tokens.

    Args:
        tokens: Number of tokens
        model_name: AI model name

    Returns:
        Estimated cost in USD
    """
    model_config = get_model_config(model_name)
    cost_per_1k = model_config.get("cost_per_1k_tokens", 0.015)

    return (tokens / 1000) * cost_per_1k
