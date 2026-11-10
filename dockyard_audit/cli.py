"""Command-line interface for Dockyard Audit."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.theme import Theme

from dockyard_audit import __version__
from dockyard_audit.auditor import DockerAuditError, audit_docker
from dockyard_audit.checks.compose import audit_compose
from dockyard_audit.config import ComposeConfigError, load_compose
from dockyard_audit.models import SEVERITY_ORDER, Finding, sort_findings
from dockyard_audit.reporters.json_report import render_json
from dockyard_audit.reporters.terminal import render_terminal

app = typer.Typer(
    name="dockyard",
    help="Read-only audits for Docker Engine resources and Compose files.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console(stderr=True)


class OutputFormat(str, Enum):
    terminal = "terminal"
    json = "json"


class FailThreshold(str, Enum):
    critical = "critical"
    warning = "warning"
    info = "info"
    never = "never"


def _emit(findings: list[Finding], output_format: OutputFormat, output: Path | None) -> None:
    if output_format == OutputFormat.json:
        content = render_json(findings)
        if output:
            output.write_text(content + "\n", encoding="utf-8")
            console.print(f"JSON report written to {output}")
        else:
            typer.echo(content)
    else:
        if output:
            raise typer.BadParameter("--output is supported only with --format json.")
        render_terminal(findings, console)


def _exit_for_findings(findings: list[Finding], threshold: FailThreshold) -> None:
    if threshold == FailThreshold.never:
        raise typer.Exit(0)
    threshold_rank = SEVERITY_ORDER[threshold.value]
    should_fail = any(SEVERITY_ORDER[item.severity] <= threshold_rank for item in findings)
    raise typer.Exit(1 if should_fail else 0)


@app.command()
def compose(
    file: Annotated[Path, typer.Argument(help="Path to a Docker Compose YAML file.")],
    output_format: Annotated[OutputFormat, typer.Option("--format", help="Output format.")] = OutputFormat.terminal,
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Write JSON to a file.")] = None,
    fail_on: Annotated[FailThreshold, typer.Option("--fail-on", help="Fail at this severity threshold.")] = FailThreshold.never,
) -> None:
    """Audit a Compose file without connecting to Docker."""
    try:
        findings = sort_findings(audit_compose(load_compose(file)))
        _emit(findings, output_format, output)
        _exit_for_findings(findings, fail_on)
    except ComposeConfigError as exc:
        console.print(f"[red]Compose error:[/red] {exc}")
        raise typer.Exit(2) from exc
    except OSError as exc:
        console.print(f"[red]Output error:[/red] {exc}")
        raise typer.Exit(2) from exc


@app.command()
def docker(
    output_format: Annotated[OutputFormat, typer.Option("--format", help="Output format.")] = OutputFormat.terminal,
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Write JSON to a file.")] = None,
    fail_on: Annotated[FailThreshold, typer.Option("--fail-on", help="Fail at this severity threshold.")] = FailThreshold.never,
) -> None:
    """Audit containers, images, and volumes on the configured Docker Engine."""
    try:
        findings = audit_docker()
        _emit(findings, output_format, output)
        _exit_for_findings(findings, fail_on)
    except DockerAuditError as exc:
        console.print(f"[red]Docker error:[/red] {exc}")
        raise typer.Exit(2) from exc
    except OSError as exc:
        console.print(f"[red]Output error:[/red] {exc}", stderr=True)
        raise typer.Exit(2) from exc


@app.command()
def audit(
    compose_file: Annotated[Path | None, typer.Option("--compose", help="Compose file to inspect.")] = None,
    include_docker: Annotated[bool, typer.Option("--docker", help="Also inspect live Docker resources.")] = False,
    output_format: Annotated[OutputFormat, typer.Option("--format", help="Output format.")] = OutputFormat.terminal,
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Write JSON to a file.")] = None,
    fail_on: Annotated[FailThreshold, typer.Option("--fail-on", help="Fail at this severity threshold.")] = FailThreshold.never,
) -> None:
    """Audit one or both sources in a single report."""
    if compose_file is None and not include_docker:
        console.print("Select at least one source using --compose or --docker.", style="red")
        raise typer.Exit(2)
    findings: list[Finding] = []
    try:
        if compose_file is not None:
            findings.extend(audit_compose(load_compose(compose_file)))
        if include_docker:
            findings.extend(audit_docker())
        findings = sort_findings(findings)
        _emit(findings, output_format, output)
        _exit_for_findings(findings, fail_on)
    except (ComposeConfigError, DockerAuditError) as exc:
        console.print(f"[red]Audit error:[/red] {exc}")
        raise typer.Exit(2) from exc
    except OSError as exc:
        console.print(f"[red]Output error:[/red] {exc}", stderr=True)
        raise typer.Exit(2) from exc


@app.command()
def version() -> None:
    """Print the installed Dockyard Audit version."""
    typer.echo(f"dockyard-audit {__version__}")


if __name__ == "__main__":
    app()
