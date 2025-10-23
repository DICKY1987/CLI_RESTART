# Deterministic Git System — Unified Guide (Single‑Source Replacement)

**Version:** 3.0  
**Maintainer:** You (repo owner)  
**Scope:** Replaces and consolidates the previous three documents into one authoritative source for your deterministic, safety‑gated Git workflow on Windows/PowerShell with AI‑assisted development.

---

## 0) How to Use This Document
- This file is the **single source of truth** for Git policy, safety gates, CI merge‑train, rollback, and audit mechanics.
- Keep it at: `docs/deterministic_git_unified_guide.md` (or root `DETERMINISTIC_GIT_GUIDE.md`).
- Edit using the **section IDs** (e.g., `[SEC‑3.2]`) and **index tags** (e.g., `[IDX: hooks]`) listed in §1.2. These let you jump directly to the right block in your editor.
- All **snippets** are production‑grade defaults. Adapt path names to your repo if they differ.

---

## 1) Indexes & Navigation

### 1.1 Table of Contents (ToC)
1. [Indexes & Navigation](#1-indexes--navigation)
2. [Principles & Goals](#2-principles--goals)
3. [Repository Layout & Roles](#3-repository-layout--roles)
4. [One‑Time Setup (Local & Repo)](#4-one-time-setup-local--repo)
5. [Daily Developer Workflow (Local)](#5-daily-developer-workflow-local)
6. [Policies & Merge Strategy](#6-policies--merge-strategy)
7. [CI/CD Merge‑Train Pipeline](#7-cicd-merge-train-pipeline)
8. [Safety Gates & Security](#8-safety-gates--security)
9. [Audit, Rerere & Learning Loop](#9-audit-rerere--learning-loop)
10. [Rollback & Quarantine](#10-rollback--quarantine)
11. [Windows/PowerShell Tooling](#11-windowspowershell-tooling)
12. [Reference: Config & Snippets](#12-reference-config--snippets)
13. [Editing Guide & Conventions](#13-editing-guide--conventions)
14. [FAQ & Troubleshooting](#14-faq--troubleshooting)
15. [Change Log](#15-change-log)

### 1.2 Editing Index (Jump Tags)
- **[IDX: hooks]** pre‑commit, pre‑push, lint, type, security, secrets (§8.2, §12.2)
- **[IDX: policy]** `.merge-policy.yaml`, path rules, lockfile rules, structural drivers (§6.2, §12.3)
- **[IDX: actions]** GitHub Actions merge‑train workflow (§7.3, §12.5)
- **[IDX: quarantine]** needs‑human routing, fenced paths, review gates (§7.2, §10.2)
- **[IDX: rerere]** enable/restore cache, human resolution reuse (§9.2)
- **[IDX: worktrees]** per‑tool worktrees (optional) (§11.4)
- **[IDX: safe‑ai‑session]** branch scoping wrapper (§5.1, §11.2, §12.6)
- **[IDX: git‑config]** deterministic merges (`zdiff3`), rebase, push defaults (§4.2, §12.1)
- **[IDX: rollback]** scripted revert, policy exception stamp (§10.1, §12.7)
- **[IDX: windows]** PowerShell, VS Code, scheduled jobs (§11)

---

## 2) Principles & Goals
**Determinism.** Given the same inputs and policies, merges produce the same outputs.  
**Safety.** Prevent dangerous changes from landing; quarantine risky diffs.  
**Observability.** Every action is auditable; logs are structured and searchable.  
**Automation.** Local hooks + CI merge‑train enforce behavior without heroics.  
**Learning.** Human decisions feed back into policy and `git rerere` for next time.

**Outcomes:** fewer regressions, repeatable CI merges, faster reviews, lower AI‑assist risk, clean history.

---

## 3) Repository Layout & Roles

```
repo/
├─ .gitattributes                      # File-type merge strategies (§12.4)
├─ .gitignore
├─ .editorconfig
├─ .pre-commit-config.yaml             # Hooks config (§12.2)
├─ .merge-policy.yaml                  # Merge strategy policy (§6.2)
├─ .merge-automation.yaml              # Merge-train orchestration knobs (§7)
├─ config/
│  └─ git_safety.yml                   # One-file safety profile (§8.1)
├─ scripts/                            # PowerShell automation (§11)
│  ├─ PreFlight.ps1
│  ├─ AutoMergeWorkstream.ps1
│  ├─ Rollback.ps1
│  ├─ Safe-AI-Session.ps1
│  └─ ToolsCheck.ps1
├─ .github/workflows/
│  └─ merge-train.yml                  # CI entrypoint (§12.5)
├─ .runs/                              # Audit JSONL & artifacts (§9.1)
└─ docs/
   └─ deterministic_git_unified_guide.md  # This file
```

**Branch roles:**
- `main` — protected, only CI merge‑train writes.
- `workstream/*` — developer/AI session work branches.
- `rollback/*` — auto‑generated reverts; guarded from accidental edits.
- `needs-human/*` — quarantine namespace for risky/blocked changes.

---

## 4) One‑Time Setup (Local & Repo)

### 4.1 Local prerequisites
- Git ≥ 2.42, PowerShell 7+, Python 3.11+ (for hooks), VS Code.
- Install hook tools as needed (ruff/black/isort, mypy, bandit, semgrep, trufflehog or gitleaks).

### 4.2 Deterministic Git config **[IDX: git‑config]**
Add to global (`~/.gitconfig`) or repo‑local (`.git/config`):

```ini
[merge]
	conflictstyle = zdiff3
[rerere]
	enabled = true
[rebase]
	autostash = true
[pull]
	rebase = true
[push]
	default = simple
```

### 4.3 Initialize hooks & policies
- Copy templates from §12 into your repo.
- Run `pre-commit install` (or equivalent runner) to enable local gates.
- Ensure `.gitattributes`, `.merge-policy.yaml`, `.merge-automation.yaml` are committed.

---

## 5) Daily Developer Workflow (Local)

### 5.1 Safe AI/Dev session **[IDX: safe‑ai‑session]**
Run tools through `scripts/Safe-AI-Session.ps1`:
- Creates `workstream/<tool>/<date>-<ulid>` branch.
- Optional initial checkpoint commit.
- On exit, runs hooks and a single push (or local backup only).

**Example:**
```powershell
# Start a guarded Aider session in the current repo
pwsh -File scripts/Safe-AI-Session.ps1 -Tool aider -Scope "src" -PushOnExit
```

### 5.2 Commit & push
- `pre-commit` gates run on commit; `pre-push` (optional) re‑checks critical rules.
- Fix what the gates report (format, type, security, secrets) before pushing.

### 5.3 What happens next
- A push to `workstream/*` triggers the CI **merge‑train** (§7).

---

## 6) Policies & Merge Strategy

### 6.1 Strategy layers
1) **.gitattributes** — file‑type merge drivers (e.g., text union, lockfiles prefer theirs, binary keep ours).  
2) **.merge-policy.yaml** — path rules, structural merges for JSON/YAML/TOML, priority rules.  
3) **rerere** — re‑apply known human conflict resolutions.

### 6.2 `.merge-policy.yaml` **[IDX: policy]**
Key ideas:
- **Structural merges** for JSON/YAML/TOML: parse → merge → stable key order.
- **Lockfiles** (e.g., `package-lock.json`, `poetry.lock`) prefer a predictable source to reduce churn.
- **Fenced paths** (`security/`, `scripts/`, `infra/`) route to quarantine on change or require extra checks.
- **Path precedence** for generated files vs hand‑edited.

> See §12.3 for a ready‑to‑use policy template.

---

## 7) CI/CD Merge‑Train Pipeline

### 7.1 Trigger & inputs
- Event: push to `workstream/**` or PR from `workstream/**`.
- Inputs: HEAD branch, base `main`, policies, rerere cache, hooks environment.

### 7.2 High‑level flow
1) Checkout with full history and fetch `main`.
2) Restore `rerere` cache and tool caches.
3) Run **PreFlight**: clean, validate tooling, detect conflicts.
4) Rebase/simulate merge against `main` applying strategies.
5) Run **verification gates** (schema, lint, type, security, secrets, diffs only for *new* issues).
6) **Decision:**
   - **PASS** → fast‑forward/write to `main`, publish artifacts, append audit.
   - **FAIL/RISK** → move to `needs-human/*` (quarantine), open PR/issue, attach logs.

### 7.3 GitHub Actions skeleton **[IDX: actions]**
See §12.5 for a full example.

---

## 8) Safety Gates & Security

### 8.1 One‑file safety profile
`config/git_safety.yml` centralizes: paths to scan, allow/deny lists, minimum thresholds, and tool toggles. CI & hooks both read this file.

### 8.2 Local hooks **[IDX: hooks]**
Typical pipeline:
- **Style:** ruff, black, isort (Python), prettier (JS/TS), shfmt (shell) as applicable
- **Types:** mypy / pyright / tsc
- **Security:** bandit, semgrep rulesets, dependency audit
- **Secrets:** trufflehog or gitleaks (pre‑commit & CI)
- **Safety checks:** disallow commits on `rollback/*`, block large binaries unless allowed

### 8.3 Secrets & tokens
- Use environment‑scoped tokens in CI; never commit secrets. Hooks block leaked values proactively.

---

## 9) Audit, Rerere & Learning Loop

### 9.1 Structured audit
- Each run appends a JSONL record in `.runs/audit/` with: branch, strategy, policy version, gate results, quarantine status, artifacts paths.
- Artifacts include: normalized diffs, policy evaluation logs, hook outputs, SARIF (if enabled).

### 9.2 Rerere **[IDX: rerere]**
- Enabled globally; cache stored/restored by CI.
- Human conflict resolutions are reused on future merges.

### 9.3 Policy harvesting
- Commit trailers (e.g., `Resolution: prefer-theirs on path=...`) can be parsed by a scheduled job to auto‑propose policy updates.

---

## 10) Rollback & Quarantine

### 10.1 Rollback **[IDX: rollback]**
- `scripts/Rollback.ps1 -Ref <sha>` creates `rollback/<date>-<ulid>` with a clean revert.
- Clears conflicting `rerere` entries for that case.
- Optionally stamps `.merge-policy.yaml` with a guard for similar diffs.

### 10.2 Quarantine **[IDX: quarantine]**
- Risky or failing branches are moved to `needs-human/<branch>-<reason>`.
- CI posts pointers (PR/issue links), logs, and next‑steps checklists.

---

## 11) Windows/PowerShell Tooling **[IDX: windows]**

### 11.1 ToolsCheck.ps1
- Verifies Git, Python, hook tools, and VS Code integrations; prints remediation steps.

### 11.2 Safe‑AI‑Session.ps1 **[IDX: safe‑ai‑session]**
- Starts a tool‑scoped branch, optional checkpoint commit, and single push on exit.
- Supports `-Tool aider|claude|opencode|continue|ollama` and `-Scope` path filters.

### 11.3 PreFlight.ps1
- Cleans, restores caches, validates policy files, and runs a dry‑run merge to surface conflicts early.

### 11.4 Worktrees (optional) **[IDX: worktrees]**
- Per‑tool worktrees isolate artifacts and editor settings without polluting the main tree.

---

## 12) Reference: Config & Snippets

### 12.1 Git config block **[IDX: git‑config]**
```ini
[merge]
	conflictstyle = zdiff3
[rerere]
	enabled = true
[rebase]
	autostash = true
[pull]
	rebase = true
[push]
	default = simple
```

### 12.2 `.pre-commit-config.yaml` **[IDX: hooks]**
> Minimal Python‑centric example; extend per your stack.
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.8.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.8
    hooks:
      - id: ruff
        args: ["--fix"]
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.2
    hooks:
      - id: mypy
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.9
    hooks:
      - id: bandit
  - repo: https://github.com/returntocorp/semgrep
    rev: v1.83.0
    hooks:
      - id: semgrep
        args: ["--config", "p/ci"]
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.4
    hooks:
      - id: gitleaks

# Optional pre-push gate
default_language_version:
  python: python3
```

### 12.3 `.merge-policy.yaml` **[IDX: policy]**
```yaml
version: 1
structural:
  json: true
  yaml: true
  toml: true
lockfiles:
  patterns: ["**/poetry.lock", "**/package-lock.json", "**/pnpm-lock.yaml"]
  strategy: prefer-theirs
fences:
  - path: "security/**"
    action: quarantine
  - path: "scripts/**"
    action: review
paths:
  - match: "docs/**"
    strategy: text-union
  - match: "**/*.json"
    strategy: json-structural
  - match: "**/*.yaml"
    strategy: yaml-structural
  - match: "**/*.toml"
    strategy: toml-structural
```

### 12.4 `.gitattributes`
```gitattributes
# Text defaults
* text=auto

# Favor union merges for docs to reduce churn
*.md merge=union

# Structural drivers are applied by the policy/tooling layer
# (left as text here to keep Git simple)

# Binary safety
*.png binary
*.jpg binary
*.pdf binary
```

### 12.5 `.github/workflows/merge-train.yml` **[IDX: actions]**
```yaml
name: Merge Train
on:
  push:
    branches: ["workstream/**"]
  pull_request:
    branches: ["main"]

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Setup Python
        uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - name: Restore caches (tools, rerere)
        uses: actions/cache@v4
        with:
          path: |
            ~/.cache/pip
            .git/rr-cache
          key: ${{ runner.os }}-rr-${{ github.sha }}
          restore-keys: |
            ${{ runner.os }}-rr-
      - name: PreFlight
        run: pwsh -File scripts/PreFlight.ps1
      - name: AutoMerge Workstream
        run: pwsh -File scripts/AutoMergeWorkstream.ps1
      - name: Verification Gates
        run: |
          pre-commit run --all-files || true
          python scripts/ci_verify.py
      - name: Decide → main or quarantine
        run: pwsh -File scripts/CiDecide.ps1
      - name: Upload audit artifacts
        uses: actions/upload-artifact@v4
        with:
          name: audit-${{ github.run_id }}
          path: .runs/**
```

### 12.6 `scripts/Safe-AI-Session.ps1` **[IDX: safe‑ai‑session]**
```powershell
param(
  [Parameter(Mandatory=$true)][string]$Tool,
  [string]$Scope = ".",
  [switch]$PushOnExit
)
$ulid = (Get-Date -Format "yyyyMMdd-HHmmss")
$branch = "workstream/$Tool/$ulid"
& git switch -c $branch
if (Test-Path $Scope) { git add $Scope; git commit -m "feat(session): start $Tool session [$ulid]" --allow-empty }
try {
  Write-Host "Session started on $branch. Do your work…"
  Read-Host "Press Enter to end session"
} finally {
  pre-commit run --all-files
  if ($PushOnExit) { git push -u origin $branch }
}
```

### 12.7 `scripts/Rollback.ps1` **[IDX: rollback]**
```powershell
param([Parameter(Mandatory=$true)][string]$Ref)
$ulid = (Get-Date -Format "yyyyMMdd-HHmmss")
$rb = "rollback/$ulid"
& git switch -c $rb main
& git revert --no-edit $Ref
# Optional: clear rerere entry for this conflict case
# Optional: stamp policy exception proposal
Write-Host "Rollback prepared on $rb"
```

---

## 13) Editing Guide & Conventions
- **Section IDs** like `[SEC‑7.3]` are implicit in headings (use your editor’s Outline view or ToC above).
- **Index tags** like `[IDX: policy]` appear where implementers are likely to edit; search for them to jump quickly.
- **Snippets** in §12 are canonical; update there first, then cross‑check dependent sections.
- **Keep changes atomic:** one PR per concern (policy vs hooks vs CI), so the audit trail stays readable.

---

## 14) FAQ & Troubleshooting
- **Hooks blocking my commit?** Run `pre-commit run --all-files` locally and fix reported issues; see §8.2.
- **Merge‑train failed with quarantine. Why?** Check `.runs/audit/*.jsonl` and artifacts uploaded by CI; see §7.2, §9.1.
- **Conflicts every time on JSON?** Ensure structural merge is enabled in policy; see §6.2.
- **Accidental edits on `rollback/*`?** Hook rules should block; verify §8.2 and your hook versions.

---

## 15) Change Log
- **v3.0** — Unified single‑source doc; adds editing index, CI skeleton, Safe‑AI‑Session snippet.

