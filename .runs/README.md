Append-only ledgers for operational events

Structure
- audit/: Existing merge/audit records (schema in audit/schema.json)
- artifacts/: CI artifacts staging directory
- changes.jsonl: Append-only deployment/change events (one JSON object per line)
- secrets.jsonl: Append-only secret rotation/break-glass events (one JSON object per line)

Guidelines
- Do not rewrite history; only append new lines.
- Ensure entries contain an ISO-8601 timestamp and an owner.
- Keep sensitive values redacted; reference secret IDs rather than raw values.

Example (JSONL)
{"timestamp":"2025-10-24T12:00:00Z","event":"deploy","service":"cli-orchestrator","version":"1.2.3","owner":"@platform-team"}
{"timestamp":"2025-10-24T12:05:00Z","event":"secret_rotation","secret_id":"kv://prod/cli/api-key","owner":"@secops-team"}

