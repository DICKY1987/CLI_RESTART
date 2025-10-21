import os

import pytest

from cli_multi_rapid.config.validation import (
    ConfigValidationError,
    validate_and_build_settings,
)


def test_validation_success(monkeypatch):
    # Provide env needed for expansion
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    env, settings = validate_and_build_settings("dev")
    assert env == "dev"
    assert settings.app.api_port == 8000
    assert settings.workflow.max_concurrent >= 1


def test_validation_failure_on_bad_value(tmp_path, monkeypatch):
    # Temporarily write an invalid override and point CONFIG_DIR to it
    from cli_multi_rapid.config import loader

    d = tmp_path / "config"
    d.mkdir()
    (d / "base.yaml").write_text("app:\n  api_port: -1\n")
    # monkeypatch the constants used by loader
    monkeypatch.setattr(loader, "CONFIG_DIR", d)
    monkeypatch.setattr(loader, "BASE_FILE", d / "base.yaml")

    with pytest.raises(ConfigValidationError):
        validate_and_build_settings("dev")


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("CLI_ENV", "prod")
    env, settings = validate_and_build_settings()
    assert env == "prod"

