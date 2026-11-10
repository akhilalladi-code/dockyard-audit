import json

from dockyard_audit.models import Finding
from dockyard_audit.reporters.json_report import render_json


def test_json_report_summary():
    findings = [Finding("COMPOSE003", "critical", "api", "Privileged", "Details", "Fix it")]
    payload = json.loads(render_json(findings))
    assert payload["summary"] == {"total": 1, "critical": 1, "warning": 0, "info": 0}
    assert payload["findings"][0]["rule_id"] == "COMPOSE003"
