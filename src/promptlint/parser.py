"""Prompt parser.

Transforms raw prompt text into a PromptDocument, pre-computing properties
that downstream rules and analyzers need. The parser is intentionally simple —
it does not attempt to understand prompt semantics, only structure.
"""

from __future__ import annotations

from promptlint.models import PromptDocument


def parse_prompt(text: str) -> PromptDocument:
    """Parse raw text into a PromptDocument.

    Handles edge cases: empty strings, whitespace-only input, and very large
    prompts. The original text is preserved exactly as provided.

    Args:
        text: Raw prompt text. May come from a file, stdin, or the Python API.

    Returns:
        A PromptDocument with pre-computed metrics.
    """
    lines = text.splitlines() if text else []
    words = text.split() if text else []

    return PromptDocument(
        text=text,
        lines=lines,
        character_count=len(text),
        word_count=len(words),
        line_count=len(lines),
    )
