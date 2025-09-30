---
name: /plan-mods
description: Analyze repo and emit plan.yaml following .det-tools/schemas/plan.schema.json
model: opus
tools: [fs, shell]
confirm: true
outputs:
  - .det-tools/out/analysis_report.json
  - plan.yaml
---
Analyze the codebase and write a machine-readable plan.yaml that follows .det-tools/schemas/plan.schema.json.

