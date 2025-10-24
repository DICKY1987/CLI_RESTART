Configuration Layout and Precedence

- Canonical tree
  - config/base.yaml
  - config/dev.yaml, config/staging.yaml, config/prod.yaml
  - config/policies/
    - compliance_rules.json
    - slo-policy.yaml, secrets-policy.yaml
    - flags.yaml (migrated from flags/registry.yaml)

- Precedence (highest wins)
  - Policy overlays in `config/policies/` (when applicable)
  - Environment file `config/<env>.yaml`
  - Base defaults `config/base.yaml`

- Environment resolution
  - Explicit parameter > `CLI_ENV` > `CLI_ORCHESTRATOR_ENV` > `ENVIRONMENT` > dev

- Legacy paths (temporary compatibility)
  - Previous locations `policies/`, `config/policy/`, and `flags/` are deprecated.
  - Code should prefer `config/policies/`.
  - A short-term shim checks both locations where relevant until full migration.

- Developer notes
  - Do not store secrets in YAML. Use environment variables and `.env.example`.
  - Keep policy files self-contained; avoid cross-file includes.

