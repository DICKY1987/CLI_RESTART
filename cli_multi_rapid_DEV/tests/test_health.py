from src.health import status


def test_status_ok():
    assert status() == "ok"

