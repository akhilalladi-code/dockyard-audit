"""Shared data models for audit results."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

Severity = Literal["critical", "warning", "info"]
SEVERITY_ORDER: dict[str, int] = {"critical": 0, "warning": 1, "info": 2}


@dataclass(frozen=True, slots=True)
class Finding:
    """A single actionable audit observation."""

    rule_id: str
    severity: Severity
    resource: str
    title: str
    detail: str
    remediation: str

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-safe representation."""
        return asdict(self)


def sort_findings(findings: list[Finding]) -> list[Finding]:
    """Sort findings by severity, rule and resource."""
    return sorted(findings, key=lambda item: (
        SEVERITY_ORDER[item.severity], item.rule_id, item.resource
    ))
