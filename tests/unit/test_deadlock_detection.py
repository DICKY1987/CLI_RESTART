from src.cli_multi_rapid.coordination.deadlock_detector import detect_deadlock


def test_cycle_detection() -> None:
    graph = {"a": {"b"}, "b": {"c"}, "c": {"a"}}
    report = detect_deadlock(graph, {"a": 0.0, "b": 0.0, "c": 0.0}, timeout_seconds=999999)
    assert report.cycle_detected is True


def test_timeout_detection() -> None:
    import time

    now = time.time()
    graph = {"a": set()}
    report = detect_deadlock(graph, {"a": now - 10}, timeout_seconds=1)
    assert "a" in report.timed_out

