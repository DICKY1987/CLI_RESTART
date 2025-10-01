import time as _time
from datetime import datetime as _dt
import pytest


@pytest.fixture
def frozen_time(monkeypatch):
    fixed = 1735689600.0  # 2025-01-01T00:00:00Z

    def fake_time():
        return fixed

    class FakeDatetime(_dt):
        @classmethod
        def now(cls, tz=None):
            return _dt.fromtimestamp(fixed, tz)

        @classmethod
        def utcnow(cls):
            return _dt.utcfromtimestamp(fixed)

    monkeypatch.setattr('time.time', fake_time)
    monkeypatch.setattr('datetime.datetime', FakeDatetime)
    yield