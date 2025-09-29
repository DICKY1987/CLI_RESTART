from pathlib import Path

from src.cli_multi_rapid.workflow_runner import WorkflowRunner


def test_execute_via_router_dry_run(tmp_path: Path):
    wf = tmp_path / "wf_exec.yaml"
    wf.write_text(
        """
name: Exec Simplified
simplified: true
execute: true
operations:
  - id: 1
    type: plan
    complexity: 1
  - id: 2
    type: format
    complexity: 1
  - id: 3
    type: test
    complexity: 1
""".strip()
    )
    runner = WorkflowRunner()
    res = runner.run(workflow_file=wf, dry_run=True)
    assert res.success
    assert res.steps_completed == 3
