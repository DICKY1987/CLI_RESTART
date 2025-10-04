Secrets Management
==================

Overview
--------
- Default backend: `env` reads secrets from environment variables.
- Optional backends (stubs): HashiCorp Vault, AWS Secrets Manager, Azure Key Vault.
- Switch backends without changing call sites via `SecretsManager`.

Config
------
- Schema: `config/secrets.schema.json`
- Example (env with prefix):

```
{
  "backend": "env",
  "prefix": "CLI_ORCH"
}
```

This will look up `CLI_ORCH_JWT_SECRET` for `get_secret("JWT_SECRET")`.

Python usage
------------
```
from cli_multi_rapid.security.secrets_manager import SecretsManager

cfg = {"backend": "env", "prefix": "CLI_ORCH"}
m = SecretsManager.from_config(cfg)
jwt = m.get_secret("JWT_SECRET")
```

Backends
--------
- `env`: No dependencies. Uppercases keys; applies optional `prefix_`.
- `vault`: Requires `hvac` and a `VAULT_TOKEN` (or `vault_token_env`) in the environment.
- `aws_secrets_manager`: Requires `boto3` and AWS credentials in the environment/profile.
- `azure_key_vault`: Requires `azure-identity` and `azure-keyvault-secrets`.

Notes
-----
- The non-env backends are implemented to import their SDKs lazily. If missing,
  a clear error is raised when the backend is instantiated.
- Networked calls should be mocked in tests. Prefer `env` in CI.
