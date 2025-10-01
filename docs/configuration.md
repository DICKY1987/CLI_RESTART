Configuration and Operations Readiness

- Environments: dev, staging, prod. Base config at `config/base.yaml` with overrides in `config/<env>.yaml`.
- Selection: pass `--env` on CLI or set `CLI_ENV`/`CLI_ORCHESTRATOR_ENV`/`ENVIRONMENT`.
- Validation: Pydantic models validate config at startup. The CLI exits if invalid.
- Secrets: never stored in YAML. Provide via environment variables (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `REDIS_URL`).

Validate the env template

- Run `python scripts/validate_env.py --check .env.example` to ensure all Vars referenced in code are present in the template.

Local usage

- Copy `.env.example` to `.env` and set your local values.
- Run `python -m cli_multi_rapid.main --env dev --help` to verify startup validation.

