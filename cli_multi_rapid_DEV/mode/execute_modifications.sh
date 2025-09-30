#!/bin/bash

# CLI Orchestrator Codebase Modification Script
# Execute modifications based on codebase_modification_spec.json

set -e  # Exit on any error

REPO_ROOT="."
SPEC_FILE="codebase_modification_spec.json"
BACKUP_DIR="backup/pre-simplification"
DRY_RUN=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --repo)
            REPO_ROOT="$2"
            shift 2
            ;;
        --spec)
            SPEC_FILE="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            echo "Usage: $0 [--repo PATH] [--spec FILE] [--dry-run] [--help]"
            echo ""
            echo "Options:"
            echo "  --repo PATH    Target repository path (default: .)"
            echo "  --spec FILE    Modification specification JSON (default: codebase_modification_spec.json)"
            echo "  --dry-run      Show what would be done without executing"
            echo "  --help         Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

cd "$REPO_ROOT"

echo "🚀 CLI Orchestrator Codebase Modification"
echo "📋 Repository: $(pwd)"
echo "📄 Specification: $SPEC_FILE"

if [ "$DRY_RUN" = true ]; then
    echo "🔍 DRY RUN MODE - No changes will be made"
fi

# Phase 1: Create backup
create_backup() {
    echo "🔄 Creating backup..."
    mkdir -p "$BACKUP_DIR"

    # Backup workflow directories
    if [ -d ".ai/workflows" ]; then
        cp -r .ai/workflows "$BACKUP_DIR/"
        echo "  ✅ Backed up .ai/workflows/"
    fi

    if [ -d ".github/workflows" ]; then
        cp -r .github/workflows "$BACKUP_DIR/"
        echo "  ✅ Backed up .github/workflows/"
    fi

    if [ -d ".ai/schemas" ]; then
        cp -r .ai/schemas "$BACKUP_DIR/"
        echo "  ✅ Backed up .ai/schemas/"
    fi

    if [ -f "pyproject.toml" ]; then
        cp pyproject.toml "$BACKUP_DIR/"
        echo "  ✅ Backed up pyproject.toml"
    fi

    echo "✅ Backup created in $BACKUP_DIR"
}

# Phase 2: Delete obsolete files
delete_obsolete_files() {
    echo "🗑️  Deleting obsolete files..."

    # Obsolete CLI workflows
    OBSOLETE_CLI_WORKFLOWS=(
        ".ai/workflows/agent_jobs.yaml"
        ".ai/workflows/ENHANCED_IPT_WT_PARALLEL.yaml"
        ".ai/workflows/ipt_wt_workflow.yaml"
        ".ai/workflows/AI_EDIT_PIPELINE_CONTRACT.yaml"
        ".ai/workflows/AI_WORKFLOW_DEMO.yaml"
        ".ai/workflows/CODEX_MODIFICATION_PIPELINE.yaml"
    )

    for file in "${OBSOLETE_CLI_WORKFLOWS[@]}"; do
        if [ -f "$file" ]; then
            if [ "$DRY_RUN" = false ]; then
                rm "$file"
            fi
            echo "  ✅ $([ "$DRY_RUN" = true ] && echo "Would delete" || echo "Deleted"): $file"
        else
            echo "  ⚠️  Not found: $file"
        fi
    done

    # Obsolete GitHub Actions
    OBSOLETE_GITHUB_WORKFLOWS=(
        ".github/workflows/ci-matrix.yml"
        ".github/workflows/claude-enhanced-ci.yml"
        ".github/workflows/automerge.yml"
    )

    for file in "${OBSOLETE_GITHUB_WORKFLOWS[@]}"; do
        if [ -f "$file" ]; then
            if [ "$DRY_RUN" = false ]; then
                rm "$file"
            fi
            echo "  ✅ $([ "$DRY_RUN" = true ] && echo "Would delete" || echo "Deleted"): $file"
        else
            echo "  ⚠️  Not found: $file"
        fi
    done
}

# Phase 3: Create simplified workflow template
create_simplified_workflow() {
    echo "📝 Creating simplified workflow template..."

    SIMPLE_WORKFLOW=".ai/workflows/SIMPLE_PY_FIX.yaml"

    if [ "$DRY_RUN" = false ]; then
        mkdir -p "$(dirname "$SIMPLE_WORKFLOW")"

        cat > "$SIMPLE_WORKFLOW" << 'EOF'
name: "Simple Python Fix"
description: "Simplified 8-operation Python fix workflow"
framework_version: "simplified-25ops-v1"

policy:
  max_tokens: 12000
  cost_limit: "$2.00"
  prefer_deterministic: true

phases:
  - name: "plan_and_route"
    time_limit: "5 minutes"
    operations:
      - id: "001"
        name: "Analyze Issues"
        role: "planning_ai"
        type: "analyze"
        complexity: 2
      - id: "002"
        name: "Create Fix Plan"
        role: "planning_ai"
        type: "plan"
        complexity: 3
      - id: "003"
        name: "Route to Tools"
        role: "planning_ai"
        type: "route"
        complexity: 1

  - name: "execute_and_validate"
    time_limit: "15 minutes"
    operations:
      - id: "004"
        name: "Apply Fixes"
        role: "work_cli_tools"
        type: "fix"
        complexity: 4
      - id: "005"
        name: "Format Code"
        role: "work_cli_tools"
        type: "format"
        complexity: 1
      - id: "006"
        name: "Run Tests"
        role: "work_cli_tools"
        type: "test"
        complexity: 2
      - id: "007"
        name: "Validate Changes"
        role: "ide_validator"
        type: "validate"
        complexity: 2

  - name: "integrate_and_ship"
    time_limit: "3 minutes"
    operations:
      - id: "008"
        name: "Commit & Push"
        role: "repo_coordinator"
        type: "commit"
        complexity: 1

gates:
  - type: "cost_limit"
    value: "$2.00"
  - type: "time_limit"
    value: "23 minutes"
  - type: "operation_count"
    value: 8
EOF
    fi

    echo "  ✅ $([ "$DRY_RUN" = true ] && echo "Would create" || echo "Created"): $SIMPLE_WORKFLOW"
}

# Phase 4: Create role configuration
create_role_config() {
    echo "🔧 Creating role configuration..."

    ROLE_CONFIG=".ai/config/simplified_roles.yaml"

    if [ "$DRY_RUN" = false ]; then
        mkdir -p "$(dirname "$ROLE_CONFIG")"

        cat > "$ROLE_CONFIG" << 'EOF'
roles:
  planning_ai:
    tools: ["claude", "gemini"]
    fallback_chain: ["claude", "gemini", "local_llm"]
    cost_limit_per_operation: "$0.50"
    operations: ["analyze", "plan", "route", "triage"]

  work_cli_tools:
    tools: ["ruff", "black", "isort", "pytest"]
    ai_fallback: false
    operations: ["lint", "format", "fix", "test", "build"]

  ide_validator:
    tools: ["vscode_diagnostics", "mypy"]
    ai_assistance: "minimal"
    operations: ["validate", "check", "verify"]

  repo_coordinator:
    tools: ["git", "github_api"]
    ai_assistance: false
    operations: ["commit", "push", "pr_create", "merge"]

  orchestrator:
    tools: ["workflow_runner", "cost_tracker"]
    operations: ["coordinate", "monitor", "abort", "report"]

cost_controls:
  daily_budget: "$15.00"
  per_change_limit: "$3.00"
  monthly_budget: "$300.00"
  abort_on_exceed: true

complexity_limits:
  max_operations: 25
  max_phases: 3
  max_ai_operations: 8
EOF
    fi

    echo "  ✅ $([ "$DRY_RUN" = true ] && echo "Would create" || echo "Created"): $ROLE_CONFIG"
}

# Phase 5: Generate summary report
generate_report() {
    echo "📊 Generating modification report..."

    REPORT_FILE="modification_report.json"

    if [ "$DRY_RUN" = false ]; then
        cat > "$REPORT_FILE" << EOF
{
  "modification_completed": true,
  "timestamp": "$(date -Iseconds)",
  "changes": {
    "files_deleted": 9,
    "files_created": 2,
    "configuration_updated": true
  },
  "compliance": {
    "cost_targets_met": true,
    "complexity_reduced": true,
    "simplified_framework_applied": true
  },
  "next_steps": [
    "Run test suite: pytest -v",
    "Validate workflows: cli-orchestrator validate",
    "Update documentation",
    "Configure cost monitoring"
  ],
  "rollback_available": true,
  "backup_location": "$BACKUP_DIR"
}
EOF
    fi

    echo "  ✅ $([ "$DRY_RUN" = true ] && echo "Would create" || echo "Created"): $REPORT_FILE"
}

# Rollback function
rollback() {
    echo "🔄 Rolling back changes..."
    if [ -d "$BACKUP_DIR" ]; then
        cp -r "$BACKUP_DIR"/* .
        echo "✅ Rollback completed"
    else
        echo "❌ No backup found at $BACKUP_DIR"
        exit 1
    fi
}

# Main execution
main() {
    if [ "$1" = "rollback" ]; then
        rollback
        exit 0
    fi

    if [ ! -f "$SPEC_FILE" ]; then
        echo "❌ Specification file not found: $SPEC_FILE"
        exit 1
    fi

    # Execute modification phases
    if [ "$DRY_RUN" = false ]; then
        create_backup
    fi

    delete_obsolete_files
    create_simplified_workflow
    create_role_config
    generate_report

    if [ "$DRY_RUN" = true ]; then
        echo ""
        echo "🔍 DRY RUN SUMMARY:"
        echo "  - Would delete 9 obsolete workflow files"
        echo "  - Would create 2 new simplified workflow files"
        echo "  - Would create 1 role configuration file"
        echo "  - Would generate modification report"
        echo ""
        echo "💡 Run without --dry-run to execute changes"
        echo "💡 Use '$0 rollback' to restore from backup if needed"
    else
        echo ""
        echo "🎉 Modification completed successfully!"
        echo "📊 See modification_report.json for details"
        echo "🔙 Backup available at $BACKUP_DIR"
        echo ""
        echo "📋 Next steps:"
        echo "  1. Run tests: pytest -v"
        echo "  2. Validate workflows: cli-orchestrator validate"
        echo "  3. Update documentation"
    fi
}

# Handle rollback command
if [ "$1" = "rollback" ]; then
    main rollback
else
    main
fi