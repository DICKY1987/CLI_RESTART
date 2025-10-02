import pytest

from src.cli_multi_rapid.resilience.circuit_breaker import SimpleCircuitBreaker


def test_circuit_opens_after_failures(monkeypatch):
    cb = SimpleCircuitBreaker(failure_threshold=2, reset_timeout=1)

    def boom():
        raise RuntimeError("x")

    with pytest.raises(RuntimeError):
        cb.call(boom)
    with pytest.raises(RuntimeError):
        cb.call(boom)

    # Now should be open
    with pytest.raises(RuntimeError):
        cb.call(lambda: 1)

