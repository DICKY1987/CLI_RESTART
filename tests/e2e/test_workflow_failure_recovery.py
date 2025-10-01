import pytest
from pathlib import Path
from typer.testing import CliRunner

from src.cli_multi_rapid.main import app


def test_workflow_failure_recovery(tmp_path: Path, monkeypatch):
    runner = CliRunner()
    # Define a workflow that references an unknown actor to force failure
    wf = tmp_path / 'bad.yaml'
    wf.write_text('name: bad\nversion: 1\nsteps:\n  - id: s1\n    name: bad\n    actor: does_not_exist\n', encoding='utf-8')
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["run", str(wf)])
    assert res.exit_code != 0