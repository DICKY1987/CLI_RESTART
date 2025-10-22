from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Session:
    id: str
    title: str
    cwd: str | None = None


class SessionManager:
    """Minimal session lifecycle manager (stub)."""

    def __init__(self) -> None:
        self.sessions: dict[str, Session] = {}

    def create(self, session_id: str, title: str, cwd: str | None = None) -> Session:
        sess = Session(id=session_id, title=title, cwd=cwd)
        self.sessions[session_id] = sess
        return sess

    def get(self, session_id: str) -> Session | None:
        return self.sessions.get(session_id)

    def remove(self, session_id: str) -> None:
        self.sessions.pop(session_id, None)
