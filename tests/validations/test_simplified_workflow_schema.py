from pathlib import Path

from src.cli_multi_rapid.workflow_runner import WorkflowRunner


def test_simplified_workflow_validates_and_dry_runs(tmp_path: Path):
    wf = tmp_path / "wf.yaml"
    wf.write_text(
        """
name: Test Simplified
simplified: true
operations:
  - id: 1
    type: plan
    complexity: 1
  - id: 2
    type: edit
    complexity: 2
""".strip()
    )
    runner = WorkflowRunner()
    res = runner.run(workflow_file=wf, dry_run=True)
    assert res.success
    # completed operations should equal the number of operations in dry run
    assert res.steps_completed == 2
