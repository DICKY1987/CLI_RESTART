from pathlib import Path
from typer.testing import CliRunner

from src.cli_multi_rapid.main import app


def test_multi_step_workflow(tmp_path: Path, monkeypatch):
    runner = CliRunner()
    wf_src = Path('tests/e2e/fixtures/multi_step.yaml')
    wf = tmp_path / 'workflow.yaml'
    wf.write_text(wf_src.read_text(), encoding='utf-8')

    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["run", str(wf)])
    assert res.exit_code == 0
    assert (tmp_path / 'artifacts' / 'e2e' / 'snapshot.json').exists()
    assert (tmp_path / 'artifacts' / 'e2e' / 'analysis2.json').exists()