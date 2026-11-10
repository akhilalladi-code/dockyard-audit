"""Checks for live Docker images."""

from __future__ import annotations

from typing import Any

from dockyard_audit.models import Finding


def audit_images(images: list[Any]) -> list[Finding]:
    """Flag images carrying a latest tag."""
    findings: list[Finding] = []
    seen: set[str] = set()
    for image in images:
        attrs = getattr(image, "attrs", {}) or {}
        for tag in attrs.get("RepoTags") or []:
            if not isinstance(tag, str) or tag == "<none>:<none>" or tag in seen:
                continue
            seen.add(tag)
            if tag.endswith(":latest"):
                findings.append(Finding(
                    "IMAGE001", "info", tag, "Image uses latest tag",
                    f"Image {tag} can resolve to different content over time.",
                    "Pin a version tag or immutable digest for reproducible deployments.",
                ))
    return findings
