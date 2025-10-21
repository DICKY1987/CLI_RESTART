from __future__ import annotations

from .automated_merge_strategy import AutomatedMergeStrategy, ConflictAnalysis
from .automated_merge_strategy import MergeStrategy as _AMSStrategyEnum


class MergeStrategy:
    """Stable facade delegating to AutomatedMergeStrategy."""

    def __init__(self) -> None:
        self._impl = AutomatedMergeStrategy()

    async def analyze(self, base_branch: str, feature_branch: str) -> ConflictAnalysis:
        return await self._impl.analyze_merge_conflicts(base_branch, feature_branch)

    async def select(self, analysis: ConflictAnalysis) -> tuple[str, _AMSStrategyEnum]:
        return await self._impl.select_optimal_merge_tool(analysis)

    async def execute(
        self,
        tool: str,
        strategy: _AMSStrategyEnum,
        analysis: ConflictAnalysis,
        base_branch: str,
        feature_branch: str,
    ) -> dict:
        return await self._impl.execute_merge(
            tool, strategy, analysis, base_branch, feature_branch
        )
