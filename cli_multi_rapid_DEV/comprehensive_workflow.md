# Comprehensive Workflow: A Detailed, Actionable Guide

This document provides a complete, step-by-step guide to the integrated and deterministic workflow. It combines the conceptual clarity of a structured workflow with the concrete, actionable commands needed for implementation. Each step is meticulously detailed to explain its purpose, execution method, and role within the larger pipeline.

## Phase 0: PRECHECK (Foundation Setup)

**Objective:** To establish a clean, well-structured, and deterministic foundation for the project before any development work begins.

| Step | Action | Executor | Type | Implementation | Description | GitHub Save Point? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Check Git State | `Developer` | ⚙️ [Deterministic Command] | `git status --porcelain` | Verifies that the working directory is clean (no uncommitted changes). The command should return empty. | No |
| 2 | Scaffold Directories | `Developer` | ⚙️ [Deterministic Command] | `mkdir -p .ai agentic schemas scripts phases tests tools .github/workflows` | Creates the standard directory structure required for the deterministic workflow. | No |
| 3 | Create Baseline Config | `Developer` | ⚙️ [Deterministic Command] | `touch .ai/.gitkeep && echo 'version: 1.0' > agentic/agentic.yaml` | Creates a baseline configuration file for the agentic system. | No |
| 4 | Initialize Job Schema | `Developer` | 📜 [Deterministic Script] | `init_schema.py` | Creates the `schemas/job.schema.json` file, which defines the structure for task manifests. | No |
| 5 | Add Deterministic Wrapper | `Developer` | 📜 [Deterministic Script] | `create_wrapper.sh` | Creates `scripts/deterministic.sh`, a bash wrapper that ensures all scripts are executed with consistent RunID tracking for auditability. | No |

## Phase 1: PLAN (Repository & Workflow Planning)

**Objective:** To define the high-level plan, including phase objectives, dependencies, and readiness criteria.

| Step | Action | Executor | Type | Implementation | Description | GitHub Save Point? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 6 | Create Production Checklist | `planning_ai` | 🤖 [AI Decision] | `claude_code` | Generates a `.ai/production_checklist.md` file with a comprehensive list of criteria that must be met before deployment. | No |
| 7 | Define Phase Objectives | `planning_ai` | 🤖 [AI Decision] | `claude_code` | Creates `.ai/phase_plan.md`, which outlines the entry and exit criteria for each phase of the workflow. | No |
| 8 | Setup Dependency Graph | `planning_ai` | 🤖 [AI Decision] | `claude_code` | Creates `.ai/dependencies.yaml` to define the interdependencies between different phases and components. | No |

## Phase 2: EXECUTE & VALIDATE (Implementation & Quality Assurance)

**Objective:** To implement the planned changes and validate them against the defined quality gates.

| Step | Action | Executor | Type | Implementation | Description | GitHub Save Point? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 9 | Create Orchestrator Skeleton | `work_cli_tools` | 🤖 [AI Decision] | `aider` | Generates the main `orchestrator.py` file, which will act as the state machine for the workflow. | No |
| 10 | Apply Code Modifications | `work_cli_tools` | 🤖 [AI Decision] | `aider` | Applies the necessary code modifications as per the plan. | No |
| 11 | Setup Pre-commit Hooks | `repo_coordinator` | ⚙️ [Deterministic Command] | `pre-commit install` | Installs the pre-commit hooks defined in `.pre-commit-config.yaml` to automate linting and formatting. | No |
| 12 | Run Validation | `ide_validator` | ⚙️ [Deterministic Command] | `ruff check . && black --check . && mypy src` | Runs a series of checks for linting, formatting, and type safety. | No |
| 13 | Run Tests | `ide_validator` | ⚙️ [Deterministic Command] | `pytest -q --cov=src --cov-report=term-missing --cov-fail-under=85` | Executes the test suite and checks for a minimum of 85% code coverage. | No |
| 14 | **Commit Changes** | `repo_coordinator` | ⚙️ [Deterministic Command] | `gh-checkpoint` | Stages all validated changes and creates a new commit with a conventional commit message. | **Yes** |

## Phase 3: INTEGRATE & SHIP (CI/CD & Release)

**Objective:** To integrate the changes into the main branch and prepare for a new release.

| Step | Action | Executor | Type | Implementation | Description | GitHub Save Point? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 15 | Create CI Workflow | `repo_coordinator` | 📜 [Deterministic Script] | `setup_ci.py` | Creates the `.github/workflows/validate.yml` file for continuous integration. | No |
| 16 | **Create Pull Request** | `repo_coordinator` | ⚙️ [Deterministic Command] | `gh-create-pr` | Creates a new pull request, automatically populating the title and body from the commit history. | **Yes** |
| 17 | **Merge & Tag Release** | `repo_coordinator` | ⚙️ [Deterministic Command] | `gh-release` | After the PR is approved and merged, this command creates a new version tag and generates release notes. | **Yes** |
| 18 | **Cleanup Branches** | `repo_coordinator` | ⚙️ [Deterministic Command] | `gh-cleanup-branches` | Cleans up the temporary branches used during the workflow. | **Yes** |

## Multi-Stream Execution (Parallel Workflows)

This section outlines how to run multiple, independent workflows in parallel, using a branching strategy to prevent conflicts.

| Stream | Executor | Implementation | Description |
| :--- | :--- | :--- | :--- |
| **A: Foundation** | `claude_code` | `git checkout -b stream-a-foundation && ... && git push -u origin stream-a-foundation` | Focuses on the core infrastructure and setup of the project. |
| **B: Schemas** | `Codex` | `git checkout -b stream-b-schemas && ... && git push -u origin stream-b-schemas` | Defines the data schemas and validation rules. |
| **C: Orchestration** | `claude_code` | `git checkout -b stream-c-orchestration && ... && git push -u origin stream-c-orchestration` | Implements the main workflow orchestration logic. |

## Common CLI Commands

These commands are available throughout the workflow to provide status updates and control.

| Command | Description |
| :--- | :--- |
| `cli-multi-rapid phase stream list` | Lists all available workflow streams. |
| `cli-multi-rapid phase stream run <stream-name> --dry` | Performs a dry run of a specific workflow stream. |
| `cli-multi-rapid workflow-status` | Checks the current status of the overall workflow. |
| `cli-multi-rapid compliance check` | Runs a compliance check against the defined quality gates. |
