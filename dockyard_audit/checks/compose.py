"""Static checks for Docker Compose services."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from dockyard_audit.models import Finding


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _image_is_mutable(image: Any) -> bool:
    if not isinstance(image, str) or not image.strip():
        return False
    value = image.strip()
    if "${" in value or "@" in value:
        return False
    last_segment = value.rsplit("/", 1)[-1]
    if ":" not in last_segment:
        return True
    return last_segment.rsplit(":", 1)[-1].lower() == "latest"


def _mount_is_docker_socket(mount: Any) -> bool:
    if isinstance(mount, str):
        source = mount.split(":", 1)[0]
    elif isinstance(mount, Mapping):
        source = str(mount.get("source", ""))
    else:
        return False
    normalized = source.replace("\\", "/").lower()
    return normalized in {"/var/run/docker.sock", "/run/docker.sock"} or bool(
        re.search(r"(^|/)docker\.sock$", normalized)
    )


def audit_compose(document: dict[str, Any]) -> list[Finding]:
    """Return findings for all services in a validated Compose document."""
    findings: list[Finding] = []
    for service_name, raw_service in document["services"].items():
        service = raw_service if isinstance(raw_service, Mapping) else {}
        resource = str(service_name)
        if not service.get("restart"):
            findings.append(Finding(
                "COMPOSE001", "warning", resource, "No restart policy configured",
                "The service does not define a restart policy.",
                "Set an explicit restart policy appropriate for the workload.",
            ))
        user = str(service.get("user", "")).strip()
        if not user or user in {"0", "root", "0:0", "root:root"}:
            findings.append(Finding(
                "COMPOSE002", "warning", resource, "Service may run as root",
                "No non-root user is explicitly configured for this service.",
                "Set user to a dedicated unprivileged UID/GID where supported.",
            ))
        if service.get("privileged") is True:
            findings.append(Finding(
                "COMPOSE003", "critical", resource, "Privileged mode enabled",
                "The service is configured with privileged container access.",
                "Remove privileged: true and grant only the capabilities required.",
            ))
        if str(service.get("network_mode", "")).lower() == "host":
            findings.append(Finding(
                "COMPOSE004", "warning", resource, "Host networking enabled",
                "The service shares the host network namespace.",
                "Use a dedicated Compose network unless host networking is essential.",
            ))
        if any(_mount_is_docker_socket(mount) for mount in _as_list(service.get("volumes"))):
            findings.append(Finding(
                "COMPOSE005", "warning", resource, "Docker socket is mounted",
                "The service can access the host Docker socket through a bind mount.",
                "Remove the socket mount or use a narrowly scoped alternative.",
            ))
        if _image_is_mutable(service.get("image")):
            findings.append(Finding(
                "COMPOSE006", "warning", resource, "Image reference may be mutable",
                "The service uses an untagged image or the latest tag.",
                "Pin an explicit version tag or immutable image digest.",
            ))
        if not service.get("healthcheck"):
            findings.append(Finding(
                "COMPOSE007", "info", resource, "No healthcheck configured",
                "Compose does not define a healthcheck for this service.",
                "Add a healthcheck that verifies application readiness.",
            ))
        capabilities = _as_list(service.get("cap_add"))
        if capabilities:
            findings.append(Finding(
                "COMPOSE008", "warning", resource, "Additional capabilities configured",
                f"The service adds capabilities: {', '.join(map(str, capabilities))}.",
                "Review each added capability and remove anything not strictly required.",
            ))
    return findings
