#!/usr/bin/env python3
"""Lightweight help output checks to prevent regressions."""

from typer.testing import CliRunner

from src.cli_multi_rapid.main import app


runner = CliRunner()


def test_root_help_contains_repo_group():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "repo" in result.stdout
    assert "run-ipt-wt" in result.stdout

