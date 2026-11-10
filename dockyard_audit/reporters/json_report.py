"""JSON serialization for audit findings."""

from __future__ import annotations

import json

from dockyard_audit.models import Finding, sort_findings


def render_json(findings: list[Finding]) -> str:
    """Serialize findings as stable, indented JSON."""
    payload = {
        "tool": "dockyard-audit",
        "version": 1,
        "summary": {
            "total": len(findings),
            "critical": sum(item.severity == "critical" for item in findings),
            "warning": sum(item.severity == "warning" for item in findings),
            "info": sum(item.severity == "info" for item in findings),
        },
        "findings": [item.to_dict() for item in sort_findings(findings)],
    }
    return json.dumps(payload, indent=2, sort_keys=False)
