"""
Nox configuration (consolidated)

WS-F: Keep ONLY multi-Python version testing sessions.
"""

import nox

# Python versions to test
PYTHON_VERSIONS = ["3.11", "3.12"]


@nox.session(python=PYTHON_VERSIONS)
def tests(session):
    """Run the Python test suite across supported versions."""
    # Install project with test extras defined in pyproject.toml
    session.install("-e", ".[test]")
    # Execute pytest with coverage
    session.run(
        "pytest",
        "--cov=src",
        "--cov-report=term-missing",
        "tests/",
    )

