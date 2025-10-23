# Contributing

Thanks for your interest in improving `cli_multi_rapid_DEV`!

## Quick start

1. Fork and clone the repo.
2. Create a virtual environment and install dev deps:
   - `pip install -e .`
   - `pip install -r requirements.txt` (optional extras for local tooling)
   - `pip install pre-commit`
   - `pre-commit install`
3. Run tests: `python -m unittest -v` or `pytest -q`.

## Development standards

- Keep changes focused and include tests for new behavior.
- Run formatting, linting, type checks, and tests locally before pushing.
- Ensure CI passes; coverage is gated at 85%.

## Code Quality and Error Handling

To maintain a high-quality and maintainable codebase, we have specific standards for code quality and error handling. All contributors are expected to follow these guidelines.

- **Code Quality:** Please read our [Code Quality Guide](docs/development/code-quality.md) to learn about our standards for code style, documentation, and dead code detection.
- **Error Handling:** All errors should be handled using our standardized exception and error code system. Please read our [Error Handling Guide](docs/development/error-handling.md) for details.

## Pull requests

- Describe the problem and solution clearly, referencing issues if applicable.
- Add user-facing notes to `README.md` when behavior changes.
- For security-sensitive changes, coordinate privately per `SECURITY.md`.
