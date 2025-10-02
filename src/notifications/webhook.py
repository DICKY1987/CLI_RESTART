"""Webhook notification backend."""

from __future__ import annotations

import os
from typing import Dict, Any

import requests


class WebhookNotifier:
    """Send notifications via webhook."""

    def __init__(self, url: str | None = None):
        """Initialize webhook notifier."""
        self.url = url or os.getenv("WEBHOOK_URL")
        if not self.url:
            raise ValueError("Webhook URL not configured")

    def send(self, event: str, data: Dict[str, Any]) -> bool:
        """Send webhook notification."""
        payload = {"event": event, "data": data}

        try:
            response = requests.post(self.url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Failed to send webhook: {e}")
            return False

    def send_workflow_event(self, event_type: str, workflow_name: str, **kwargs: Any) -> bool:
        """Send workflow event."""
        return self.send(
            event=f"workflow.{event_type}",
            data={"workflow_name": workflow_name, **kwargs},
        )
