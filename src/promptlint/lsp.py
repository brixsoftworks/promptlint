"""Language Server Protocol (LSP) for PromptLint.

Allows IDEs like VS Code, Cursor, and Neovim to provide real-time
linting and red squiggly lines for AI prompts in text files.
"""

from __future__ import annotations

import logging

try:
    from pygls.lsp.methods import TEXT_DOCUMENT_DID_CHANGE, TEXT_DOCUMENT_DID_OPEN
    from pygls.lsp.types import (
        Diagnostic,
        DiagnosticSeverity,
        DidChangeTextDocumentParams,
        DidOpenTextDocumentParams,
        Position,
        Range,
    )
    from pygls.server import LanguageServer
    PYGLS_AVAILABLE = True
except ImportError:
    PYGLS_AVAILABLE = False


def start_language_server() -> None:
    """Start the PromptLint Language Server."""
    if not PYGLS_AVAILABLE:
        print("Error: pygls is not installed.")
        print("Install with: pip install promptlint[lsp]")
        return

    from promptlint.analyzer import analyze_prompt
    from promptlint.models import Severity
    from promptlint.parser import parse_prompt

    server = LanguageServer("promptlint-ls", "v1")

    # Map PromptLint severity to LSP severity
    def _map_severity(severity: Severity) -> DiagnosticSeverity:
        if severity == Severity.INFO:
            return DiagnosticSeverity.Information
        if severity == Severity.WARNING:
            return DiagnosticSeverity.Warning
        return DiagnosticSeverity.Error

    def _validate_document(uri: str, text: str) -> None:
        """Run PromptLint on the document text and publish diagnostics."""
        doc = parse_prompt(text)
        report = analyze_prompt(doc)

        diagnostics = []
        for result in report.results:
            # LSP is 0-indexed, PromptLint is 1-indexed
            line_idx = (result.line - 1) if result.line else 0

            # Simple fallback for column range: highlight the first 10 chars if no column
            # In a real AST, we'd have exact start/end columns
            start_col = (result.column - 1) if result.column else 0
            end_col = start_col + 10

            message = f"[{result.rule_id}] {result.message}"
            if result.suggestion:
                message += f"\nSuggestion: {result.suggestion}"

            diagnostics.append(
                Diagnostic(
                    range=Range(
                        start=Position(line=line_idx, character=start_col),
                        end=Position(line=line_idx, character=end_col),
                    ),
                    message=message,
                    severity=_map_severity(result.severity),
                    source="PromptLint",
                )
            )

        server.publish_diagnostics(uri, diagnostics)

    @server.feature(TEXT_DOCUMENT_DID_OPEN)
    def did_open(ls: LanguageServer, params: DidOpenTextDocumentParams) -> None:
        """Text document did open notification."""
        doc = ls.workspace.get_document(params.text_document.uri)
        _validate_document(doc.uri, doc.source)

    @server.feature(TEXT_DOCUMENT_DID_CHANGE)
    def did_change(ls: LanguageServer, params: DidChangeTextDocumentParams) -> None:
        """Text document did change notification."""
        doc = ls.workspace.get_document(params.text_document.uri)
        _validate_document(doc.uri, doc.source)

    logging.basicConfig(level=logging.ERROR)
    server.start_io()
