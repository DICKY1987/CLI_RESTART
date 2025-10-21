from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def _import_integration_manager():
    try:
        # Expect repo root on sys.path for src imports
        from integrations.integration_manager import IntegrationManager  # type: ignore

        return IntegrationManager
    except Exception:
        try:
            import sys
            from pathlib import Path

            root = Path(__file__).resolve().parents[4] / "src"
            if str(root) not in sys.path:
                sys.path.append(str(root))
            from integrations.integration_manager import (
                IntegrationManager,  # type: ignore
            )

            return IntegrationManager
        except Exception:
            return None


@dataclass
class WorkflowContextData:
    workflow_id: str
    name: str
    user_id: str | None = None
    jira_project: str | None = None
    slack_channel: str | None = None
    github_repo: str | None = None


class PlatformIntegrationsBridge:
    """Adapter to existing enterprise integrations (JIRA/Slack/GitHub/Teams)."""

    def __init__(self, config_file: str | None = None) -> None:
        IM = _import_integration_manager()
        self._mgr = IM(config_file) if IM else None

    async def initialize(self) -> None:
        if not self._mgr:
            return
        await self._mgr.initialize_integrations()

    async def notify_started(self, ctx: WorkflowContextData) -> None:
        if not self._mgr:
            return
        await self._mgr.notify_workflow_started(
            ctx.workflow_id,
            {
                "name": ctx.name,
                "user_id": ctx.user_id,
                "jira_project": ctx.jira_project,
                "slack_channel": ctx.slack_channel,
                "github_repo": ctx.github_repo,
            },
        )

    async def notify_progress(self, workflow_id: str, progress: dict[str, Any]) -> None:
        if not self._mgr:
            return
        await self._mgr.notify_workflow_progress(workflow_id, progress)

    async def notify_completed(self, workflow_id: str, result: dict[str, Any]) -> None:
        if not self._mgr:
            return
        await self._mgr.notify_workflow_completed(workflow_id, result)

    async def notify_failed(self, workflow_id: str, error: dict[str, Any]) -> None:
        if not self._mgr:
            return
        await self._mgr.notify_workflow_failed(workflow_id, error)
