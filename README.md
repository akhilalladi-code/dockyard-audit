# Dockyard Audit

Read-only Docker environment auditor for Compose files and live Docker Engine resources.

## Install

```bash
git clone https://github.com/akhilalladi-code/dockyard-audit.git
cd dockyard-audit
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Python 3.10+. Compose auditing works without a Docker daemon.

## Usage

```bash
dockyard compose ./docker-compose.yml
dockyard docker
dockyard audit --compose ./compose.yaml --docker
dockyard compose ./compose.yaml --format json --output report.json
dockyard compose ./compose.yaml --fail-on warning
```

## Checks

Compose rules detect missing restart policy, root user configuration, privileged mode, host networking, Docker socket mounts, mutable image references, missing healthchecks, and added capabilities. Live checks inspect container restart/privilege/network settings, latest-tagged images, and unattached volumes.

## Safety

Dockyard performs read-only inspection. It never starts, stops, deletes, rebuilds, or modifies Docker resources. Findings are conservative indicators, not a security certification. See [docs/rules.md](docs/rules.md).

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
```

## Screenshots

Add genuine terminal captures after running Dockyard in your environment; screenshots are not fabricated.

## License

MIT. See [LICENSE](LICENSE).
