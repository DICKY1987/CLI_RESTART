from __future__ import annotations

import datetime as dt
from types import SimpleNamespace
from typing import Any, Optional

from sqlalchemy import select

from src.db.connection import get_engine, get_session
from src.db.models import Workstream


def create_workstream(
    name: str,
    metadata: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
) -> Workstream:
    with get_session() as session:
        # Map provided 'metadata' to ORM attribute 'meta' (column name is 'metadata').
        ws = Workstream(name=name, status="pending", meta=metadata, correlation_id=correlation_id)
        session.add(ws)
        session.flush()
        # Access PK to ensure it's loaded, then detach so attributes remain accessible
        _ = ws.id  # load primary key
        # Return a plain, detached copy for safe attribute access after session closes
        plain = SimpleNamespace(
            id=ws.id,
            name=ws.name,
            status=ws.status,
            created_at=ws.created_at,
            updated_at=ws.updated_at,
            meta=ws.meta,
            correlation_id=ws.correlation_id,
        )
        # For SQLite on Windows, dispose engine to release file handle for tests
        try:
            get_engine().dispose()
        except Exception:
            pass
        return plain


def update_status(workstream_id: int, status: str) -> Workstream:
    with get_session() as session:
        ws = session.get(Workstream, workstream_id)
        if ws is None:
            raise ValueError(f"Workstream {workstream_id} not found")
        ws.status = status
        ws.updated_at = dt.datetime.now(dt.timezone.utc)
        session.add(ws)
        session.flush()
        return SimpleNamespace(
            id=ws.id,
            name=ws.name,
            status=ws.status,
            created_at=ws.created_at,
            updated_at=ws.updated_at,
            meta=ws.meta,
            correlation_id=ws.correlation_id,
        )


def get_workstream(workstream_id: int) -> Optional[Workstream]:
    with get_session() as session:
        ws = session.get(Workstream, workstream_id)
        if ws is None:
            return None
        return SimpleNamespace(
            id=ws.id,
            name=ws.name,
            status=ws.status,
            created_at=ws.created_at,
            updated_at=ws.updated_at,
            meta=ws.meta,
            correlation_id=ws.correlation_id,
        )


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
        results = list(session.scalars(stmt).all())
        return [
            SimpleNamespace(
                id=r.id,
                name=r.name,
                status=r.status,
                created_at=r.created_at,
                updated_at=r.updated_at,
                meta=r.meta,
                correlation_id=r.correlation_id,
            )
            for r in results
        ]
