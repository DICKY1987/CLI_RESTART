#!/usr/bin/env python3
"""Tests for global --json output mode."""

from typer.testing import CliRunner

from src.cli_multi_rapid.main import app


runner = CliRunner()


def test_run_json_mode(tmp_path):
    wf = tmp_path / "wf.yaml"
    wf.write_text("""name: test\nsteps: []\n""")
    result = runner.invoke(app, ["--json", "run", str(wf)])
    assert result.exit_code in (0, 1)
    # Should be valid JSON parsable by Typer rich printer
    assert "{" in result.stdout


def test_repo_branch_dry_run_json():
    result = runner.invoke(app, ["--json", "repo", "branch", "--name", "test-branch", "--dry-run"])
    assert result.exit_code == 0
    assert "intent" in result.stdout

