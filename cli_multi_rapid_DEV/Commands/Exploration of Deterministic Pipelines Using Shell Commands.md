* **Exploration of Deterministic Pipelines Using Shell Commands**

  * **Objective**

    * User wanted to explore how shell commands from various applications could be used together to create deterministic pipelines.
    * Emphasis on minimizing AI unpredictability and maximizing reproducibility.
  * **Relevant Tools and CLIs Identified**

    * Git and GitHub CLI (`gh`) for version control and PR automation.
    * PowerShell for Windows-native orchestration and scripting.
    * Python for validators, generators, scrapers, and glue code.
    * VS Code CLI (`code`) for orchestrating tasks from the editor.
    * Windows Package Manager (`winget`) for deterministic installs.
    * Claude Code (planner) and Codex CLI (diff generator) as AI assistants.
    * Linters and formatters across domains (`ruff`, `black`, `psscriptanalyzer`, `sqlfluff`).
    * Ollama/local models for cost-aware AI fallback.
  * **Deterministic Design Rules**

    * Command contracts must define inputs, outputs, side-effects, idempotency, exit codes, dry-run support.
    * State stamps/lock files to ensure idempotence.
    * No implicit prompts, always pass flags.
    * Time-bounded retries with exponential backoff.
    * Structured logs as JSONL.
    * Gates (lint, tests, security scans) before merges.
    * Repository hygiene enforced automatically (branching, pruning, protection).
    * Dry-runs before applying changes.
    * Failures must produce actionable, machine-readable outputs.

* **Command Patterns for Pipelines**

  * **Atomic Savepoint (gh-checkpoint)**

    * Combines `git add`, `commit`, `push` with PR creation.
    * Ensures state is synced to remote.
  * **AI Plan → Diff → Apply**

    * Claude generates a structured plan.
    * Codex generates a patch (unified diff).
    * Apply patch in new branch, run quality gates, push, open PR.
  * **Repository Hygiene**

    * Scripted policy to prune branches via `gh api` + Python.
    * Dry-run mode before application.
  * **Environment Pinning and Verification**

    * Using `winget` with lockfiles for deterministic environment setup.
  * **VS Code Integration**

    * VS Code tasks can trigger these pipelines as entry points.

* **Comprehensive YAML Workflow File**

  * **Meta and Definitions**

    * Version, last updated, retry policies, logging/output schema, quality gates.
  * **Commands**

    * `gh-checkpoint`: commits and syncs work to GitHub.
    * `ai-plan`: Claude Code generates a plan.
    * `ai-diff`: Codex generates patch from plan.
    * `apply-diff-to-branch`: creates feature branch and applies patch.
    * `quality-gates`: runs linting and tests.
    * `push-and-pr`: pushes branch and opens PR.
    * `hygiene-plan` and `hygiene-apply`: branch cleanup workflow.
    * `env-pin`: winget environment installation and verification.
  * **Pipelines**

    * `plan-diff-apply`: AI-assisted flow from plan to patch to PR.
    * `repo-hygiene`: scheduled cleanup pipeline.

* **Plain English Explanation of the YAML**

  * Patch file describes specific code modifications.
  * Pipelines describe the sequence of deterministic actions to apply those modifications.
  * `plan-diff-apply` pipeline: plan → patch → apply → gates → push PR.
  * `repo-hygiene` pipeline: prune branches.

* **Optimization Discussion: Reducing Token Usage**

  * **Observation**

    * Claude Code generating both plan JSON and Codex diff is token- and step-expensive.
  * **Proposed Optimization**

    * Use Claude Code to directly generate a unified diff (skip Codex).
    * New `ai-diff-direct` command replaces `ai-plan` + `ai-diff`.
  * **Token Efficiency Strategies**

    * Narrow context to only relevant files or snippets.
    * Provide repo maps instead of raw file bodies.
    * Short, schema’d prompts requiring only diffs.
    * Chunk large edits into multiple diffs.
    * Cap output (context lines, max hunk size).
  * **Fallback**

    * If direct diffs fail, fall back to plan + Codex pipeline.

* **Parallel Workstreams from Patch Files**

  * **Goal**

    * Identify independent modifications that can be executed simultaneously.
    * Parallelization is only safe if workstreams are independent.
  * **Definition of Independence**

    * No overlapping file modifications.
    * No dependent files being changed across streams.
    * No global artifacts (lockfiles, schema, CI configs) touched simultaneously.
    * No overlapping impacted tests.
  * **Tiered Partitioning Approach**

    * **Tier 0**: Cheap, deterministic (path rules, file-level partitioning).
    * **Tier 1**: Static dependency graph refinement (AST import analysis, build system graphs).
    * **Tier 2**: Test impact analysis (coverage maps).
    * **Tier 3**: AI arbitration by Claude Code only for ambiguous cases.
  * **Guardrails**

    * Global artifacts trigger merging of shards.
    * Public interface changes merge with dependent changes.
    * Release coupling forces grouping.

* **Scripts for Workstream Partitioning**

  * **`patch_splitter.py`**

    * Splits unified diffs into per-bucket shards by regex/path rules.
  * **`deps_refine.py`**

    * Refines shards by checking dependency graph, globals, coverage, merges connected components.
  * **Validation**

    * Run `git apply --check` for each shard.
    * Run only impacted tests.
  * **Execution**

    * Each final shard (workstream) gets its own branch, commit, quality gates, and PR.

* **Maintenance Concerns**

  * **User Concern**

    * Guardrails and Tier 1 dependency rules might require multi-file solutions with updates whenever code changes.
  * **Clarification**

    * Not necessary. Use:

      * Regex/glob rules for paths (self-adapting).
      * Auto-generated dependency graphs rebuilt each run.
      * Optional coverage maps updated via CI.
      * Rule-based global patterns (rarely change).
    * Single-file control plane possible (`parallel_rules.yaml`) for all rules, updated rarely.

* **Nature of Workstreams**

  * **Question**

    * Are workstreams patch files, plans, or instruction sets?
  * **Clarification**

    * They can be represented in three ways:

      * **Patch-as-artifact**: unified diff, deterministic, preferred.
      * **Plan-as-representation**: JSON/YAML describing goals and targets.
      * **Instruction-as-execution**: sequence of deterministic commands.
    * Recommended: **patch + manifest** (manifest = metadata/instructions).

* **Manifest vs Patch**

  * **Patch**

    * Unified diff describing *what* changes in the code.
  * **Manifest**

    * Metadata and deterministic pipeline describing *how* to apply the patch.
    * Contains branch, steps, gates, dependencies, PR labeling, etc.
  * **Example**

    * Patch modifies a Python function to add a timeout.
    * Manifest specifies checkout, apply patch, run `ruff`, run `pytest`, commit, push, create PR.

* **Prebuilt Pipelines vs Diff-Driven Pipelines**

  * **Issue**

    * Prebuilt pipelines are deterministic but may not fit all diffs.
    * New diffs may require different deterministic steps.
  * **Two Strategies**

    * **Universal Pipeline**: apply patch, run base checks, push PR. Safe but suboptimal.
    * **Diff Analysis + Pipeline Synthesis**: analyze diff, then create tailored deterministic manifest with correct steps (formatters, migrations, builds).
  * **Rules Engine for Pipeline Synthesis**

    * File extensions, paths, and patterns trigger domain-specific deterministic adapters.
    * Example mappings:

      * Python files → `ruff`, `pytest`.
      * Lockfiles → reinstall dependencies.
      * SQL migrations → DB dry-run.
      * CI workflows → `actionlint`.
      * Dockerfiles → `hadolint` + smoke build.
    * Produces manifest with deterministic steps.

* **Library of Shell Commands**

  * **User Concept**

    * Create a library of proven, deterministic shell commands across domains.
    * AI can reference this library when deciding pipelines, preferring shell commands over custom scripts.
  * **Capability Registry**

    * YAML file defining reusable deterministic shell commands with match rules.
    * Each capability defines what it provides (`lint`, `unit_test`, `deps_install`, etc.).
  * **Selector Rules**

    * Defines order of preference: shell commands > standard tools > scripts > AI.
    * Maps detected needs from diffs to capabilities.
  * **Execution Process**

    * Diff analyzer extracts file types/paths.
    * Selector maps to capabilities.
    * Manifest synthesized with base steps + selected deterministic commands + finalize steps.
  * **Reliability Guardrails**

    * Preflight patch check.
    * Idempotent command design.
    * Retries for network steps.
    * Global file detection to prevent unsafe parallelism.
    * Abort on non-zero exit with structured logs.
  * **AI Role**

    * Not used for routine selection.
    * Only used as fallback to arbitrate ambiguous cases or generate a new command, which is then added to capability registry.

* **Three-Layer Framework Recap**

  * **Layer 1**: Generate patch file (what changes).
  * **Layer 2**: Partition into independent workstreams.
  * **Layer 3**: Execute using deterministic pipelines, preferring shell commands from a capability registry.

* **User Clarification and Confusion**

  * User was unsure if the approach was correct or missing the point.
  * Confirmed: user is on track.
  * Key insight: patch = what changes, manifest/pipeline = how to execute.
  * Deterministic shell command library is a robust way to minimize friction and AI reliance.
