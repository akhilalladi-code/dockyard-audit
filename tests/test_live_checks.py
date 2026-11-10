from types import SimpleNamespace
from dockyard_audit.checks.containers import audit_containers
from dockyard_audit.checks.images import audit_images
from dockyard_audit.checks.volumes import audit_volumes

def test_container_checks():
    container = SimpleNamespace(name="api", attrs={"Name": "/api", "State": {"Status": "running"}, "HostConfig": {"RestartPolicy": {"Name": "no"}, "Privileged": True, "NetworkMode": "host"}})
    assert {f.rule_id for f in audit_containers([container])} == {"CONTAINER001", "CONTAINER002", "CONTAINER003"}

def test_image_latest_tag():
    image = SimpleNamespace(short_id="sha256:1234567890abcdef", attrs={"RepoTags": ["nginx:latest"]})
    findings = audit_images([image])
    assert len(findings) == 1 and findings[0].rule_id == "IMAGE001"

def test_volume_without_mount_is_reported():
    volume = SimpleNamespace(name="old-data", attrs={"Name": "old-data"})
    findings = audit_volumes([volume], [])
    assert len(findings) == 1 and findings[0].rule_id == "VOLUME001"
