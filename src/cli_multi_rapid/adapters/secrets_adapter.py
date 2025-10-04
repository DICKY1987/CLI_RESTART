from __future__ import annotations

from typing import Any

from cli_multi_rapid.security.secrets_manager import SecretsManager


class SecretsAdapter:
    def __init__(self, cfg: dict[str, Any] | None = None) -> None:
        self._mgr = SecretsManager.from_config(cfg)

    def get(self, name: str) -> str:
        return self._mgr.get_secret(name)


def from_config(cfg: dict[str, Any] | None) -> SecretsAdapter:
    return SecretsAdapter(cfg)
