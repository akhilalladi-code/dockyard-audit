"""Human-readable terminal report."""

from __future__ import annotations

from collections import Counter

from rich.console import Console
from rich.table import Table

from dockyard_audit.models import Finding, sort_findings

STYLES = {"critical": "bold red", "warning": "yellow", "info": "cyan"}


def render_terminal(findings: list[Finding], console: Console | None = None) -> None:
    """Render findings and remediation guidance."""
    console = console or Console()
    console.print("\n[bold]Dockyard Audit[/bold]")
    if not findings:
        console.print("[green]No findings. The inspected scope passed the configured checks.[/green]")
        return
    table = Table(show_header=True, header_style="bold")
    table.add_column("Severity", no_wrap=True)
    table.add_column("Rule", no_wrap=True)
    table.add_column("Resource")
    table.add_column("Finding")
    for item in sort_findings(findings):
        style = STYLES[item.severity]
        table.add_row(
            f"[{style}]{item.severity.upper()}[/{style}]",
            item.rule_id, item.resource, item.title,
        )
    console.print(table)
    counts = Counter(item.severity for item in findings)
    console.print(
        f"\n[bold]Summary:[/bold] {len(findings)} findings · "
        f"[red]{counts['critical']} critical[/red] · "
        f"[yellow]{counts['warning']} warning[/yellow] · "
        f"[cyan]{counts['info']} info[/cyan]"
    )
    for item in sort_findings(findings):
        console.print(f"\n[bold]{item.rule_id} — {item.resource}[/bold]")
        console.print(item.detail)
        console.print(f"[dim]Remediation: {item.remediation}[/dim]")
