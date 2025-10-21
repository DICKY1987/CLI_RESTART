from __future__ import annotations

"""
Role Manager for the simplified workflow system.

Provides a compact 5-role mapping with tool assignments and fallback chains
without impacting existing router behavior. Intended for use by the
SimplifiedRouter and the simplified workflow execution path.
"""



class RoleManager:
    """Manages roles, tools and fallbacks for simplified workflows."""

    def __init__(self) -> None:
        # Configuration-driven map; kept local and minimal for now.
        self._roles: dict[str, dict[str, object]] = {
            "planning_ai": {
                "primary_tool": "claude_code",
                "fallback_tools": ["gemini_cli", "local_llm"],
                "cost_tier": "premium",
                "responsibilities": [
                    "analyze_requests",
                    "create_plans",
                    "determine_resources",
                ],
            },
            "work_cli_tools": {
                "primary_tool": "aider",
                "fallback_tools": ["continue_vscode", "manual_editing"],
                "cost_tier": "standard",
                "responsibilities": [
                    "apply_modifications",
                    "refactoring",
                    "formatting",
                ],
            },
            "ide_validator": {
                "primary_tool": "vscode",
                "fallback_tools": ["language_servers", "static_analyzers"],
                "cost_tier": "free",
                "responsibilities": [
                    "syntax_checking",
                    "error_detection",
                    "quick_fixes",
                ],
            },
            "repo_coordinator": {
                "primary_tool": "github_cli",
                "fallback_tools": ["git_commands", "github_api"],
                "cost_tier": "free",
                "responsibilities": [
                    "git_operations",
                    "branch_management",
                    "pr_creation",
                ],
            },
            "orchestrator": {
                "primary_tool": "custom_scripts",
                "fallback_tools": ["github_actions", "manual_process"],
                "cost_tier": "free",
                "responsibilities": [
                    "workflow_coordination",
                    "state_management",
                    "cost_tracking",
                ],
            },
        }

        # Minimal operation→role mapping for common operation kinds
        self._operation_role_map: dict[str, str] = {
            "plan": "planning_ai",
            "analyze": "planning_ai",
            "design": "planning_ai",
            "edit": "work_cli_tools",
            "modify": "work_cli_tools",
            "refactor": "work_cli_tools",
            "format": "work_cli_tools",
            "validate": "ide_validator",
            "lint": "ide_validator",
            "typecheck": "ide_validator",
            "test": "ide_validator",
            "commit": "repo_coordinator",
            "branch": "repo_coordinator",
            "pr": "repo_coordinator",
            "coordinate": "orchestrator",
            "track_costs": "orchestrator",
        }

    def get_role_for_operation(self, operation_type: str) -> str:
        """Return role name for a given operation type, defaulting to work_cli_tools."""
        key = (operation_type or "").strip().lower()
        return self._operation_role_map.get(key, "work_cli_tools")

    def get_tools_for_role(self, role_name: str) -> list[str]:
        cfg = self._roles.get(role_name, {})
        tools: list[str] = []
        primary = cfg.get("primary_tool")
        if isinstance(primary, str):
            tools.append(primary)
        fallbacks = cfg.get("fallback_tools")
        if isinstance(fallbacks, list):
            tools.extend(str(x) for x in fallbacks)
        return tools

    def get_fallback_chain(self, role_name: str) -> list[str]:
        cfg = self._roles.get(role_name, {})
        chain = []
        primary = cfg.get("primary_tool")
        if isinstance(primary, str):
            chain.append(primary)
        fallbacks = cfg.get("fallback_tools")
        if isinstance(fallbacks, list):
            chain.extend(str(x) for x in fallbacks)
        return chain

    def check_tool_availability(self, tool_name: str) -> bool:
        # Lightweight availability check; for now assume all named tools are callable
        # via existing adapters or external CLIs orchestrated by higher layers.
        return bool(tool_name)
