"""Slack notification backend."""

from __future__ import annotations

import os
from typing import Any

import requests


class SlackNotifier:
    """Send notifications to Slack."""

    def __init__(self, webhook_url: str | None = None):
        """Initialize Slack notifier.

        Args:
            webhook_url: Slack webhook URL (defaults to SLACK_WEBHOOK_URL env var)
        """
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        if not self.webhook_url:
            raise ValueError("Slack webhook URL not configured")

    def send(self, message: str, **kwargs: Any) -> bool:
        """Send message to Slack.

        Args:
            message: Message text
            **kwargs: Additional Slack message parameters

        Returns:
            True if sent successfully
        """
        payload: dict[str, Any] = {"text": message}
        payload.update(kwargs)

        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Failed to send Slack notification: {e}")
            return False

    def send_workflow_started(self, workflow_name: str):
        """Send workflow started notification."""
        return self.send(
            f":rocket: Workflow started: *{workflow_name}*",
            attachments=[{"color": "good", "text": f"Workflow: {workflow_name}"}],
        )

    def send_workflow_completed(self, workflow_name: str, duration: float):
        """Send workflow completed notification."""
        return self.send(
            f":white_check_mark: Workflow completed: *{workflow_name}*",
            attachments=[
                {
                    "color": "good",
                    "text": f"Workflow: {workflow_name}\nDuration: {duration:.2f}s",
                }
            ],
        )

    def send_workflow_failed(self, workflow_name: str, error: str):
        """Send workflow failed notification."""
        return self.send(
            f":x: Workflow failed: *{workflow_name}*",
            attachments=[
                {"color": "danger", "text": f"Workflow: {workflow_name}\nError: {error}"}
            ],
        )
