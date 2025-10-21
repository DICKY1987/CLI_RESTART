from __future__ import annotations

"""
Simplified decision-matrix router for 25-operation workflows.

Uses RoleManager to map operations to roles, then selects a primary tool
with graceful fallback when unavailable. Provides basic cost estimation
to integrate with the existing CostTracker.
"""


from ..roles.role_manager import RoleManager


class SimplifiedRouter:
    def __init__(self) -> None:
        self.roles = RoleManager()

    def route_operation(
        self, operation: dict[str, object], complexity_score: int | None = None
    ) -> str:
        op_type = str(operation.get("type", "edit")).lower()
        role = self.roles.get_role_for_operation(op_type)
        return self.apply_decision_matrix(op_type, role, operation, complexity_score)

    def apply_decision_matrix(
        self,
        operation_type: str,
        role_name: str,
        operation: dict[str, object],
        complexity_score: int | None,
    ) -> str:
        # Inputs to drive decision: file_count, file_size, complexity
        file_count = int(operation.get("file_count", 1) or 1)
        file_size = int(operation.get("file_size_kb", 1) or 1)
        cx = int(
            complexity_score
            if complexity_score is not None
            else operation.get("complexity", 1) or 1
        )

        chain = self.roles.get_fallback_chain(role_name)
        # Simple selection logic: prefer primary for low/moderate complexity; use first fallback for larger ops
        if cx <= 2 and file_count <= 5 and file_size <= 256:
            preferred = chain[0] if chain else "aider"
        elif cx <= 4 and file_count <= 20 and file_size <= 1024:
            preferred = chain[0] if chain else "aider"
        else:
            preferred = chain[1] if len(chain) > 1 else (chain[0] if chain else "aider")

        # Ensure availability; if not, walk the chain
        return self.check_fallback_availability(preferred, chain)

    def check_fallback_availability(
        self, primary_tool: str, chain: list | None = None
    ) -> str:
        chain = chain or [primary_tool]
        for tool in chain:
            if self.roles.check_tool_availability(tool):
                return tool
        # last resort
        return primary_tool

    def estimate_operation_cost(self, operation: dict[str, object], tool: str) -> float:
        # Crude token estimate based on complexity and file size
        cx = int(operation.get("complexity", 1) or 1)
        file_count = int(operation.get("file_count", 1) or 1)
        file_size = int(operation.get("file_size_kb", 1) or 1)
        base = 200  # base tokens per op
        size_factor = min(file_size / 64.0, 20.0)
        count_factor = min(file_count / 3.0, 10.0)
        tool_factor = 1.0 if tool in {"aider", "vscode"} else 1.5
        return float(
            int(base * (1 + cx * 0.5 + size_factor + count_factor) * tool_factor)
        )
