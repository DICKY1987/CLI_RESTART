from src.observability.tracing import init_tracing


def test_tracing_init_noop_without_deps():
    # Should not raise even if opentelemetry is not installed
    assert init_tracing(service_name="test-service") is None
