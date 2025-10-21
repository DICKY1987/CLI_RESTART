from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum

from .connection_manager import ConnectionManager


class EventType(str, Enum):
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_PROGRESS = "workflow_progress"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    SYSTEM_HEALTH = "system_health"
    NOTIFICATION = "notification"
    ERROR_RECOVERY = "error_recovery"
    COST_ALERT = "cost_alert"


@dataclass
class WorkflowEvent:
    event_type: EventType
    workflow_id: str | None
    timestamp: dt.datetime
    data: dict


# Module-level manager to allow tests to patch
connection_manager = ConnectionManager("redis://local")


class EventBroadcaster:
    def __init__(self, redis_url: str | None = None) -> None:
        self.redis_url = redis_url
        self.event_history: list[WorkflowEvent] = []

    def _record(self, event: WorkflowEvent) -> None:
        self.event_history.append(event)

    async def broadcast_workflow_started(self, workflow_id: str, data: dict) -> int:
        event = WorkflowEvent(EventType.WORKFLOW_STARTED, workflow_id, dt.datetime.now(), data)
        self._record(event)
        return await connection_manager.broadcast_to_topic("workflow.events", {
            "type": EventType.WORKFLOW_STARTED.value,
            "workflow_id": workflow_id,
            "data": data,
        })

    async def broadcast_workflow_progress(self, workflow_id: str, data: dict) -> int:
        event = WorkflowEvent(EventType.WORKFLOW_PROGRESS, workflow_id, dt.datetime.now(), data)
        self._record(event)
        return await connection_manager.broadcast_to_topic("workflow.events", {
            "type": EventType.WORKFLOW_PROGRESS.value,
            "workflow_id": workflow_id,
            "data": data,
        })

    async def broadcast_workflow_completed(self, workflow_id: str, data: dict) -> int:
        event = WorkflowEvent(EventType.WORKFLOW_COMPLETED, workflow_id, dt.datetime.now(), data)
        self._record(event)
        return await connection_manager.broadcast_to_topic("workflow.events", {
            "type": EventType.WORKFLOW_COMPLETED.value,
            "workflow_id": workflow_id,
            "data": data,
        })

    async def broadcast_workflow_failed(self, workflow_id: str, data: dict) -> int:
        event = WorkflowEvent(EventType.WORKFLOW_FAILED, workflow_id, dt.datetime.now(), data)
        self._record(event)
        return await connection_manager.broadcast_to_topic("workflow.events", {
            "type": EventType.WORKFLOW_FAILED.value,
            "workflow_id": workflow_id,
            "data": data,
        })

    async def broadcast_system_health(self, data: dict) -> int:
        event = WorkflowEvent(EventType.SYSTEM_HEALTH, None, dt.datetime.now(), data)
        self._record(event)
        return await connection_manager.broadcast_to_all({
            "type": EventType.SYSTEM_HEALTH.value,
            "data": data,
        })

    async def broadcast_notification(self, message: str, level: str = "info") -> int:
        event = WorkflowEvent(EventType.NOTIFICATION, None, dt.datetime.now(), {"message": message, "level": level})
        self._record(event)
        return await connection_manager.broadcast_to_all({
            "type": EventType.NOTIFICATION.value,
            "message": message,
            "level": level,
        })

    async def broadcast_error_recovery(self, error_code: str, resolution: str, data: dict | None = None) -> int:
        payload = {"error_code": error_code, "resolution": resolution}
        if data:
            payload.update(data)
        event = WorkflowEvent(EventType.ERROR_RECOVERY, None, dt.datetime.now(), payload)
        self._record(event)
        return await connection_manager.broadcast_to_all({
            "type": EventType.ERROR_RECOVERY.value,
            **payload,
        })

    async def broadcast_cost_alert(self, model: str, data: dict) -> int:
        event = WorkflowEvent(EventType.COST_ALERT, None, dt.datetime.now(), {"model": model, **data})
        self._record(event)
        return await connection_manager.broadcast_to_all({
            "type": EventType.COST_ALERT.value,
            "model": model,
            **data,
        })

    def get_recent_events(
        self,
        *,
        workflow_id: str | None = None,
        event_type: EventType | None = None,
        limit: int = 100,
    ) -> list[WorkflowEvent]:
        events = self.event_history
        if workflow_id is not None:
            events = [e for e in events if e.workflow_id == workflow_id]
        if event_type is not None:
            events = [e for e in events if e.event_type == event_type]
        return events[-limit:]

