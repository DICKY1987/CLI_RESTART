from __future__ import annotations

import datetime as dt
from typing import Any, Optional

from sqlalchemy import select

from src.db.connection import get_session
from src.db.models import Workstream


def create_workstream(name: str, metadata: Optional[dict[str, Any]] = None, correlation_id: Optional[str] = None) -> Workstream:
    with get_session() as session:
        ws = Workstream(name=name, status="pending", metadata=metadata, correlation_id=correlation_id)
        session.add(ws)
        session.flush()
        return ws


def update_status(workstream_id: int, status: str) -> Workstream:
    with get_session() as session:
        ws = session.get(Workstream, workstream_id)
        if ws is None:
            raise ValueError(f"Workstream {workstream_id} not found")
        ws.status = status
        ws.updated_at = dt.datetime.now(dt.timezone.utc)
        session.add(ws)
        session.flush()
        return ws


def get_workstream(workstream_id: int) -> Optional[Workstream]:
    with get_session() as session:
        return session.get(Workstream, workstream_id)


def list_workstreams(
    *,
    status: Optional[str] = None,
    start: Optional[dt.datetime] = None,
    end: Optional[dt.datetime] = None,
    correlation_id: Optional[str] = None,
) -> list[Workstream]:
    with get_session() as session:
        stmt = select(Workstream)
        if status:
            stmt = stmt.where(Workstream.status == status)
        if correlation_id:
            stmt = stmt.where(Workstream.correlation_id == correlation_id)
        if start:
            stmt = stmt.where(Workstream.created_at >= start)
        if end:
            stmt = stmt.where(Workstream.created_at <= end)
        return list(session.scalars(stmt).all())

