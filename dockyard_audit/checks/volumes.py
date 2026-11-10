"""Checks for live Docker volumes."""

from __future__ import annotations

from typing import Any

from dockyard_audit.models import Finding


def audit_volumes(volumes: list[Any], containers: list[Any]) -> list[Finding]:
    """Report volumes not referenced by the inspected container list."""
    attached: set[str] = set()
    for container in containers:
        attrs = getattr(container, "attrs", {}) or {}
        for mount in attrs.get("Mounts", []) or []:
            if mount.get("Name"):
                attached.add(str(mount["Name"]))
    findings: list[Finding] = []
    for volume in volumes:
        attrs = getattr(volume, "attrs", {}) or {}
        name = str(attrs.get("Name") or getattr(volume, "name", "unknown"))
        if name not in attached:
            findings.append(Finding(
                "VOLUME001", "info", name, "Volume not attached to inspected containers",
                "No container in the current Docker listing reports this volume as mounted.",
                "Confirm the volume is still needed before removing it; Dockyard never deletes volumes.",
            ))
    return findings
