from __future__ import annotations

"""
Environment-aware configuration loader.

Merges base config with environment overrides (dev/staging/prod) and expands
environment variables. No secrets are stored in YAML; secrets must come from
environment variables.
"""

import os
from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path("config")
BASE_FILE = CONFIG_DIR / "base.yaml"


class UnknownEnvironmentError(ValueError):
    pass


def _deep_merge(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge dict b into dict a and return a new dict."""
    result: dict[str, Any] = dict(a)
    for k, v in b.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def _expand_env(value: Any) -> Any:
    if isinstance(value, str):
        # Support ${VAR} interpolation
        return os.path.expandvars(value)
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    return value


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data


def resolve_environment(explicit_env: str | None = None) -> str:
    """Resolve environment from explicit arg or environment variables.

    Precedence: explicit > CLI_ENV > CLI_ORCHESTRATOR_ENV > ENVIRONMENT.
    """
    env = (
        explicit_env
        or os.getenv("CLI_ENV")
        or os.getenv("CLI_ORCHESTRATOR_ENV")
        or os.getenv("ENVIRONMENT")
        or "dev"
    )
    env = env.lower().strip()
    if env in {"development", "dev"}:
        return "dev"
    if env in {"staging", "stage", "preprod"}:
        return "staging"
    if env in {"production", "prod"}:
        return "prod"
    if env in {"test", "testing"}:
        # use dev defaults for local tests
        return "dev"
    raise UnknownEnvironmentError(f"Unknown environment: {env}")


def load_config(explicit_env: str | None = None) -> dict[str, Any]:
    """Load merged configuration for the given environment.

    - Loads base.yaml
    - Loads <env>.yaml and merges over base
    - Expands ${VAR} using process environment
    """
    env = resolve_environment(explicit_env)
    base = _load_yaml(BASE_FILE)
    env_file = CONFIG_DIR / f"{env}.yaml"
    overrides = _load_yaml(env_file)
    merged = _deep_merge(base, overrides)
    return _expand_env(merged)


__all__ = [
    "UnknownEnvironmentError",
    "resolve_environment",
    "load_config",
]

