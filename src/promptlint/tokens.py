"""Token and size estimation for AI prompts.

Estimates token counts without requiring a real tokenizer library.
The estimates use a heuristic of ~1.3 tokens per word for English text.
This is documented as an approximation, not an exact count.
"""

from __future__ import annotations

import math


def estimate_tokens(text: str) -> int:
    """Estimate the number of tokens in the text.

    Uses a heuristic of ~1.3 tokens per word for English text.
    This is an approximation — exact counts require a model-specific tokenizer.
    """
    if not text or not text.strip():
        return 0
    word_count = len(text.split())
    return math.ceil(word_count * 1.3)


def get_prompt_statistics(text: str) -> dict[str, int | float]:
    """Return a dictionary of prompt size statistics.

    Returns:
        dict with keys: character_count, word_count, line_count,
        estimated_tokens, avg_word_length, avg_line_length
    """
    if not text:
        return {
            "character_count": 0,
            "word_count": 0,
            "line_count": 0,
            "estimated_tokens": 0,
            "avg_word_length": 0.0,
            "avg_line_length": 0.0,
        }

    words = text.split()
    lines = text.splitlines()

    word_count = len(words)
    line_count = len(lines)
    char_count = len(text)

    avg_word_length = sum(len(w) for w in words) / word_count if word_count else 0.0
    avg_line_length = char_count / line_count if line_count else 0.0

    return {
        "character_count": char_count,
        "word_count": word_count,
        "line_count": line_count,
        "estimated_tokens": estimate_tokens(text),
        "avg_word_length": round(avg_word_length, 1),
        "avg_line_length": round(avg_line_length, 1),
    }


def format_token_report(text: str) -> str:
    """Return a formatted string summarizing prompt statistics."""
    stats = get_prompt_statistics(text)
    lines = [
        "Prompt Statistics",
        "─" * 35,
        f"  Characters:       {stats['character_count']:>10,}",
        f"  Words:            {stats['word_count']:>10,}",
        f"  Lines:            {stats['line_count']:>10,}",
        f"  Estimated tokens: {stats['estimated_tokens']:>10,}",
        f"  Avg word length:  {stats['avg_word_length']:>10}",
        f"  Avg line length:  {stats['avg_line_length']:>10}",
        "─" * 35,
        "  Token estimate uses ~1.3 tokens/word heuristic.",
    ]
    return "\n".join(lines)
