"""PromptLint reporter module.

Provides beautiful terminal output using Rich and clean JSON for CI/CD.
The terminal reporter and JSON reporter are completely separate paths —
JSON mode never mixes terminal text.
"""

from __future__ import annotations

import json

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from promptlint import __version__
from promptlint.models import AnalysisReport, PromptStatistics, RuleResult, Severity


def _severity_style(severity: Severity) -> tuple[str, str]:
    """Return (Rich style, icon) for a severity level."""
    match severity:
        case Severity.INFO:
            return "dim blue", "ℹ"
        case Severity.WARNING:
            return "yellow", "⚠"
        case Severity.ERROR:
            return "red", "✕"
        case Severity.CRITICAL:
            return "bold red", "✕"


def _score_color(score: int) -> str:
    """Return a Rich color string based on the score value."""
    if score >= 90:
        return "green"
    if score >= 60:
        return "yellow"
    return "red"


def print_analysis_report(report: AnalysisReport, console: Console | None = None) -> None:
    """Print the full analysis report with scores, diagnostics, and summary."""
    console = console or Console()

    # Header
    console.print()
    console.print(f" [bold]PromptLint {__version__}[/bold]")
    console.print()
    console.rule(style="dim")
    console.print()

    # Quality Score
    sc = _score_color(report.score)
    console.print(f" [bold]QUALITY SCORE[/bold]{'':>20}[bold {sc}]{report.score}/100[/bold {sc}]"
                  f"  [dim]({report.rating})[/dim]")
    console.print()

    # Category scores
    for cat in report.category_scores:
        cc = _score_color(cat.score)
        console.print(f" {cat.name:<32}[{cc}]{cat.score}[/{cc}]")

    console.print()
    console.rule(style="dim")
    console.print()

    # Diagnostics
    if report.results:
        for result in report.results:
            _print_result(result, console)
            console.print()

        console.rule(style="dim")
        console.print()
        count = report.issue_count
        console.print(f" [dim]{count} issue{'s' if count != 1 else ''} found[/dim]")
    else:
        console.print(" [green]No issues found![/green]")

    console.print()


def _print_result(result: RuleResult, console: Console) -> None:
    """Print a single diagnostic result."""
    style, icon = _severity_style(result.severity)
    line_info = f" (line {result.line})" if result.line else ""

    header = Text()
    header.append(f" {icon} ", style=style)
    header.append(f"{result.rule_id:<10} ", style=f"bold {style}")
    header.append(result.message)
    if line_info:
        header.append(line_info, style="dim")
    console.print(header)

    if result.suggestion:
        console.print(f"   [dim]{result.suggestion}[/dim]")


def print_score_report(report: AnalysisReport, console: Console | None = None) -> None:
    """Print a compact score-only report."""
    console = console or Console()
    sc = _score_color(report.score)

    panel = Panel(
        Text(f"{report.score}/100  ({report.rating})", style=f"bold {sc}", justify="center"),
        title=f"[bold]PromptLint {__version__}[/bold]",
        subtitle="PromptLint Quality Score",
        border_style=sc,
        box=box.ROUNDED,
    )
    console.print(panel)


def print_security_report(report: AnalysisReport, console: Console | None = None) -> None:
    """Print security-specific findings."""
    console = console or Console()
    security_results = [r for r in report.results if r.category == "security"]

    console.print()
    console.print(f" [bold]PromptLint {__version__}[/bold] — Security Scan")
    console.print()

    if not security_results:
        console.print(
            Panel(
                "[green]No security issues detected.[/green]",
                border_style="green",
                title="Security",
            )
        )
        return

    table = Table(title="Security Findings", box=box.SIMPLE_HEAVY)
    table.add_column("Severity", style="bold", width=10)
    table.add_column("Rule", width=8)
    table.add_column("Message")

    for r in security_results:
        style, icon = _severity_style(r.severity)
        table.add_row(
            Text(f"{icon} {r.severity.value}", style=style),
            r.rule_id,
            r.message,
        )

    console.print(table)
    console.print()


def print_token_report(statistics: PromptStatistics, console: Console | None = None) -> None:
    """Print prompt size and token statistics."""
    console = console or Console()

    table = Table(title="Prompt Statistics", box=box.ROUNDED)
    table.add_column("Metric", style="bold cyan")
    table.add_column("Value", justify="right")

    table.add_row("Characters", f"{statistics.character_count:,}")
    table.add_row("Words", f"{statistics.word_count:,}")
    table.add_row("Lines", f"{statistics.line_count:,}")
    table.add_row("Estimated Tokens", f"{statistics.estimated_tokens:,}")

    console.print(table)
    console.print(" [dim]Token estimate uses ~1.3 tokens/word heuristic.[/dim]")
    console.print()


def print_diff_report(
    old_report: AnalysisReport,
    new_report: AnalysisReport,
    old_name: str,
    new_name: str,
    console: Console | None = None,
) -> None:
    """Print a comparison between two prompt analysis reports."""
    console = console or Console()

    console.print()
    console.print(f" [bold]PromptLint {__version__}[/bold] — Prompt Diff")
    console.print()

    # Score comparison
    delta = new_report.score - old_report.score
    delta_str = f"+{delta}" if delta > 0 else str(delta)
    delta_color = "green" if delta > 0 else ("red" if delta < 0 else "dim")

    table = Table(title="Prompt Quality Comparison", box=box.ROUNDED)
    table.add_column("", style="bold")
    table.add_column(old_name, justify="right")
    table.add_column(new_name, justify="right")
    table.add_column("Delta", justify="right")

    table.add_row(
        "Quality Score",
        Text(f"{old_report.score}/100", style=_score_color(old_report.score)),
        Text(f"{new_report.score}/100", style=_score_color(new_report.score)),
        Text(delta_str, style=f"bold {delta_color}"),
    )

    # Category comparison
    old_cats = {c.name: c.score for c in old_report.category_scores}
    new_cats = {c.name: c.score for c in new_report.category_scores}

    for name in old_cats:
        old_s = old_cats.get(name, 100)
        new_s = new_cats.get(name, 100)
        d = new_s - old_s
        d_str = f"+{d}" if d > 0 else str(d)
        d_color = "green" if d > 0 else ("red" if d < 0 else "dim")
        table.add_row(
            name,
            str(old_s),
            str(new_s),
            Text(d_str, style=d_color),
        )

    # Issue count
    old_issues = old_report.issue_count
    new_issues = new_report.issue_count
    issue_delta = new_issues - old_issues
    id_str = f"+{issue_delta}" if issue_delta > 0 else str(issue_delta)
    id_color = "red" if issue_delta > 0 else ("green" if issue_delta < 0 else "dim")
    table.add_row(
        "Issues",
        str(old_issues),
        str(new_issues),
        Text(id_str, style=id_color),
    )

    console.print(table)
    console.print()

    # Improvement summary
    if delta > 0:
        console.print(f" [bold green]↑ {delta_str} improvement[/bold green]")
    elif delta < 0:
        console.print(f" [bold red]↓ {delta_str} regression[/bold red]")
    else:
        console.print(" [dim]No change in overall score.[/dim]")
    console.print()


def report_to_json(report: AnalysisReport) -> str:
    """Convert report to a valid JSON string. Never mixes terminal text."""
    return json.dumps(report.model_dump(mode="json"), indent=2)
