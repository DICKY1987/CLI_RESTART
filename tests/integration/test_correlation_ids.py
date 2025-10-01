from src.observability.correlation import new_correlation_id, get_correlation_id, bind_correlation_id


def test_correlation_id_generation_and_binding():
    cid = new_correlation_id()
    assert cid
    assert get_correlation_id() == cid
    # Rebind
    bind_correlation_id("abc123")
    assert get_correlation_id() == "abc123"