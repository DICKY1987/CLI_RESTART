import json
from pathlib import Path
from typer.testing import CliRunner

from src.cli_multi_rapid.main import app


def test_full_workflow_execution(tmp_path: Path, monkeypatch):
    runner = CliRunner()
    # Copy sample workflow to tmp
    wf_src = Path('tests/e2e/fixtures/simple_linear.yaml')
    wf = tmp_path / 'workflow.yaml'
    wf.write_text(wf_src.read_text(), encoding='utf-8')

    # Ensure artifacts path resolves under tmp
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["run", str(wf), "--dry-run"])
    # In dry-run, execution should succeed
    assert result.exit_code == 0

    # Now run real (non-dry-run) to produce artifacts
    result2 = runner.invoke(app, ["run", str(wf)])
    assert result2.exit_code in (0,)
    out_art = tmp_path / 'artifacts' / 'e2e' / 'analysis.json'
    assert out_art.exists()
    # Validate it is JSON
    json.loads(out_art.read_text(encoding='utf-8'))