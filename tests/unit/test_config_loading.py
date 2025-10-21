import os
from pathlib import Path

import pytest

from cli_multi_rapid.config.loader import (
    UnknownEnvironmentError,
    load_config,
    resolve_environment,
)


def test_resolve_environment_aliases():
    assert resolve_environment("development") == "dev"
    assert resolve_environment("prod") == "prod"
    assert resolve_environment("staging") == "staging"


def test_resolve_environment_from_env(monkeypatch):
    monkeypatch.setenv("CLI_ENV", "staging")
    assert resolve_environment() == "staging"


def test_unknown_environment():
    with pytest.raises(UnknownEnvironmentError):
        resolve_environment("weird")


def test_load_config_merges(tmp_path, monkeypatch):
    # Use repo config files; ensure env variables are expanded
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    cfg = load_config("dev")
    assert cfg["app"]["debug"] is True
    assert cfg["workflow"]["max_concurrent"] == 2
    assert cfg["redis"]["url"].startswith("redis://")

