"""Orchestration for read-only Docker Engine audits."""

from __future__ import annotations

from typing import Any

import docker
from docker.errors import DockerException

from dockyard_audit.checks.containers import audit_containers
from dockyard_audit.checks.images import audit_images
from dockyard_audit.checks.volumes import audit_volumes
from dockyard_audit.models import Finding, sort_findings


class DockerAuditError(RuntimeError):
    """Raised when Docker cannot be inspected."""


def audit_docker(client: Any | None = None) -> list[Finding]:
    """Inspect Docker resources using list/inspect calls only."""
    owned_client = client is None
    if owned_client:
        try:
            client = docker.from_env()
            client.ping()
        except DockerException as exc:
            raise DockerAuditError(
                "Cannot connect to Docker. Start Docker Engine or check DOCKER_HOST and permissions."
            ) from exc
    try:
        containers = client.containers.list(all=True)
        images = client.images.list()
        volumes = client.volumes.list()
        return sort_findings(
            audit_containers(containers) + audit_images(images)
            + audit_volumes(volumes, containers)
        )
    except DockerException as exc:
        raise DockerAuditError(f"Docker inspection failed: {exc}") from exc
    finally:
        if owned_client and client is not None:
            try:
                client.close()
            except Exception:
                pass
