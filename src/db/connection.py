from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    data_dir = Path(".data")
    data_dir.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{(data_dir / 'registry.db').as_posix()}"


def create_db_engine() -> Engine:
    url = get_database_url()
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, echo=False, future=True, connect_args=connect_args)


ENGINE: Engine | None = None
SessionLocal: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    global ENGINE, SessionLocal
    if ENGINE is None:
        ENGINE = create_db_engine()
        SessionLocal = sessionmaker(bind=ENGINE, autocommit=False, autoflush=False, future=True)
    return ENGINE


@contextmanager
def get_session() -> Iterator[Session]:
    if SessionLocal is None:
        get_engine()
    assert SessionLocal is not None
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

