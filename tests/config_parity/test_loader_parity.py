from __future__ import annotations

import json
from pathlib import Path

import pytest

from cli_multi_rapid.config.loader import (
    UnknownEnvironmentError,
    load_config,
    resolve_environment,
)

HERE = Path(__file__).parent
GOLDEN = HERE / "golden"


def test_resolve_environment_aliases():
    assert resolve_environment("development") == "dev"
    assert resolve_environment("dev") == "dev"
    assert resolve_environment("staging") == "staging"
    assert resolve_environment("preprod") == "staging"
    assert resolve_environment("prod") == "prod"
    assert resolve_environment("production") == "prod"
    assert resolve_environment("testing") == "dev"
    with pytest.raises(UnknownEnvironmentError):
        resolve_environment("weird")


@pytest.mark.parametrize(
    "env_name, golden_name",
    [
        ("dev", "dev.json"),
        ("staging", "staging.json"),
        ("prod", "prod.json"),
    ],
)
def test_config_merge_matches_golden_snapshots(env_name: str, golden_name: str, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("REDIS_URL", "redis://test:6379/0")
    cfg = load_config(env_name)
    golden_path = GOLDEN / golden_name
    got = json.loads(json.dumps(cfg))
    want = json.loads(golden_path.read_text(encoding="utf-8"))
    assert got == want


def test_legacy_profiles_path_shim(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    repo_root = Path.cwd()
    config_dir = repo_root / "config"
    profiles_dir = config_dir / "profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)
    legacy_file = profiles_dir / "dev.yaml"
    legacy_file.write_text("app:\n  log_level: DEBUG\n", encoding="utf-8")
    primary = config_dir / "dev.yaml"
    backup = None
    if primary.exists():
        backup = tmp_path / "dev.yaml.bak"
        primary.replace(backup)
    try:
        monkeypatch.setenv("CONFIG_LEGACY_PATHS", "1")
        cfg = load_config("dev")
        assert cfg.get("app", {}).get("log_level") == "DEBUG"
    finally:
        if backup and backup.exists():
            backup.replace(primary)
        legacy_file.unlink(missing_ok=True)

