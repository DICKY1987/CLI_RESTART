# Merge Audit Logs

This directory contains structured audit logs for all merge-train operations.

## Overview

The CLI Orchestrator's deterministic merge system generates machine-readable audit logs in **JSONL** (JSON Lines) format for:
- Automated merges from `workstream/**` branches
- Rollback operations
- Quarantine routing decisions
- Verification gate results

## Directory Structure

```
.runs/
├── audit/
│   ├── schema.json              # JSON Schema for audit records
│   ├── README.md                # This file
│   ├── merge-YYYYMMDD-HHMMSS.jsonl    # Merge operation logs
│   ├── rollback-YYYYMMDD-HHMMSS.jsonl # Rollback operation logs
│   └── ...
└── artifacts/
    ├── diff-YYYYMMDD-HHMMSS.patch    # Git diffs
    ├── policy-eval-*.log              # Policy evaluation logs
    └── ...
```

## File Format

### JSONL (JSON Lines)
Each line in a `.jsonl` file is a complete, valid JSON object representing a single event:

```jsonl
{"timestamp":"2025-10-23T10:30:00Z","run_id":"12345","branch_source":"workstream/ai-refactor/20251023-103000","branch_target":"main","policy_version":"2.0.0","strategies_applied":["merge-drivers","rerere"],"conflicts_found":0,"verification_gates":{"pre_commit":"pass","integration_tests":"pass"},"outcome":"merged"}
{"timestamp":"2025-10-23T11:00:00Z","run_id":"12346","branch_source":"workstream/security-fix/20251023-110000","branch_target":"main","policy_version":"2.0.0","conflicts_found":5,"outcome":"quarantined","quarantine_reason":"Conflict count exceeds safety limit"}
```

### Record Schema

See `schema.json` for the complete JSON Schema definition.

**Required Fields:**
- `timestamp` (ISO 8601): When the operation started
- `run_id` (string): Unique identifier (GitHub run ID or local timestamp)
- `branch_source` (string): Source branch being merged
- `branch_target` (string): Target branch (typically `main`)
- `policy_version` (string): Version of `.merge-policy.yaml` used
- `outcome` (enum): `merged`, `quarantined`, `failed`, or `rolled_back`

**Optional Fields:**
- `strategies_applied` (array): Merge strategies used
- `fallbacks_used` (array): Fallback strategies when primary failed
- `conflicts_found` (integer): Number of conflicts
- `verification_gates` (object): Results of pre-commit, tests, security scans
- `quarantine_reason` (string): Why the merge was quarantined
- `artifacts` (array): Paths to related files
- `errors` (array): Errors encountered

## Usage

### Querying Logs

**Count merges by outcome:**
```bash
jq -s 'group_by(.outcome) | map({outcome: .[0].outcome, count: length})' .runs/audit/*.jsonl
```

**Find all quarantined merges:**
```bash
jq 'select(.outcome == "quarantined")' .runs/audit/*.jsonl
```

**List merges with conflicts:**
```bash
jq 'select(.conflicts_found > 0)' .runs/audit/*.jsonl
```

**Analyze verification gate failures:**
```bash
jq 'select(.verification_gates.pre_commit == "fail")' .runs/audit/*.jsonl
```

**Get average conflicts per merge:**
```bash
jq -s '[.[].conflicts_found] | add / length' .runs/audit/*.jsonl
```

### Monitoring

**Watch for quarantines:**
```bash
tail -f .runs/audit/*.jsonl | jq 'select(.outcome == "quarantined")'
```

**Check recent merge success rate:**
```bash
jq -s 'group_by(.outcome) | map({outcome: .[0].outcome, count: length})' \
  .runs/audit/merge-$(date +%Y%m%d)*.jsonl
```

### Policy Analysis

**Find most common fallback strategies:**
```bash
jq -s '[.[].fallbacks_used[].strategy] | group_by(.) | map({strategy: .[0], count: length}) | sort_by(.count) | reverse' \
  .runs/audit/*.jsonl
```

**Identify files that frequently conflict:**
```bash
jq -s '[.[].conflict_files[]] | group_by(.) | map({file: .[0], count: length}) | sort_by(.count) | reverse | .[0:10]' \
  .runs/audit/*.jsonl
```

## Integration

### CI/CD (GitHub Actions)

The merge-train workflow (`.github/workflows/merge-train.yml`) automatically:
1. Generates audit records during merge operations
2. Writes to `.git/merge-audit.jsonl` (temporary, for CI upload)
3. Writes to `.runs/audit/merge-<timestamp>.jsonl` (permanent, in repo)
4. Uploads `.git/merge-audit.jsonl` as workflow artifact

### Local Development

Scripts that generate audit logs:
- `scripts/AutoMerge-Workstream.ps1` - Main merge automation
- `scripts/Rollback.ps1` - Rollback operations
- `scripts/PreFlight-Check.ps1` - Pre-flight analysis (optional)

## Retention

- **Repo audit logs** (`.runs/audit/*.jsonl`): Committed to Git, permanent history
- **CI artifacts** (uploaded via GitHub Actions): 90-day retention
- **Temporary logs** (`.git/merge-audit.jsonl`, `.git/merge-fallback.log`): Not committed, overwritten per run

## Security

Audit logs may contain:
- ✅ Branch names, commit SHAs, timestamps
- ✅ Policy versions, strategies used
- ✅ Verification gate results
- ✅ Error messages

Audit logs **do not** contain:
- ❌ Secrets or API keys
- ❌ File contents or code diffs
- ❌ PII (personally identifiable information)

If sensitive information appears in audit logs, **DO NOT commit them**. Add to `.gitignore` and investigate the source.

## Schema Validation

Validate audit logs against the schema:

```bash
# Using Python
python -c "
import json, jsonschema
schema = json.load(open('.runs/audit/schema.json'))
for line in open('.runs/audit/merge-20251023-103000.jsonl'):
    record = json.loads(line)
    jsonschema.validate(record, schema)
    print(f'✅ {record[\"run_id\"]} valid')
"
```

```bash
# Using Node.js with AJV
npm install -g ajv-cli
cat .runs/audit/*.jsonl | ajv validate -s .runs/audit/schema.json -d @
```

## Contributing

When adding new fields to audit records:
1. Update `schema.json` with the new field definition
2. Update this README with usage examples
3. Ensure scripts write the new field
4. Test schema validation with sample data

## Troubleshooting

**Q: No audit logs being generated?**
- Ensure `.runs/audit/` directory exists
- Check script permissions (PowerShell execution policy)
- Verify `AutoMerge-Workstream.ps1` is being called

**Q: Invalid JSON errors?**
- Each line must be a complete JSON object
- No trailing commas
- Validate with `jq .` or `python -m json.tool`

**Q: How to reset audit history?**
- Audit logs are in Git - use `git rm .runs/audit/*.jsonl` to remove
- Consider archiving instead of deleting for compliance

## References

- [JSON Lines format](http://jsonlines.org/)
- [JSON Schema specification](https://json-schema.org/)
- [Merge Policy Documentation](../../.merge-policy.yaml)
- [Merge Train Workflow](../../.github/workflows/merge-train.yml)
