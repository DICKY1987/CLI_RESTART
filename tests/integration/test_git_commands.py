#!/usr/bin/env python3
"""Basic integration tests for git CLI commands in dry-run mode."""

from typer.testing import CliRunner

from src.cli_multi_rapid.main import app


runner = CliRunner()


def test_repo_init_dry_run():
    result = runner.invoke(app, ["--json", "repo", "init", "--dry-run"])
    assert result.exit_code == 0
    assert "git init" in result.stdout


def test_repo_commit_dry_run():
    result = runner.invoke(app, ["--json", "repo", "commit", "-m", "test", "--dry-run"])
    assert result.exit_code == 0
    assert "commit" in result.stdout


def test_repo_pr_dry_run():
    result = runner.invoke(app, ["--json", "repo", "pr", "--title", "DX PR", "--dry-run"])
    assert result.exit_code == 0
    assert "open_pr" in result.stdout

