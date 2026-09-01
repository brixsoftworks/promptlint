"""PromptLint CLI.

The user-facing command-line interface. Built with Typer for clean argument
parsing and Rich for beautiful terminal output. This module contains no
analysis logic — it delegates to the application functions.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from promptlint import __version__

app = typer.Typer(
    name="promptlint",
    help="The developer toolkit for AI prompts. Write prompts. Lint them. Test them. Ship them.",
    add_completion=True,
    no_args_is_help=False,
)

console = Console()
err_console = Console(stderr=True)


def _read_prompt(file: str | None = None) -> str:
    """Read prompt text from a file path, stdin ('-'), or interactively."""
    if file == "-":
        if sys.stdin.isatty():
            err_console.print("[yellow]Reading from stdin (Ctrl+D to end)...[/yellow]")
        return sys.stdin.read()

    if file is not None:
        path = Path(file)
        if not path.exists():
            err_console.print(f"[red]Error:[/red] File not found: {file}")
            raise typer.Exit(1)
        if not path.is_file():
            err_console.print(f"[red]Error:[/red] Not a file: {file}")
            raise typer.Exit(1)
        try:
            return path.read_text(encoding="utf-8")
        except Exception as e:
            err_console.print(f"[red]Error:[/red] Could not read file: {e}")
            raise typer.Exit(1)

    # If file argument was omitted:
    # 1. Non-interactive stdin pipe (e.g. `cat prompt.txt | promptlint score`)
    if not sys.stdin.isatty():
        return sys.stdin.read()

    # 2. Interactive Terminal helper
    cwd = Path.cwd()
    candidates = list(cwd.glob("*.txt")) + list(cwd.glob("*.md")) + list(cwd.glob("examples/*.txt"))

    if candidates:
        console.print("[bold cyan]PromptLint Interactive File Picker[/bold cyan]")
        console.print("No file specified. Found potential prompt files in current directory:")
        for idx, cand in enumerate(candidates[:5], 1):
            console.print(f"  [bold green][{idx}][/bold green] {cand.relative_to(cwd)}")
        console.print("  [bold green][0][/bold green] Type / Paste prompt manually")

        try:
            choice = typer.prompt("\nSelect an option", default="1")
            if choice.isdigit() and 1 <= int(choice) <= len(candidates[:5]):
                selected = candidates[int(choice) - 1]
                console.print(f"[dim]Reading {selected}...[/dim]\n")
                return selected.read_text(encoding="utf-8")
        except Exception:
            pass

    console.print("[bold cyan]Type or paste your prompt below[/bold cyan] (press Enter twice or Ctrl+D to submit):\n")
    lines = []
    try:
        while True:
            line = input()
            if not line and lines and not lines[-1]:
                break
            lines.append(line)
    except (EOFError, KeyboardInterrupt):
        pass

    text = "\n".join(lines).strip()
    if not text:
        err_console.print("[red]Error:[/red] Empty prompt provided.")
        raise typer.Exit(1)
    return text


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"PromptLint {__version__}")
        raise typer.Exit()


def _run_interactive_wizard() -> None:
    """Launch interactive wizard when promptlint is run with no arguments."""
    console.print("\n⚡ [bold font-heading text-white]Welcome to PromptLint![/bold font-heading]")
    console.print("[dim]The developer toolkit for testing, analyzing, and optimizing AI prompts.[/dim]\n")

    console.print("[bold]Select an action:[/bold]")
    console.print("  [bold green][1][/bold green] 📊 Analyze & Score a Prompt")
    console.print("  [bold green][2][/bold green] 🛡️ Run Security Scan (Secrets & Injections)")
    console.print("  [bold green][3][/bold green] ⚡ Auto-Fix a Prompt")
    console.print("  [bold green][4][/bold green] 🤖 Start MCP Server (For Claude Code / Antigravity)")
    console.print("  [bold green][5][/bold green] 🔌 Start Language Server (LSP)")
    console.print("  [bold green][0][/bold green] Exit\n")

    try:
        choice = typer.prompt("Choice", default="1")
        if choice == "1":
            text = _read_prompt(None)
            from promptlint.analyzer import analyze_prompt
            from promptlint.parser import parse_prompt
            from promptlint.reporter import print_analysis_report

            doc = parse_prompt(text)
            report = analyze_prompt(doc)
            print_analysis_report(report, console)
        elif choice == "2":
            text = _read_prompt(None)
            from promptlint.analyzer import analyze_prompt
            from promptlint.parser import parse_prompt
            from promptlint.reporter import print_security_report

            doc = parse_prompt(text)
            report = analyze_prompt(doc)
            print_security_report(report, console)
        elif choice == "3":
            text = _read_prompt(None)
            from promptlint.fixer import fix_prompt

            fixed = fix_prompt(text)
            console.print("\n[bold green]--- Improved Prompt ---[/bold green]\n")
            console.print(fixed, highlight=False)
        elif choice == "4":
            from promptlint.mcp_server import start_mcp_server

            start_mcp_server()
        elif choice == "5":
            from promptlint.lsp import start_language_server

            start_language_server()
        else:
            console.print("[dim]Goodbye![/dim]")
    except (KeyboardInterrupt, typer.Abort):
        console.print("\n[dim]Cancelled.[/dim]")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-V",
            help="Show version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """PromptLint — The developer toolkit for AI prompts."""
    if ctx.invoked_subcommand is None:
        if sys.stdin.isatty():
            _run_interactive_wizard()
        else:
            # If piped into root command, run analyze automatically
            text = sys.stdin.read()
            if text.strip():
                from promptlint.analyzer import analyze_prompt
                from promptlint.parser import parse_prompt
                from promptlint.reporter import print_analysis_report

                doc = parse_prompt(text)
                report = analyze_prompt(doc)
                print_analysis_report(report, console)


@app.command()
def analyze(
    file: Annotated[
        str | None, typer.Argument(help="Prompt file or Python file to analyze (omit or use '-' for stdin)")
    ] = None,
    json_output: Annotated[bool, typer.Option("--json", "-j", help="Output as JSON")] = False,
    quiet: Annotated[bool, typer.Option("--quiet", "-q", help="Only show score")] = False,
    ai: Annotated[bool, typer.Option("--ai", help="Use LLM for semantic analysis (requires LiteLLM)")] = False,
) -> None:
    """Analyze a prompt and report quality issues."""
    from promptlint.analyzer import analyze_prompt
    from promptlint.parser import parse_prompt
    from promptlint.reporter import print_analysis_report, print_score_report, report_to_json

    text = _read_prompt(file)

    # Check if this is a Python file
    if file and file.endswith(".py") and file != "-":
        from promptlint.extractor import extract_prompts_from_python

        prompts = extract_prompts_from_python(text)
        if not prompts:
            console.print(f"[yellow]No prompts found in {file}.[/yellow]")
            return

        console.print(f"[bold blue]Found {len(prompts)} prompt(s) in {file}[/bold blue]\n")
        has_issues = False
        for i, extracted in enumerate(prompts, 1):
            doc = parse_prompt(extracted.text)
            report = analyze_prompt(doc, use_ai=ai)
            console.print(
                f"[bold]Prompt {i} (line {extracted.line_number})[/bold] - Context: [dim]{extracted.context_name}[/dim]"
            )
            print_score_report(report, console)
            if report.issue_count > 0:
                has_issues = True
            console.print("-" * 40)

        if has_issues:
            raise typer.Exit(1)
        return

    doc = parse_prompt(text)
    report = analyze_prompt(doc, use_ai=ai)

    if json_output:
        sys.stdout.write(report_to_json(report) + "\n")
    elif quiet:
        print_score_report(report, console)
    else:
        print_analysis_report(report, console)

    if report.has_critical:
        raise typer.Exit(2)
    if report.issue_count > 0:
        raise typer.Exit(1)


@app.command()
def score(
    file: Annotated[str | None, typer.Argument(help="Prompt file to score (omit to select interactively)")] = None,
    json_output: Annotated[bool, typer.Option("--json", "-j", help="Output as JSON")] = False,
) -> None:
    """Show only the quality score for a prompt."""
    from promptlint.analyzer import analyze_prompt
    from promptlint.parser import parse_prompt
    from promptlint.reporter import print_score_report

    text = _read_prompt(file)
    doc = parse_prompt(text)
    report = analyze_prompt(doc)

    if json_output:
        import json

        data = {"score": report.score, "rating": report.rating}
        sys.stdout.write(json.dumps(data, indent=2) + "\n")
    else:
        print_score_report(report, console)


@app.command()
def security(
    file: Annotated[
        str | None, typer.Argument(help="Prompt file to scan for security issues (omit to select interactively)")
    ] = None,
    json_output: Annotated[bool, typer.Option("--json", "-j", help="Output as JSON")] = False,
) -> None:
    """Run a security scan on a prompt."""
    from promptlint.analyzer import analyze_prompt
    from promptlint.parser import parse_prompt
    from promptlint.reporter import print_security_report

    text = _read_prompt(file)
    doc = parse_prompt(text)
    report = analyze_prompt(doc)

    if json_output:
        import json

        security_data = {
            "security_status": report.security_status.model_dump(),
            "findings": [r.model_dump(mode="json") for r in report.results if r.category == "security"],
        }
        sys.stdout.write(json.dumps(security_data, indent=2) + "\n")
    else:
        print_security_report(report, console)

    if report.security_status.has_secrets:
        raise typer.Exit(2)


@app.command()
def tokens(
    file: Annotated[
        str | None, typer.Argument(help="Prompt file to analyze token usage (omit to select interactively)")
    ] = None,
    json_output: Annotated[bool, typer.Option("--json", "-j", help="Output as JSON")] = False,
) -> None:
    """Show token count and size statistics for a prompt."""
    from promptlint.parser import parse_prompt
    from promptlint.reporter import print_token_report
    from promptlint.scoring import calculate_score

    text = _read_prompt(file)
    doc = parse_prompt(text)
    _, _, _, statistics = calculate_score([], doc)

    if json_output:
        import json

        sys.stdout.write(json.dumps(statistics.model_dump(), indent=2) + "\n")
    else:
        print_token_report(statistics, console)


@app.command()
def fix(
    file: Annotated[str | None, typer.Argument(help="Prompt file to fix (omit to select interactively)")] = None,
    output: Annotated[
        str | None,
        typer.Option("--output", "-o", help="Write fixed prompt to this file"),
    ] = None,
    magic: Annotated[bool, typer.Option("--magic", help="Rewrite using AI (requires LiteLLM)")] = False,
) -> None:
    """Apply deterministic improvements to a prompt."""
    from promptlint.fixer import fix_prompt

    text = _read_prompt(file)

    if magic:
        from promptlint.fixer_ai import fix_prompt_magic

        try:
            fixed = fix_prompt_magic(text)
        except Exception as e:
            err_console.print(f"[red]Error with magic fix:[/red] {e}")
            raise typer.Exit(1)
    else:
        from promptlint.fixer import fix_prompt

        fixed = fix_prompt(text)

    if output:
        Path(output).write_text(fixed, encoding="utf-8")
        console.print(f"[green]Fixed prompt written to:[/green] {output}")
    else:
        console.print(fixed, highlight=False)


@app.command()
def diff(
    old_file: Annotated[str, typer.Argument(help="Original prompt file")],
    new_file: Annotated[str, typer.Argument(help="Updated prompt file")],
    json_output: Annotated[bool, typer.Option("--json", "-j", help="Output as JSON")] = False,
) -> None:
    """Compare two prompts and show quality changes."""
    from promptlint.diff import diff_prompts
    from promptlint.reporter import print_diff_report

    old_text = _read_prompt(old_file)
    new_text = _read_prompt(new_file)

    old_name = Path(old_file).name if old_file != "-" else "old"
    new_name = Path(new_file).name if new_file != "-" else "new"

    result = diff_prompts(old_text, new_text, old_name, new_name)

    if json_output:
        import json

        data = {
            "old": {
                "name": old_name,
                "score": result.old_report.score,
                "rating": result.old_report.rating,
            },
            "new": {
                "name": new_name,
                "score": result.new_report.score,
                "rating": result.new_report.rating,
            },
            "delta": result.score_delta,
        }
        sys.stdout.write(json.dumps(data, indent=2) + "\n")
    else:
        print_diff_report(result.old_report, result.new_report, old_name, new_name, console)


@app.command()
def test(
    file: Annotated[str, typer.Argument(help="YAML test specification file")],
) -> None:
    """Run prompt test cases (requires model adapter)."""
    from promptlint.testing import load_test_spec, run_tests

    path = Path(file)
    if not path.exists():
        err_console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    spec = load_test_spec(path)
    results = run_tests(spec)

    console.print(f"\n [bold]{spec.name}[/bold] — Prompt Test\n")

    passed = sum(1 for r in results if r.passed)
    total = len(results)

    for i, result in enumerate(results, 1):
        status = "[green]PASS[/green]" if result.passed else "[red]FAIL[/red]"
        console.print(f"  {status}  Case {i}: {result.message}")

    console.print()
    console.print(f"  Cases: {total}  Passed: {passed}  Failed: {total - passed}")

    if passed < total:
        raise typer.Exit(1)


@app.command()
def lsp() -> None:
    """Start the Language Server Protocol (LSP)."""
    from promptlint.lsp import start_language_server

    start_language_server()


@app.command()
def mcp() -> None:
    """Start the Model Context Protocol (MCP) Server."""
    from promptlint.mcp_server import start_mcp_server

    start_mcp_server()


if __name__ == "__main__":
    app()
