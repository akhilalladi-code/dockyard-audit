from pathlib import Path

from typer.testing import CliRunner

from dockyard_audit.cli import app

runner = CliRunner()


def test_compose_cli_success(tmp_path: Path):
    file = tmp_path / "compose.yml"
    file.write_text(
        "services:\n  web:\n    image: nginx:1.27\n    user: '1000'\n"
        "    restart: unless-stopped\n    healthcheck: {}\n",
        encoding="utf-8",
    )
    result = runner.invoke(app, ["compose", str(file)])
    assert result.exit_code == 0, result.output
    assert "Dockyard Audit" in result.output


def test_compose_cli_fail_on_warning(tmp_path: Path):
    file = tmp_path / "compose.yml"
    file.write_text("services:\n  web:\n    image: nginx:latest\n", encoding="utf-8")
    result = runner.invoke(app, ["compose", str(file), "--fail-on", "warning"])
    assert result.exit_code == 1


def test_compose_cli_json(tmp_path: Path):
    file = tmp_path / "compose.yml"
    file.write_text(
        "services:\n  web:\n    image: nginx:1.27\n    user: '1000'\n"
        "    restart: unless-stopped\n    healthcheck: {}\n",
        encoding="utf-8",
    )
    result = runner.invoke(app, ["compose", str(file), "--format", "json"])
    assert result.exit_code == 0
    assert '"findings": []' in result.output


def test_audit_requires_a_source():
    assert runner.invoke(app, ["audit"]).exit_code == 2


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "dockyard-audit" in result.output
