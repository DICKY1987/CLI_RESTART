# Unified Atomic Workflow: Command-Based Multi-Agent Pipeline

## Core Principle: Deterministic Commands + AI Decision Points
### Primary Deliverable: Error-Free Modified Codebase

---

## PHASE 0: ENTRY POINT CONVERGENCE & TASK CLASSIFICATION

### Entry Point Processing [AI MAKES DECISIONS] (10 atoms)
**Preserved as-is - requires AI reasoning**
```yaml
atom_001: detect_entry_point_type | Role: orchestrator
atom_002: validate_input_format_compliance | Role: orchestrator  
atom_003: extract_modification_requirements | Role: planning_ai
atom_004: analyze_user_intent_patterns | Role: planning_ai
atom_005: determine_analysis_depth_required | Role: thinking_ai
atom_006: assess_modification_complexity | Role: thinking_ai
atom_007: calculate_resource_requirements | Role: cost_resource_manager
atom_008: establish_quality_thresholds | Role: qa_test_agent
atom_009: determine_convergence_readiness | Role: orchestrator
atom_010: route_to_planning_pipeline | Role: orchestrator
```

### **COMMAND: `precheck`** [DETERMINISTIC]
```yaml
purpose: Fast readiness validation + routing inputs for planning phase
replaces_atoms:
  - range: atom_011..atom_020  # Complexity Assessment & Service Routing
    count: 10
implementation:
  script: |
    Scans project files, measures scope, checks tool availability (git, python, node, etc.),
    verifies API quotas, calculates complexity score, determines routing strategy,
    locks resource allocation, and emits routing decision JSON.
  bash: ./.det-tools/scripts/precheck.sh
  pwsh: ./.det-tools/scripts/Precheck.ps1
outputs: .det-tools/out/precheck.json
success_criteria:
  - All required tools available
  - Quota limits confirmed
  - Complexity score calculated
  - JSON contains: {files, scope, complexity_score, selected_route, tools_available}
```

### **COMMAND: `init-moddoc`** [DETERMINISTIC]
```yaml
purpose: Bootstrap modification tracking document and audit trail
replaces_atoms:
  - range: atom_021..atom_030  # ModDoc Initialization
    count: 10
implementation:
  script: |
    Creates moddoc.json with schema, generates unique modification ID, sets timestamps,
    initializes cost tracking structures, creates audit trail, sets up monitoring hooks,
    establishes rollback points, configures notifications, validates schema compliance.
  bash: ./.det-tools/scripts/init-moddoc.sh
  pwsh: ./.det-tools/scripts/Init-ModDoc.ps1
outputs: moddoc.json
success_criteria:
  - moddoc.json created and schema-valid
  - run_id, timestamps, audit_trail present
  - Cost tracking initialized
  - Rollback points established
```

---

## PHASE 1: UNIFIED PLANNING & ANALYSIS

### **COMMAND: `analyze-project`** [AI-ASSISTED]
```yaml
purpose: Comprehensive codebase research and information gathering
replaces_atoms:
  - range: atom_031..atom_045  # Research & Information Gathering
    count: 15
implementation:
  script: |
    Analyzes existing codebase structure, identifies dependencies and business logic,
    researches best practices, assesses security/performance impacts, evaluates technical debt,
    identifies testing/documentation needs, analyzes compatibility constraints and integration points,
    assesses deployment requirements, evaluates rollback scenarios, synthesizes findings.
    Calls AI agents (planning_ai, thinking_ai) for complex analysis.
  bash: ./.det-tools/scripts/analyze_project.sh
  pwsh: ./.det-tools/scripts/Analyze-Project.ps1
outputs: .det-tools/out/analysis_report.json
success_criteria:
  - Complete dependency map
  - Security/performance risk assessment
  - Testing requirements identified
  - Integration points documented
  - JSON contains: {dependencies, risks, technical_debt, testing_needs, deployment_reqs}
```

### Modification Planning [AI MAKES DECISIONS] (20 atoms)
**Preserved as-is - requires AI reasoning and decomposition**
```yaml
atom_046: decompose_requirements_to_tasks | Role: planning_ai
atom_047: identify_file_modifications | Role: planning_ai
atom_048: determine_modification_sequence | Role: thinking_ai
atom_049: assess_parallelization_opportunities | Role: orchestrator
atom_050: identify_critical_path | Role: thinking_ai
atom_051: estimate_task_durations | Role: planning_ai
atom_052: assign_task_priorities | Role: planning_ai
atom_053: determine_resource_allocation | Role: cost_resource_manager
atom_054: establish_dependencies | Role: thinking_ai
atom_055: identify_risk_factors | Role: resilience_agent
atom_056: create_contingency_plans | Role: resilience_agent
atom_057: define_success_criteria | Role: qa_test_agent
atom_058: establish_quality_gates | Role: qa_test_agent
atom_059: determine_approval_requirements | Role: human_oversight
atom_060: create_execution_schedule | Role: orchestrator
atom_061: validate_plan_feasibility | Role: thinking_ai
atom_062: optimize_resource_usage | Role: cost_resource_manager
atom_063: finalize_modification_plan | Role: planning_ai
atom_064: generate_moddoc_content | Role: planning_ai
atom_065: validate_moddoc_schema | Role: orchestrator
```

### **COMMAND: `setup-workstreams`** [DETERMINISTIC]
```yaml
purpose: Create isolated parallel workstreams with monitoring and rollback capability
replaces_atoms:
  - range: atom_066..atom_080  # Workstream Creation
    count: 15
implementation:
  script: |
    Identifies independent code clusters, creates workstream definitions with unique IDs,
    establishes isolation boundaries, configures git branch strategies and worktree environments,
    initializes monitoring per workstream, establishes inter-stream communication channels,
    configures synchronization points and conflict detection, sets up rollback procedures,
    validates isolation guarantees.
  bash: ./.det-tools/scripts/setup_workstreams.sh
  pwsh: ./.det-tools/scripts/Setup-Workstreams.ps1
outputs: .det-tools/out/workstreams.json
success_criteria:
  - N isolated worktrees/branches created
  - Sync points configured
  - Conflict detection active
  - Rollback hooks established
  - JSON contains: {workstream_ids, branches, isolation_verified}
```

### **COMMAND: `assign-tools`** [DETERMINISTIC]
```yaml
purpose: Map tasks to roles to tools with parameters, fallbacks, and cost limits
replaces_atoms:
  - range: atom_081..atom_090  # Tool Assignment & Configuration
    count: 10
implementation:
  script: |
    Maps each task to appropriate role, selects primary tools per role based on task complexity,
    configures tool-specific parameters, establishes fallback sequences (primary→secondary→tertiary),
    validates tool availability and health, configures tool integrations and monitoring,
    sets cost limits per tool, validates complete configuration.
  bash: ./.det-tools/scripts/assign_tools.sh
  pwsh: ./.det-tools/scripts/Assign-Tools.ps1
outputs: .det-tools/out/toolmap.json
success_criteria:
  - All tasks have assigned tools
  - Fallback chains configured
  - Cost limits set
  - Health checks passing
  - JSON contains: {task_tool_map, fallbacks, cost_limits, health_status}
```

---

## PHASE 2: PARALLEL CODE MODIFICATION EXECUTION

### **COMMAND: `exec-core-edits`** [AI-ASSISTED]
```yaml
purpose: Workstream A - Core business logic modifications with validation
replaces_atoms:
  - range: atom_091..atom_115  # Workstream A: Core Logic Modifications
    count: 25
implementation:
  script: |
    Initializes workstream A context and checks out dedicated branch, loads modification specs,
    analyzes target files, generates code modifications (calls work_cli_tools AI),
    applies patches, validates syntax/imports/types, auto-fixes simple errors,
    applies formatting/linting rules, runs unit tests, fixes failures,
    validates business logic, optimizes performance, adds error handling,
    updates inline documentation, commits and pushes changes, generates workstream report,
    updates cost tracking, validates completion criteria.
  bash: ./.det-tools/scripts/ws_core_edits.sh
  pwsh: ./.det-tools/scripts/WS-Core-Edits.ps1
outputs: 
  - .det-tools/out/ws_a_report.json
  - workstream-a branch with commits
success_criteria:
  - Clean diff committed and pushed
  - Syntax/lint/format passing
  - Unit tests green
  - Business logic validated
  - Documentation updated
```

### **COMMAND: `exec-config-infra`** [DETERMINISTIC]
```yaml
purpose: Workstream B - Configuration and infrastructure changes with validation
replaces_atoms:
  - range: atom_116..atom_140  # Workstream B: Configuration & Infrastructure
    count: 25
implementation:
  script: |
    Initializes workstream B context and checks out dedicated branch, loads configuration specs,
    identifies all config files (YAML/JSON/ENV), backs up existing configs,
    applies configuration modifications, validates syntax and schema compliance,
    checks compatibility with existing services, validates environment variables,
    tests config loading mechanisms, verifies service connectivity,
    validates security settings and permission levels, checks network configurations,
    tests failover scenarios, verifies backup procedures and monitoring hooks,
    validates alert configurations, documents all changes, commits and pushes,
    generates configuration report, updates inventory, validates success criteria.
  bash: ./.det-tools/scripts/ws_config_infra.sh
  pwsh: ./.det-tools/scripts/WS-Config-Infra.ps1
outputs:
  - .det-tools/out/ws_b_report.json
  - workstream-b branch with commits
success_criteria:
  - Config schema-valid
  - Environment variables verified
  - Service connectivity confirmed
  - Security/network checks passing
  - Backup procedures tested
```

### **COMMAND: `exec-tests-docs`** [AI-ASSISTED]
```yaml
purpose: Workstream C - Test generation/execution and documentation updates
replaces_atoms:
  - range: atom_141..atom_165  # Workstream C: Tests & Documentation
    count: 25
implementation:
  script: |
    Initializes workstream C context and checks out dedicated branch, analyzes test requirements,
    generates test cases (calls qa_test_agent AI), creates unit and integration tests,
    validates test syntax, runs complete test suites, verifies coverage thresholds,
    adds missing test cases, creates performance and security tests,
    generates test documentation, updates API documentation,
    creates/updates user guides and README files, generates changelog,
    creates migration guides, validates documentation links and completeness,
    commits and pushes changes, generates coverage report, updates documentation index.
  bash: ./.det-tools/scripts/ws_tests_docs.sh
  pwsh: ./.det-tools/scripts/WS-Tests-Docs.ps1
outputs:
  - .det-tools/out/ws_c_report.json
  - .det-tools/out/coverage_report.json
  - workstream-c branch with commits
success_criteria:
  - Test suites created and passing
  - Coverage thresholds met
  - Documentation complete and linked
  - Changelog generated
```

### **COMMAND: `vscode-validate-all`** [DETERMINISTIC]
```yaml
purpose: Universal IDE-based validation across all modified files
replaces_atoms:
  - range: atom_166..atom_190  # VS Code Universal Validation
    count: 25
implementation:
  script: |
    Aggregates all modified files from workstreams, initializes VS Code API context,
    loads appropriate language servers per file type, configures linting rules,
    performs comprehensive scan: syntax errors, type errors, import errors,
    formatting issues, security vulnerabilities, performance issues,
    accessibility compliance, naming conventions, documentation completeness,
    test associations. Applies auto-fixes for simple issues, flags complex problems,
    generates fix suggestions, applies automated corrections, re-validates,
    generates detailed validation report categorized by severity,
    routes complex fixes to appropriate agents, updates validation metrics.
  bash: ./.det-tools/scripts/vscode_validate_all.sh
  pwsh: ./.det-tools/scripts/VSCode-Validate-All.ps1
outputs: .det-tools/out/vscode_validation.json
success_criteria:
  - All critical errors fixed or flagged
  - Auto-fixable issues resolved
  - Comprehensive validation report generated
  - Files meet quality thresholds
  - JSON contains: {errors_fixed, warnings, suggestions, routing_decisions}
```

---

## PHASE 3: INTEGRATION & MERGE COORDINATION

### **COMMAND: `detect-resolve-conflicts`** [DETERMINISTIC]
```yaml
purpose: Automated conflict detection and resolution across workstreams
replaces_atoms:
  - range: atom_191..atom_210  # Conflict Detection & Resolution
    count: 20
implementation:
  script: |
    Initializes merge context, creates integration branch, analyzes changes from all workstreams,
    detects file overlaps and merge conflicts, categorizes conflict types (textual, semantic, structural),
    assesses severity, determines resolution strategy (auto vs manual),
    applies automatic resolution for simple conflicts, flags complex conflicts for human review,
    generates detailed conflict report with recommendations, applies manual resolutions when provided,
    validates merge integrity, updates merge documentation.
  bash: ./.det-tools/scripts/detect_resolve_conflicts.sh
  pwsh: ./.det-tools/scripts/Detect-Resolve-Conflicts.ps1
outputs: .det-tools/out/merge_conflicts.json
success_criteria:
  - All conflicts detected and categorized
  - Auto-resolvable conflicts fixed
  - Manual conflicts flagged with context
  - Merge integrity validated
  - JSON contains: {conflicts_auto_resolved, manual_review_needed, resolution_strategy}
```

### **COMMAND: `run-integration-tests`** [DETERMINISTIC]
```yaml
purpose: Comprehensive integration testing of merged codebase
replaces_atoms:
  - range: atom_211..atom_235  # Integration Testing
    count: 25
implementation:
  script: |
    Sets up isolated integration environment, deploys integrated changes,
    runs smoke tests for basic functionality, executes full integration test suite,
    tests API contracts and database integrity, verifies service interactions and data flows,
    checks error handling and edge cases, validates backward compatibility,
    tests configuration loading and security boundaries, runs performance benchmarks,
    verifies resource usage and concurrent operations, validates transaction integrity,
    tests rollback procedures, verifies monitoring integration and alert mechanisms,
    validates logging completeness, generates comprehensive integration report,
    assesses overall integration success and updates quality metrics.
  bash: ./.det-tools/scripts/run_integration_tests.sh
  pwsh: ./.det-tools/scripts/Run-Integration-Tests.ps1
outputs: 
  - .det-tools/out/integration_report.json
  - .det-tools/out/junit_integration.xml
success_criteria:
  - Smoke tests passing
  - Integration suite green
  - Performance benchmarks met
  - Security boundaries verified
  - Rollback tested successfully
```

### **COMMAND: `validate-quality-gates`** [DETERMINISTIC]
```yaml
purpose: Enforce quality thresholds before allowing merge
replaces_atoms:
  - range: atom_236..atom_250  # Quality Gate Validation
    count: 15
implementation:
  script: |
    Initializes quality gate checks against predefined thresholds,
    checks code coverage percentage, validates test pass rate,
    verifies performance benchmarks, checks security scan results,
    validates documentation coverage, verifies code complexity metrics,
    checks dependency vulnerabilities, validates accessibility standards,
    verifies licensing compliance, assesses technical debt impact,
    generates comprehensive quality report with pass/fail per gate,
    determines overall gate status, updates quality dashboard.
  bash: ./.det-tools/scripts/validate_quality_gates.sh
  pwsh: ./.det-tools/scripts/Validate-Quality-Gates.ps1
outputs: .det-tools/out/quality_gates.json
success_criteria:
  - All quality gates passing or explicitly waived
  - Coverage ≥ threshold
  - Security scans clean
  - Performance within limits
  - JSON contains: {gates_passed, gates_failed, thresholds, waivers}
```

### **COMMAND: `prepare-final-merge`** [DETERMINISTIC]
```yaml
purpose: Final merge preparation with rollback capability
replaces_atoms:
  - range: atom_251..atom_265  # Final Merge Preparation
    count: 15
implementation:
  script: |
    Creates final merge branch from integration branch, applies all validated changes,
    runs final validation suite (quick sanity checks), generates merge documentation,
    creates rollback snapshot/tag, prepares deployment artifacts,
    generates release notes from commits and changelog, updates version numbers,
    tags release candidate, notifies stakeholders, requests formal merge approval,
    validates approval received, prepares merge-to-main operation,
    updates merge tracking systems.
  bash: ./.det-tools/scripts/prepare_final_merge.sh
  pwsh: ./.det-tools/scripts/Prepare-Final-Merge.ps1
outputs:
  - .det-tools/out/merge_ready.json
  - Release notes and deployment artifacts
success_criteria:
  - Final validation passing
  - Rollback snapshot created
  - Approvals obtained
  - Documentation complete
  - Ready-to-merge flag set
```

---

## PHASE 4: PR CREATION & REVIEW

### PR Generation [AI MAKES DECISIONS] (15 atoms)
**Preserved as-is - requires AI for quality content generation**
```yaml
atom_266: analyze_change_summary | Role: planning_ai
atom_267: generate_pr_title | Role: docs_summarizer
atom_268: create_pr_description | Role: docs_summarizer
atom_269: summarize_modifications | Role: docs_summarizer
atom_270: list_affected_components | Role: docs_summarizer
atom_271: describe_testing_performed | Role: qa_test_agent
atom_272: document_performance_impact | Role: docs_summarizer
atom_273: note_breaking_changes | Role: docs_summarizer
atom_274: attach_validation_reports | Role: orchestrator
atom_275: link_related_issues | Role: orchestrator
atom_276: set_pr_metadata | Role: repo_ai
atom_277: configure_pr_settings | Role: repo_ai
atom_278: create_pull_request | Role: repo_ai
atom_279: update_pr_tracking | Role: orchestrator
atom_280: notify_reviewers | Role: orchestrator
```

### Automated Review [AI MAKES DECISIONS] (20 atoms)
**Preserved as-is - requires AI reasoning for code review**
```yaml
atom_281: initialize_review_context | Role: orchestrator
atom_282: perform_code_analysis | Role: thinking_ai
atom_283: check_coding_standards | Role: qa_test_agent
atom_284: review_architecture_changes | Role: thinking_ai
atom_285: assess_security_implications | Role: security_compliance
atom_286: evaluate_performance_changes | Role: thinking_ai
atom_287: review_test_coverage | Role: qa_test_agent
atom_288: check_documentation_updates | Role: docs_summarizer
atom_289: validate_dependency_changes | Role: planning_ai
atom_290: assess_maintainability | Role: thinking_ai
atom_291: review_error_handling | Role: resilience_agent
atom_292: check_logging_adequacy | Role: qa_test_agent
atom_293: evaluate_monitoring_coverage | Role: qa_test_agent
atom_294: assess_rollback_capability | Role: resilience_agent
atom_295: generate_review_feedback | Role: thinking_ai
atom_296: prioritize_review_findings | Role: planning_ai
atom_297: create_review_comments | Role: thinking_ai
atom_298: post_review_feedback | Role: orchestrator
atom_299: update_review_status | Role: orchestrator
atom_300: signal_review_complete | Role: orchestrator
```

### Human Review Gate [AI MAKES DECISIONS] (15 atoms)
**Preserved as-is - requires human judgment integration**
```yaml
atom_301: assess_human_review_need | Role: human_oversight
atom_302: prepare_review_materials | Role: docs_summarizer
atom_303: highlight_critical_changes | Role: planning_ai
atom_304: generate_decision_summary | Role: docs_summarizer
atom_305: request_human_review | Role: human_oversight
atom_306: track_review_progress | Role: orchestrator
atom_307: collect_human_feedback | Role: human_oversight
atom_308: interpret_review_decisions | Role: orchestrator
atom_309: apply_requested_changes | Role: work_cli_tools
atom_310: validate_change_application | Role: qa_test_agent
atom_311: update_pr_with_changes | Role: repo_ai
atom_312: notify_review_completion | Role: orchestrator
atom_313: validate_approval_status | Role: human_oversight
atom_314: update_approval_tracking | Role: orchestrator
atom_315: signal_human_review_done | Role: orchestrator
```

---

## PHASE 5: MERGE & DEPLOYMENT

### **COMMAND: `execute-final-merge`** [DETERMINISTIC]
```yaml
purpose: Execute protected merge with validation and notification
replaces_atoms:
  - range: atom_316..atom_330  # Final Merge Execution
    count: 15
implementation:
  script: |
    Validates all merge preconditions (CI status, approvals, quality gates),
    checks CI/CD pipeline status, verifies all required approvals obtained,
    creates merge commit with proper attribution, executes merge to main/master branch,
    verifies merge success and integrity, updates branch protection rules,
    tags merged commit with version, updates issue tracking systems,
    notifies stakeholders of merge completion, triggers deployment pipeline,
    archives PR artifacts and reports, updates merge metrics and analytics,
    cleans up temporary branches and worktrees.
  bash: ./.det-tools/scripts/execute_final_merge.sh
  pwsh: ./.det-tools/scripts/Execute-Final-Merge.ps1
outputs: .det-tools/out/merge_complete.json
success_criteria:
  - Merge to main successful
  - Version tagged
  - Stakeholders notified
  - Deployment triggered
  - Cleanup completed
```

### **COMMAND: `prepare-rollback`** [DETERMINISTIC]
```yaml
purpose: Comprehensive rollback preparation and testing
replaces_atoms:
  - range: atom_331..atom_340  # Rollback Preparation
    count: 10
implementation:
  script: |
    Creates detailed rollback plan with step-by-step procedures,
    identifies multiple rollback points (commit, deployment, data),
    prepares automated rollback scripts for each component,
    tests rollback procedures in isolated environment,
    documents rollback steps with timing and dependencies,
    configures automated rollback triggers based on metrics,
    sets up rollback monitoring and alerting,
    validates rollback readiness through dry-run,
    archives rollback artifacts for immediate access.
  bash: ./.det-tools/scripts/prepare_rollback.sh
  pwsh: ./.det-tools/scripts/Prepare-Rollback.ps1
outputs: .det-tools/out/rollback_plan.json
success_criteria:
  - Rollback procedures tested
  - Automated scripts ready
  - Triggers configured
  - Documentation complete
  - Dry-run successful
```

### **COMMAND: `post-merge-validation`** [DETERMINISTIC]
```yaml
purpose: Production validation and stability monitoring
replaces_atoms:
  - range: atom_341..atom_355  # Post-Merge Validation
    count: 15
implementation:
  script: |
    Initializes post-deployment monitoring, runs production smoke tests,
    verifies system stability metrics (error rates, latency, throughput),
    checks performance metrics against baselines, validates error rates within thresholds,
    monitors resource usage (CPU, memory, network), verifies data integrity,
    checks API availability and response times, validates critical user workflows,
    assesses overall deployment success, generates deployment report with metrics,
    updates deployment dashboard, notifies operations team,
    archives deployment logs and metrics.
  bash: ./.det-tools/scripts/post_merge_validation.sh
  pwsh: ./.det-tools/scripts/Post-Merge-Validation.ps1
outputs: .det-tools/out/deployment_report.json
success_criteria:
  - Smoke tests passing
  - System stability confirmed
  - Performance within limits
  - Error rates normal
  - User workflows functional
```

---

## PHASE 6: OBSERVABILITY & OPTIMIZATION

### **COMMAND: `collect-metrics`** [DETERMINISTIC]
```yaml
purpose: Comprehensive metrics collection across entire workflow
replaces_atoms:
  - range: atom_356..atom_370  # Metrics Collection
    count: 15
implementation:
  script: |
    Collects execution metrics from all phases, aggregates performance data,
    calculates total cost consumption by tool and agent,
    measures quality metrics (coverage, defect density, test pass rate),
    tracks tool usage patterns and success rates, monitors error frequencies and types,
    collects user feedback and satisfaction scores, measures cycle time per phase,
    tracks automation vs manual intervention rates, calculates overall success rates,
    aggregates security metrics, collects rollback statistics,
    measures review efficiency, tracks merge conflict rates and resolution time.
  bash: ./.det-tools/scripts/collect_metrics.sh
  pwsh: ./.det-tools/scripts/Collect-Metrics.ps1
outputs: .det-tools/out/metrics.json
success_criteria:
  - All metrics collected
  - Data aggregated by phase
  - Cost breakdown complete
  - Quality metrics calculated
```

### Analytics & Reporting [AI MAKES DECISIONS] (15 atoms)
**Preserved as-is - requires AI for insight generation**
```yaml
atom_371: analyze_workflow_patterns | Role: thinking_ai
atom_372: identify_bottlenecks | Role: thinking_ai
atom_373: assess_cost_efficiency | Role: cost_resource_manager
atom_374: evaluate_quality_trends | Role: qa_test_agent
atom_375: analyze_failure_patterns | Role: resilience_agent
atom_376: identify_optimization_opportunities | Role: thinking_ai
atom_377: generate_executive_summary | Role: docs_summarizer
atom_378: create_detailed_reports | Role: docs_summarizer
atom_379: generate_recommendations | Role: thinking_ai
atom_380: update_dashboards | Role: orchestrator
atom_381: distribute_reports | Role: orchestrator
atom_382: archive_analytics_data | Role: orchestrator
atom_383: update_historical_trends | Role: orchestrator
atom_384: notify_stakeholders | Role: orchestrator
atom_385: signal_reporting_complete | Role: orchestrator
```

### Continuous Improvement [AI MAKES DECISIONS] (15 atoms)
**Preserved as-is - requires AI for optimization strategies**
```yaml
atom_386: analyze_success_patterns | Role: thinking_ai
atom_387: identify_failure_causes | Role: resilience_agent
atom_388: optimize_routing_algorithms | Role: orchestrator
atom_389: refine_complexity_assessment | Role: thinking_ai
atom_390: improve_conflict_detection | Role: merge_coordinator
atom_391: enhance_quality_gates | Role: qa_test_agent
atom_392: optimize_tool_selection | Role: orchestrator
atom_393: improve_cost_predictions | Role: cost_resource_manager
atom_394: refine_rollback_procedures | Role: resilience_agent
atom_395: enhance_documentation_generation | Role: docs_summarizer
atom_396: update_workflow_templates | Role: orchestrator
atom_397: deploy_improvements | Role: orchestrator
atom_398: validate_improvement_impact | Role: qa_test_agent
atom_399: archive_optimization_data | Role: orchestrator
atom_400: finalize_workflow_completion | Role: orchestrator
```

---

## CROSS-CUTTING DETERMINISTIC COMMANDS

### **COMMAND: `lint-all`**
```yaml
purpose: Universal formatting, linting, and type checking
replaces_atoms:
  - atom_097, atom_098, atom_101, atom_102, atom_103
  - count: 5
  - context: Embedded in workstream execution but also standalone
implementation:
  script: |
    Runs language-specific formatters (black, prettier, etc.),
    applies import sorting, runs linters (flake8, eslint, etc.),
    performs static type checking (mypy, tsc), auto-fixes issues,
    generates lint report.
  bash: ./.det-tools/scripts/lint_all.sh
  pwsh: ./.det-tools/scripts/Lint-All.ps1
success_criteria: Zero critical diagnostics
```

### **COMMAND: `run-tests`**
```yaml
purpose: Unified test execution with fail-fast
replaces_atoms:
  - atom_104, atom_145, atom_146, atom_147
  - count: 4
  - context: Used in multiple workstreams
implementation:
  script: |
    Discovers and runs all test suites (unit, integration),
    fails fast on first error, generates JUnit XML output.
  bash: pytest -q --maxfail=1 --junitxml=.det-tools/out/junit.xml
  pwsh: ./.det-tools/scripts/Run-Tests.ps1
success_criteria: All tests passing or pipeline halts
```

### **COMMAND: `repo-flow`**
```yaml
purpose: Standardized git operations for any workstream
replaces_atoms:
  - atom_092, atom_110, atom_111, atom_117, atom_135, atom_136, atom_142
  - count: 7
  - context: Reusable across all workstreams
implementation:
  script: |
    Creates/checks out feature branch, stages all changes,
    commits with conventional message, pushes to remote,
    handles authentication and conflicts.
  bash: ./.det-tools/scripts/repo_flow.sh
  pwsh: ./.det-tools/scripts/Repo-Flow.ps1
success_criteria: Clean tree, signed commit, remote synchronized
```

### **COMMAND: `validate-config`**
```yaml
purpose: Configuration validation against schemas
replaces_atoms:
  - atom_118, atom_122, atom_124, atom_125, atom_126
  - count: 5
implementation:
  script: |
    Validates YAML/JSON against schemas, checks environment variables,
    tests configuration loading, verifies service connectivity.
  bash: ./.det-tools/scripts/validate_config.sh
  pwsh: ./.det-tools/scripts/Validate-Config.ps1
success_criteria: Schema-valid, env complete, services reachable
```

---

## COMMAND SUMMARY

### Deterministic Commands Created: 16
```yaml
Phase 0:
  - precheck (10 atoms)
  - init-moddoc (10 atoms)

Phase 1:
  - analyze-project (15 atoms - AI-assisted)
  - setup-workstreams (15 atoms)
  - assign-tools (10 atoms)

Phase 2:
  - exec-core-edits (25 atoms - AI-assisted)
  - exec-config-infra (25 atoms)
  - exec-tests-docs (25 atoms - AI-assisted)
  - vscode-validate-all (25 atoms)

Phase 3:
  - detect-resolve-conflicts (20 atoms)
  - run-integration-tests (25 atoms)
  - validate-quality-gates (15 atoms)
  - prepare-final-merge (15 atoms)

Phase 5:
  - execute-final-merge (15 atoms)
  - prepare-rollback (10 atoms)
  - post-merge-validation (15 atoms)

Phase 6:
  - collect-metrics (15 atoms)

Cross-cutting:
  - lint-all (5 atoms)
  - run-tests (4 atoms)
  - repo-flow (7 atoms)
  - validate-config (5 atoms)
```

### AI Decision Atoms Preserved: 90
- Entry Point Processing (10)
- Modification Planning (20)
- PR Generation (15)
- Automated Review (20)
- Human Review Gate (15)
- Analytics & Reporting (15)
- Continuous Improvement (15)

### Reduction Achieved
- **Original**: 400 atoms
- **Deterministic Commands**: 16 commands (replaces ~310 atoms)
- **AI Decision Points**: 90 atoms preserved
- **Reduction Ratio**: ~19:1 for deterministic sections

### Tool Assignment Remains Via `assign-tools` Command
All role-to-tool mappings are handled by the `assign-tools` command which reads from configuration and establishes fallback chains dynamically.