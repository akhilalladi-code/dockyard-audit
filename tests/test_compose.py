from dockyard_audit.checks.compose import audit_compose


def test_compose_reports_privileged_and_host_network():
    findings = audit_compose({"services": {"api": {"image": "example/api:latest", "privileged": True, "network_mode": "host"}}})
    rules = {item.rule_id for item in findings}
    assert {"COMPOSE001", "COMPOSE002", "COMPOSE003", "COMPOSE004", "COMPOSE006", "COMPOSE007"} <= rules


def test_compose_accepts_pinned_non_root_service():
    findings = audit_compose({"services": {"api": {"image": "example/api:1.2.3", "user": "10001", "restart": "unless-stopped", "healthcheck": {"test": ["CMD", "true"]}}}})
    assert findings == []


def test_compose_detects_docker_socket_mounts():
    findings = audit_compose({"services": {"short": {"volumes": ["/var/run/docker.sock:/var/run/docker.sock"]}, "long": {"volumes": [{"type": "bind", "source": "/run/docker.sock", "target": "/sock"}]}}})
    assert {item.resource for item in findings if item.rule_id == "COMPOSE005"} == {"short", "long"}


def test_image_latest_and_untagged_detection():
    findings = audit_compose({"services": {"a": {"image": "registry.example:5000/api"}, "b": {"image": "nginx:latest"}}})
    assert {item.resource for item in findings if item.rule_id == "COMPOSE006"} == {"a", "b"}


def test_digest_and_interpolated_images_not_flagged():
    findings = audit_compose({"services": {"a": {"image": "nginx:latest@sha256:abcd"}, "b": {"image": "${IMAGE_REF}"}}})
    assert not any(item.rule_id == "COMPOSE006" for item in findings)
