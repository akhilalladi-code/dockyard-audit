# Contributing

Thanks for helping improve Dockyard Audit.

## Development setup

1. Install Python 3.10 or newer.
2. Clone the repository and create a virtual environment.
3. Run `pip install -e ".[dev]"`.
4. Run `pytest` and `ruff check .` before submitting changes.

## Guidelines

- Keep audits read-only; never mutate Docker resources.
- Give each rule a stable ID and severity.
- Explain risks and include practical remediation.
- Keep unit tests independent of a local Docker daemon.
- Cover normal, missing, malformed, and edge-case inputs.
- Avoid network access in unit tests.
- Keep errors actionable.

## Pull requests

Use conventional commit messages where practical: `feat:`, `fix:`, `test:`, `docs:`, and `ci:`. Describe the problem, approach, and validation performed.
