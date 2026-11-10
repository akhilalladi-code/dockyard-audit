# Audit rules

Dockyard Audit reports conservative configuration signals. Severity helps prioritize review; it is not a complete risk assessment.

## Compose rules

- **COMPOSE001 — restart policy (warning):** service has no explicit restart policy.
- **COMPOSE002 — user (warning):** service does not set a non-root user.
- **COMPOSE003 — privileged (critical):** service enables privileged container access.
- **COMPOSE004 — host network (warning):** service uses the host network namespace.
- **COMPOSE005 — Docker socket (warning):** service bind-mounts the Docker socket.
- **COMPOSE006 — mutable image (warning):** image is untagged or uses the latest tag.
- **COMPOSE007 — healthcheck (info):** no Compose healthcheck is defined.
- **COMPOSE008 — added capabilities (warning):** service adds Linux capabilities.

## Live Docker rules

- **CONTAINER001 — restart policy (warning):** running container has no restart policy.
- **CONTAINER002 — privileged (critical):** Docker reports privileged mode enabled.
- **CONTAINER003 — host networking (warning):** container uses host networking.
- **IMAGE001 — latest tag (info):** image metadata indicates a latest tag.
- **VOLUME001 — unattached volume (info):** no inspected container reports the volume mounted.

## Limitations

Dockyard does not inspect processes, network reachability, image vulnerabilities, secret values, host kernel settings, or full workload security posture. No findings is not a security certification.
