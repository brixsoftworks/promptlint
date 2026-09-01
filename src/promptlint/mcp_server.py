"""Model Context Protocol (MCP) Server for PromptLint.

Allows AI agents (like Claude Code, Antigravity, and Cursor) to use
PromptLint natively as a tool.
"""

from __future__ import annotations

try:
    from mcp.server.fastmcp import FastMCP

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


def start_mcp_server() -> None:
    """Start the MCP Server over stdio."""
    if not MCP_AVAILABLE:
        print("Error: MCP is not installed.")
        print("Install with: pip install promptlint[mcp]")
        return

    from promptlint.analyzer import analyze_prompt
    from promptlint.fixer import fix_prompt
    from promptlint.parser import parse_prompt

    try:
        from promptlint.fixer_ai import fix_prompt_magic

        MAGIC_AVAILABLE = True
    except ImportError:
        MAGIC_AVAILABLE = False

    # Create the FastMCP server
    mcp = FastMCP("PromptLint")

    @mcp.tool()
    def lint_prompt(prompt_text: str, use_ai: bool = False) -> str:
        """Lint an AI prompt and return quality issues and a score.

        Args:
            prompt_text: The raw prompt text to analyze.
            use_ai: Whether to use an LLM for deeper semantic analysis (slower but finds logical flaws).

        Returns:
            A formatted markdown string containing the score, rating, and all identified issues.
        """
        doc = parse_prompt(prompt_text)
        report = analyze_prompt(doc, use_ai=use_ai)

        if report.issue_count == 0:
            return "✅ Perfect prompt! Score: 100/100 (Excellent)\nNo issues found."

        output = [f"Score: {report.score}/100 ({report.rating.value})\n"]
        output.append("Issues Found:")

        for i, res in enumerate(report.results, 1):
            severity = res.severity.name
            output.append(f"{i}. [{severity}] {res.message}")
            if res.suggestion:
                output.append(f"   Suggestion: {res.suggestion}")

        return "\n".join(output)

    @mcp.tool()
    def auto_fix_prompt(prompt_text: str, magic: bool = False) -> str:
        """Automatically fix and format a prompt.

        Args:
            prompt_text: The poorly written prompt.
            magic: If true, completely rewrites the prompt using AI (requires LLM configuration). Otherwise, applies fast deterministic fixes.

        Returns:
            The improved prompt text.
        """
        if magic and MAGIC_AVAILABLE:
            return fix_prompt_magic(prompt_text)
        return fix_prompt(prompt_text)

    # Run the server
    mcp.run()
