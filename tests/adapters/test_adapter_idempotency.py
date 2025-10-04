from typing import Any, Dict, Optional

from src.cli_multi_rapid.workflow_runner import WorkflowRunner


class _DummyAdapter:
    def __init__(self):
        self.adapter_type = type("T", (), {"value": "deterministic"})()
        self._count = 0

    def get_metadata(self) -> Dict[str, Any]:
        return {"adapter_type": "deterministic"}

    def validate_step(self, step: Dict[str, Any]) -> bool:
        return True

    def execute(self, step: Dict[str, Any], context: Optional[Dict[str, Any]] = None, files: Optional[str] = None):
        self._count += 1
        return type("R", (), {"success": True, "to_dict": lambda s: {"success": True, "output": f"run-{self._count}"}})()


class _DummyRegistry:
    def __init__(self, adapter):
        self._adapter = adapter

    def get_adapter(self, name: str):
        return self._adapter


class _DummyRouter:
    def __init__(self, adapter):
        self.registry = _DummyRegistry(adapter)


def test_runner_uses_cached_result(monkeypatch):
    runner = WorkflowRunner()
    adapter = _DummyAdapter()
    runner.router = _DummyRouter(adapter)
    step = {"id": "x", "actor": "dummy", "with": {}}

    r1 = runner._execute_step(step)
    assert r1["success"] is True
    assert r1["output"].startswith("run-1")

    # Second run should return cached output (not incrementing counter)
    r2 = runner._execute_step(step)
    assert r2["success"] is True
    assert r2["output"].startswith("run-1")

    # Force flag bypasses cache
    step_force = {"id": "x", "actor": "dummy", "with": {"force": True}}
    r3 = runner._execute_step(step_force)
    assert r3["output"].startswith("run-2")
