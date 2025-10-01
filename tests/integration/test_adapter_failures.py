import json
from pathlib import Path

import pytest


def test_adapter_failures(monkeypatch, tmp_path: Path):
    # Simulate missing adapter by crafting workflow
    wf = tmp_path / 'wf.yaml'
    wf.write_text('name: x\nversion: 1\nsteps:\n  - id: s1\n    name: bad\n    actor: no_such_adapter\n', encoding='utf-8')

    from typer.testing import CliRunner
    from src.cli_multi_rapid.main import app

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    res = runner.invoke(app, ["run", str(wf)])
    assert res.exit_code != 0