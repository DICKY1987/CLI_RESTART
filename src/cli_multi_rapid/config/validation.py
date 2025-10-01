from __future__ import annotations

"""Configuration validation helpers."""

from typing import Optional, Tuple

from .loader import load_config, resolve_environment
from .models import Settings


class ConfigValidationError(Exception):
    pass


def validate_and_build_settings(explicit_env: Optional[str] = None) -> Tuple[str, Settings]:
    """Validate configuration and return (env, settings).

    Raises ConfigValidationError on invalid configuration.
    """
    env = resolve_environment(explicit_env)
    merged = load_config(env)
    try:
        settings = Settings.parse_obj(merged)
    except Exception as e:  # pydantic ValidationError
        raise ConfigValidationError(str(e))
    return env, settings

