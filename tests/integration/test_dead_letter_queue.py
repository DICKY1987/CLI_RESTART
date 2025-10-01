from src.cli_multi_rapid.resilience.dlq import FileDLQ


def test_dlq_add_and_list(tmp_path):
    dlq = FileDLQ(tmp_path / "dlq.json")
    dlq.add("wf1", "failure")
    items = dlq.list()
    assert len(items) == 1
    assert items[0].workflow == "wf1"

