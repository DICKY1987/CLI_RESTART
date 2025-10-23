#!/usr/bin/env python3
"""Run targeted security tests with coverage enforced via coverage.py."""

from __future__ import annotations

import argparse
import sys
from io import StringIO
from pathlib import Path
from typing import Iterable, List

import pytest
from coverage import Coverage


def main(argv: Iterable[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--junit", required=True)
    parser.add_argument("--coverage-xml", required=True)
    parser.add_argument("--coverage-text", required=True)
    parser.add_argument(
        "tests",
        nargs="*",
        default=[
            "tests/unit/test_security_rbac.py",
            "tests/unit/test_security_auth.py",
        ],
        help="Specific test paths to execute.",
    )
    args = parser.parse_args(list(argv))

    repo_root = Path(args.repo_root).resolve()
    junit_path = Path(args.junit).resolve()
    coverage_xml_path = Path(args.coverage_xml).resolve()
    coverage_text_path = Path(args.coverage_text).resolve()

    for target in (junit_path, coverage_xml_path, coverage_text_path):
        target.parent.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(repo_root / "src"))

    tests = [str(Path(test)) for test in args.tests]

    coverage = Coverage(
        config_file=False,
        include=[
            str(repo_root / "src/cli_multi_rapid/security/auth.py"),
            str(repo_root / "src/cli_multi_rapid/security/rbac.py"),
        ],
        branch=True,
    )

    coverage.start()
    exit_code = pytest.main(
        [
            "-p",
            "no:cov",
            "--override-ini",
            "addopts=",
            "--junitxml",
            str(junit_path),
            *tests,
        ]
    )
    coverage.stop()
    coverage.save()

    coverage.xml_report(outfile=str(coverage_xml_path))

    report_stream = StringIO()
    percent_covered = coverage.report(file=report_stream)
    coverage_text_path.write_text(report_stream.getvalue(), encoding="utf-8")

    if percent_covered < 85.0 and exit_code == 0:
        return 1

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
