"""Checks for live Docker containers."""

from __future__ import annotations

from typing import Any

from dockyard_audit.models import Finding


def audit_containers(containers: list[Any]) -> list[Finding]:
    """Inspect listed containers without changing their state."""
    findings: list[Finding] = []
    for container in containers:
        attrs = getattr(container, "attrs", {}) or {}
        host = attrs.get("HostConfig", {}) or {}
        name = str(attrs.get("Name") or getattr(container, "name", "unknown")).lstrip("/")
        state = (attrs.get("State") or {}).get("Status", "unknown")
        if state == "running":
            restart = host.get("RestartPolicy", {}) or {}
            if not restart.get("Name") or restart.get("Name") == "no":
                findings.append(Finding(
                    "CONTAINER001", "warning", name, "No restart policy configured",
                    "The running container has no effective restart policy.",
                    "Recreate it with an explicit restart policy if automatic recovery is required.",
                ))
        if host.get("Privileged") is True:
            findings.append(Finding(
                "CONTAINER002", "critical", name, "Privileged container",
                "Docker reports this container is running in privileged mode.",
                "Recreate it without privileged mode and grant only required capabilities.",
            ))
        if host.get("NetworkMode") == "host":
            findings.append(Finding(
                "CONTAINER003", "warning", name, "Host networking enabled",
                "The container shares the host network namespace.",
                "Use an isolated Docker network unless host networking is essential.",
            ))
    return findings
