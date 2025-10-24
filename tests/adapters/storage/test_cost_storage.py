from pathlib import Path

from src.cli_multi_rapid.adapters.storage.cost_storage import FileCostStorage


def test_file_cost_storage_roundtrip(temp_dir):
    logs = temp_dir / "logs"
    storage = FileCostStorage(logs_dir=logs)

    rec1 = {"timestamp": "2025-10-24T01:02:03", "operation": "op", "tokens_used": 10, "estimated_cost": 0.1}
    rec2 = {"timestamp": "2025-10-24T04:05:06", "operation": "op2", "tokens_used": 5, "estimated_cost": 0.05}

    storage.save(rec1)
    storage.save(rec2)

    all_list = list(storage.iter_all())
    assert len(all_list) == 2
    # Filter by date
    from datetime import date

    by_date = list(storage.iter_by_date(date(2025, 10, 24)))
    assert len(by_date) == 2

