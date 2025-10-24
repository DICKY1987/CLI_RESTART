#!/usr/bin/env python3
"""
Integration Test Runner

Runs all integration tests with appropriate markers and generates a report.
"""

import subprocess
import sys
from pathlib import Path


def run_integration_tests(verbose: bool = True, markers: str = "integration"):
    """
    Run integration tests with pytest.

    Args:
        verbose: Enable verbose output
        markers: Pytest markers to filter tests (default: "integration")
    """
    test_dir = Path(__file__).parent
    project_root = test_dir.parent.parent

    # Build pytest command
    cmd = [
        "pytest",
        str(test_dir),
        "-m", markers,
        "--tb=short",
        "--color=yes",
    ]

    if verbose:
        cmd.append("-v")

    # Add coverage if requested
    if "--cov" in sys.argv:
        cmd.extend([
            "--cov=src/cli_multi_rapid",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])

    print(f"Running integration tests from: {test_dir}")
    print(f"Command: {' '.join(cmd)}\n")

    # Run tests
    result = subprocess.run(cmd, cwd=project_root)

    return result.returncode


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Run integration tests")
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "-m", "--markers",
        default="integration",
        help="Pytest markers to filter tests (default: integration)"
    )
    parser.add_argument(
        "--cov",
        action="store_true",
        help="Generate coverage report"
    )

    args = parser.parse_args()

    # Add --cov to sys.argv if requested
    if args.cov and "--cov" not in sys.argv:
        sys.argv.append("--cov")

    exit_code = run_integration_tests(
        verbose=args.verbose,
        markers=args.markers
    )

    if exit_code == 0:
        print("\n✅ All integration tests passed!")
    else:
        print(f"\n❌ Integration tests failed with exit code: {exit_code}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
