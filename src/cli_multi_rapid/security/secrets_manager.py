from __future__ import annotations

"""Secrets management interfaces and pluggable backends.

Backends:
- env (default): reads secrets from environment variables.
- vault/aws/azure: lightweight stubs with clear error messages if used without
  the corresponding SDKs configured. These can be swapped in without changing
  call sites via the `SecretsManager` facade.

This module intentionally avoids importing optional SDKs at import time to keep
the base runtime light and deterministic. Networked calls must be opt-in and
mocked in tests.
"""

import os
from dataclasses import dataclass
from typing import Any, Optional


class SecretNotFoundError(KeyError):
    pass


@dataclass
class SecretsConfig:
    backend: str = "env"  # env | vault | aws_secrets_manager | azure_key_vault
    prefix: Optional[str] = None
    vault_addr: Optional[str] = None
    vault_token_env: Optional[str] = None
    vault_mount: Optional[str] = None
    aws_region: Optional[str] = None
    aws_profile: Optional[str] = None
    azure_vault_name: Optional[str] = None


class BaseSecretsBackend:
    def get_secret(self, name: str) -> str:
        raise NotImplementedError


class EnvSecretsBackend(BaseSecretsBackend):
    def __init__(self, prefix: Optional[str] = None) -> None:
        self.prefix = (prefix or "").strip()

    def _key(self, name: str) -> str:
        key = name
        if self.prefix:
            normalized = name.replace(".", "_").replace("/", "_")
            key = f"{self.prefix}_{normalized}"
        return key.upper()

    def get_secret(self, name: str) -> str:
        key = self._key(name)
        val = os.getenv(key)
        if val is None:
            val = os.getenv(name)
        if val is None:
            raise SecretNotFoundError(f"Secret not found in environment: {key}")
        return val


class VaultSecretsBackend(BaseSecretsBackend):
    def __init__(self, addr: str, token: str, mount: Optional[str] = None):
        self.addr = addr
        self.token = token
        self.mount = mount or "secret"
        self._client: Any
        try:
            import hvac  # type: ignore

            self._client = hvac.Client(url=self.addr, token=self.token)
        except Exception as e:  # noqa: BLE001
            raise RuntimeError(
                "Vault backend requires 'hvac' and valid configuration"
            ) from e

    def get_secret(self, name: str) -> str:
        path = name.lstrip("/")
        read = self._client.secrets.kv.v2.read_secret_version(
            path=path, mount_point=self.mount
        )
        data = read.get("data", {}).get("data", {})
        if "value" in data and isinstance(data["value"], str):
            return data["value"]
        raise SecretNotFoundError(f"Secret not found or not a string: {name}")


class AWSSecretsManagerBackend(BaseSecretsBackend):
    def __init__(self, region: str, profile: Optional[str] = None) -> None:
        try:
            import boto3  # type: ignore

            if profile:
                import boto3.session as boto3_session  # type: ignore

                session = boto3_session.Session(profile_name=profile, region_name=region)
            else:
                session = boto3.session.Session(region_name=region)  # type: ignore[attr-defined]
            self._client = session.client("secretsmanager")
        except Exception as e:  # noqa: BLE001
            raise RuntimeError(
                "AWS backend requires 'boto3' and valid AWS credentials"
            ) from e

    def get_secret(self, name: str) -> str:
        resp = self._client.get_secret_value(SecretId=name)
        if "SecretString" in resp and isinstance(resp["SecretString"], str):
            return resp["SecretString"]
        raise SecretNotFoundError(f"Secret is binary or missing: {name}")


class AzureKeyVaultBackend(BaseSecretsBackend):
    def __init__(self, vault_name: str) -> None:
        try:
            from azure.identity import DefaultAzureCredential  # type: ignore
            from azure.keyvault.secrets import SecretClient  # type: ignore

            url = f"https://{vault_name}.vault.azure.net"
            cred = DefaultAzureCredential()
            self._client = SecretClient(vault_url=url, credential=cred)
        except Exception as e:  # noqa: BLE001
            raise RuntimeError(
                "Azure backend requires 'azure-identity' and 'azure-keyvault-secrets'"
            ) from e

    def get_secret(self, name: str) -> str:
        s = self._client.get_secret(name)
        if s and getattr(s, "value", None):
            return str(s.value)
        raise SecretNotFoundError(f"Secret not found: {name}")


class SecretsManager:
    def __init__(self, backend: BaseSecretsBackend) -> None:
        self._backend = backend

    def get_secret(self, name: str) -> str:
        return self._backend.get_secret(name)

    @classmethod
    def from_config(cls, cfg: dict[str, Any] | SecretsConfig | None) -> SecretsManager:
        if cfg is None:
            return cls(EnvSecretsBackend())
        if isinstance(cfg, SecretsConfig):
            sc = cfg
        else:
            sc = SecretsConfig(**cfg)  # type: ignore[arg-type]

        backend_name = (sc.backend or "env").lower()
        if backend_name == "env":
            backend = EnvSecretsBackend(prefix=sc.prefix)
        elif backend_name in {"vault", "hashicorp_vault"}:
            token = os.getenv(sc.vault_token_env or "VAULT_TOKEN")
            if not (sc.vault_addr and token):
                raise RuntimeError("Vault backend requires 'vault_addr' and token env")
            backend = VaultSecretsBackend(addr=sc.vault_addr, token=token, mount=sc.vault_mount)
        elif backend_name in {"aws_secrets_manager", "aws"}:
            if not sc.aws_region:
                raise RuntimeError("AWS backend requires 'aws_region'")
            backend = AWSSecretsManagerBackend(region=sc.aws_region, profile=sc.aws_profile)
        elif backend_name in {"azure_key_vault", "azure"}:
            if not sc.azure_vault_name:
                raise RuntimeError("Azure backend requires 'azure_vault_name'")
            backend = AzureKeyVaultBackend(vault_name=sc.azure_vault_name)
        else:
            raise ValueError(f"Unknown secrets backend: {sc.backend}")
        return cls(backend)
