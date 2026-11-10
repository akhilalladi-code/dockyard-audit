"""Compose file loading and validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ComposeConfigError(ValueError):
    """Raised when a Compose file cannot be safely parsed."""


def load_compose(path: Path) -> dict[str, Any]:
    """Load a Compose YAML file and return its document mapping."""
    if not path.exists():
        raise ComposeConfigError(f"Compose file does not exist: {path}")
    if not path.is_file():
        raise ComposeConfigError(f"Compose path is not a file: {path}")
    try:
        with path.open("r", encoding="utf-8") as handle:
            document = yaml.safe_load(handle)
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ComposeConfigError(f"Could not read Compose file: {exc}") from exc
    if document is None:
        raise ComposeConfigError("Compose file is empty.")
    if not isinstance(document, dict):
        raise ComposeConfigError("Compose document must be a YAML mapping.")
    services = document.get("services")
    if not isinstance(services, dict) or not services:
        raise ComposeConfigError("Compose file must define a non-empty 'services' mapping.")
    for name, service in services.items():
        if not isinstance(name, str) or not isinstance(service, dict):
            raise ComposeConfigError("Every service must have a name and a YAML mapping.")
    return document
